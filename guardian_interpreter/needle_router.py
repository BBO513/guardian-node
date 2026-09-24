"""
Needle 3 command router for Guardian Node.

Decides, in well under a second, whether a request is a command Guardian can act on
(lights, scans, security checks, scam analysis, lessons) or something Phi-4 should
explain. Out of the box Needle 3 calls a tool for almost anything, so routing is
gated by trigger regexes (guardian_tools) and Needle is only used to fill arguments
for the tools a trigger selected:

  1. Explanation-style requests ("what is…", "why…", "explain…") -> Phi-4.
  2. Compound commands are split into clauses ("turn off X and Y", "check A then B").
  3. Each clause's triggers pick candidate tools. No candidates -> Phi-4.
  4. A single argument-free candidate is called directly; otherwise Needle runs with
     only the candidates allowed to execute.

Set open_routing=True (e.g. with a Guardian fine-tuned .cact) to let Needle route
clauses no trigger matched.
"""

import logging
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from guardian_interpreter import guardian_tools as gt

logger = logging.getLogger(__name__)

EXPLAIN_RE = re.compile(
    r"^\s*(what(\s+is|\s+are|'s|\s+does|\s+makes)\s+(?!(connected|on\b))(a|an|the)?\s*(?!devices\b)"
    r"|why\b|explain\b|how\s+(do|does|can|should|would|could|is|are)\b|tell me (about|a|an)\b"
    r"|define\b|describe\b|write\b|compose\b|sing\b|what('s| is) the (weather|time|date)\b"
    r"|can you (explain|tell me)\b|should i\b"
    r"|((can|could) you )?(recommend|suggest)\b|which\b|what('s| is) the (best|safest|worst)\b"
    # general safety questions about things that aren't *yours* ("is it ok to use hotel wifi?")
    r"|is it (safe|ok|okay|bad|dangerous|risky|wise) to\b"
    r"|(is|are) (public|hotel|free|cafe|airport|open)\s+(wifi|wi-fi|networks?|hotspots?)\b)",
    re.IGNORECASE)
# "how safe is my wifi" / "how secure are our cameras" are checks on the user's own kit, not explanations.
OWN_KIT_CHECK_RE = re.compile(
    r"^\s*how\s+(safe|secure|protected|private|locked down|strong)\s+(is|are)\s+(my|our|the)\b", re.IGNORECASE)
SPLIT_RE = re.compile(r"\s*(?:,\s*)?(?:\band then\b|\bthen\b|\band also\b|\band\b|;|,)\s*", re.IGNORECASE)
CARRY_RE = re.compile(r"\b(turn|switch|shut|put)\s+(on|off)\b|\b(turn|switch|shut|put)\s+(?:\w+\s+){1,5}(on|off)\b",
                      re.IGNORECASE)
STATUS_Q_RE = re.compile(r"^\s*(is|are|did|have|has)\b", re.IGNORECASE)
TOOL_BY_NAME = {t.__name__: t for t in gt.TOOLS}
TRIGGERS = {name: [re.compile(p, re.IGNORECASE) for p in t._needle_tool.get("triggers", [])]
            for name, t in TOOL_BY_NAME.items()}
NO_ARG_TOOLS = {name for name, t in TOOL_BY_NAME.items()
                if not t._needle_tool["parameters"].get("properties")}
# Tools whose argument is the user's own text, verbatim.
VERBATIM_ARG = {"analyze_threat": "content"}

# --- argument fixers: facts that are more reliable to read from the words than from Needle ---
WORD_NUMS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
    "sixteen seventeen eighteen".split())}
_NUM = r"(\d{1,2}|" + "|".join(WORD_NUMS) + r")"
AGE_RES = [
    re.compile(_NUM + r"[\s-]*(?:years?|yrs?)[\s-]*old\b|\b" + _NUM + r"[\s-]*(?:yo|y/o)\b", re.IGNORECASE),
    re.compile(r"\b(?:is|he's|she's|they're|aged|age|turned|turning|who's)\s+" + _NUM + r"\b", re.IGNORECASE),
]
SCHOOL_YEAR_RE = re.compile(r"\byear\s+(\d{1,2})\b", re.IGNORECASE)          # UK school year N ~ age N+5
GRADE_RE = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)\s+grade\b|\bgrade\s+(\d{1,2})\b", re.IGNORECASE)  # US ~ N+6
TEEN_WORDS_RE = re.compile(r"\b(teen|teens|teenager|teenagers|teenage|adolescent|secondary school|high school|"
                           r"gcse|sixth form|college)\b", re.IGNORECASE)
CHILD_WORDS_RE = re.compile(r"\b(little|toddler|toddlers|primary school|infant|reception|nursery|"
                            r"young (child|children|kids|son|daughter)|baby)\b", re.IGNORECASE)
PORT_RE = re.compile(r"\bports?\b", re.IGNORECASE)
FULL_SCAN_RE = re.compile(r"\b(full|complete|deep|thorough)\b|\bscan (everything|it all)\b|\bports?\s+too\b",
                          re.IGNORECASE)


def _to_int(s):
    return WORD_NUMS.get(s.lower()) if not s.isdigit() else int(s)


def detect_age_group(text: str) -> Optional[str]:
    for rx in AGE_RES:
        m = rx.search(text)
        if m:
            age = _to_int(next(g for g in m.groups() if g))
            if age is not None and 2 <= age <= 19:
                return "child" if age < 13 else "teen"
    m = SCHOOL_YEAR_RE.search(text)
    if m and 1 <= int(m.group(1)) <= 13:
        return "child" if int(m.group(1)) + 5 < 13 else "teen"
    m = GRADE_RE.search(text)
    if m:
        g = int(next(x for x in m.groups() if x))
        return "child" if g + 6 < 13 else "teen"
    if TEEN_WORDS_RE.search(text):
        return "teen"
    if CHILD_WORDS_RE.search(text):
        return "child"
    return None


DEVICE_ALIASES = {k: re.compile(v, re.IGNORECASE) for k, v in {
    "kettle": r"\bkettle\b",
    "ac": r"\b(air ?con(ditioner|ditioning)?|a/c|ac|aircon|cooling|thermostat)\b",
    "hot_water": r"\b(hot water|water heater|immersion|boiler|shower)\b",
    "lights_living": r"\b(living ?room|lounge|front room|sitting room)\b",
    "lights_bedroom": r"\bbedroom\b",
}.items()}
DEVICE_TOOLS = {"turn_on", "turn_off", "get_device_status"}
TOPIC_RES = [
    re.compile(r"\b(?:about|on|regarding)\s+(.+?)(?:\s+(?:for|with|to)\s+(?:my|our|the|a|her|his)\b.*)?[?.!]*$",
               re.IGNORECASE),
    re.compile(r"\b(?:an?|the)\s+((?:\w+\s+){0,2}\w+)\s+(?:activity|game|quiz|lesson)\b", re.IGNORECASE),
    re.compile(r"\bhow to\s+(.+?)[?.!]*$", re.IGNORECASE),
]


def detect_device(text: str) -> Optional[str]:
    found = [d for d, rx in DEVICE_ALIASES.items() if rx.search(text)]
    return found[0] if len(found) == 1 else None


def detect_topic(text: str) -> Optional[str]:
    for rx in TOPIC_RES:
        m = rx.search(text)
        if m:
            return m.group(1).strip()
    return None


def fix_args(name: str, clause: str, args: Dict[str, Any]) -> Dict[str, Any]:
    args = dict(args)
    if name == "start_child_lesson":
        group = detect_age_group(clause)
        if group:
            args["age_group"] = group
    elif name == "scan_network":
        if PORT_RE.search(clause):
            args["scan_type"] = "full" if FULL_SCAN_RE.search(clause) else "port"
        else:
            args["scan_type"] = "full" if FULL_SCAN_RE.search(clause) else "ping"
    elif name in DEVICE_TOOLS:
        device = detect_device(clause)
        if device:
            args["device"] = device
    return args


def fallback_args(name: str, clause: str) -> Optional[Dict[str, Any]]:
    """Arguments read straight from the words, for when Needle declines a triggered command."""
    if name == "start_child_lesson":
        group, topic = detect_age_group(clause), detect_topic(clause)
        return {"age_group": group, "topic": topic} if group and topic else None
    if name == "scan_network":
        return fix_args(name, clause, {})
    if name in DEVICE_TOOLS:
        device = detect_device(clause)
        return {"device": device} if device else None
    return None


TOOL_LABELS = {
    "turn_on": "Turn on", "turn_off": "Turn off", "set_temperature": "Set temperature",
    "get_device_status": "Device status", "scan_network": "Network scan", "check_router": "Router check",
    "check_wifi_security": "Wi-Fi check", "check_parental_controls": "Parental controls check",
    "check_iot_devices": "Smart device check", "analyze_threat": "Scam check", "start_child_lesson": "Lesson",
}


def describe_call(call: Dict[str, Any], spoken: bool = False) -> str:
    """A short human reply for one executed tool call."""
    label = TOOL_LABELS.get(call["name"], call["name"])
    res = call.get("result")
    if isinstance(res, dict):
        if res.get("ok") is False or res.get("success") is False:
            return f"Sorry, the {label.lower()} didn't work: {res.get('error', 'unknown error')}."
        if res.get("message"):
            return str(res["message"]).replace("Mock: ", "")
        if "state" in res:
            return f"The {call['args'].get('device', 'device')} is {res['state']}."
        if "red_flags" in res:
            flags = res["red_flags"]
            found = f" Warning signs: {', '.join(flags)}." if flags else " No obvious warning signs."
            return f"{label}: {res['status']}.{found}"
        if "status" in res:
            recs = res.get("recommendations") or []
            tip = f" Top tip: {recs[0]}" if recs else ""
            more = f" ({len(recs) - 1} more in the report.)" if len(recs) > 1 and not spoken else ""
            return f"{label}: {res['status']}.{tip}{more}"
        return f"{label}: done."
    if isinstance(res, str) and res.strip():
        if not spoken:
            return res.strip()
        lines = [ln.strip() for ln in res.strip().splitlines() if ln.strip() and not set(ln.strip()) <= set("=-*#")]
        return " ".join(lines[:3])[:300]
    return f"{label}: done."


def describe(res: "RouteResult", spoken: bool = False) -> str:
    return "\n".join(describe_call(c, spoken) for c in res.calls)


def followup_prompt(res: "RouteResult") -> Optional[str]:
    """A prompt for the LLM to explain a result in plain words, when a tool alone isn't enough.

    Scam checks need judgement a rule list can't give, so the red flags are handed to the LLM.
    """
    for c in res.calls:
        r = c.get("result")
        if c["name"] == "analyze_threat" and isinstance(r, dict) and "red_flags" in r:
            flags = ", ".join(r["red_flags"]) or "none found by the quick check"
            return (f'A family member received this message: "{r["content"]}"\n'
                    f"Quick check warning signs: {flags}.\n"
                    "Is this likely a scam? Reply in 2-4 short sentences for a family: your verdict, "
                    "the main reason, and what they should do next. Never invent website addresses, "
                    "phone numbers or organisation names; say to contact the company through its official "
                    "app or a number they already trust.")
    return None


def find_router_weights(models_dir: str) -> Optional[str]:
    """Prefer the Guardian fine-tuned model, then a local base model; None = Needle's cached base."""
    for name in ("guardian_needle.cact", "needle3.cact"):
        path = os.path.join(models_dir, name)
        if os.path.exists(path):
            return path
    return None


@dataclass
class RouteResult:
    route: str                      # "tools" or "llm"
    query: str
    calls: List[Dict[str, Any]] = field(default_factory=list)
    results: List[Any] = field(default_factory=list)
    blocked: List[Dict[str, Any]] = field(default_factory=list)
    reason: str = ""
    seconds: float = 0.0


def candidates(text: str) -> List[str]:
    found = [name for name, pats in TRIGGERS.items() if any(p.search(text) for p in pats)]
    if STATUS_Q_RE.search(text) and "get_device_status" in found:
        found = [n for n in found if n not in ("turn_on", "turn_off")]
    if "set_temperature" in found:
        found = [n for n in found if n != "turn_on"]
    return found


def split_clauses(query: str) -> List[str]:
    """Split compound commands, carrying the verb ("turn off X and Y" -> two clauses).
    Only splits when every kept clause is itself a command; otherwise the whole
    query is one clause (so "a lesson about scams and phishing" stays intact)."""
    if "analyze_threat" in candidates(query):
        return [query]
    parts = [p.strip() for p in SPLIT_RE.split(query) if p and p.strip()]
    if len(parts) < 2:
        return [query]
    clauses, carry = [], None
    for part in parts:
        m = CARRY_RE.search(part)
        if m:
            carry = f"{m.group(1) or m.group(3)} {m.group(2) or m.group(4)}"
        if not candidates(part) and carry:
            part = f"{carry} {part}"
        clauses.append(part)
    kept = [c for c in clauses if candidates(c) or len(c.split()) > 3]
    if len(kept) >= 2 and all(candidates(c) for c in kept):
        return kept
    return [query]


class NeedleRouter:
    def __init__(self, weights: Optional[str] = None, backend=None, open_routing: bool = False):
        from needle import Needle
        os.environ.setdefault("NEEDLE_TELEMETRY", "0")   # Guardian: no telemetry
        if backend is not None:
            gt.set_backend(backend)
        self.open_routing = open_routing
        t = time.time()
        self.needle = Needle(tools=gt.TOOLS, weights=weights) if weights else Needle(tools=gt.TOOLS)
        logger.info(f"Needle router loaded in {time.time() - t:.2f}s")

    def close(self):
        self.needle.close()

    def _run_clause(self, clause: str, cands: List[str]) -> List[Dict[str, Any]]:
        backend = gt.get_backend()
        if len(cands) == 1 and cands[0] in NO_ARG_TOOLS:
            result = gt._call(cands[0])
            return [{"name": cands[0], "args": {}, "result": result}]
        if len(cands) == 1 and cands[0] in VERBATIM_ARG:
            arg = VERBATIM_ARG[cands[0]]
            result = gt._call(cands[0], **{arg: clause})
            return [{"name": cands[0], "args": {arg: clause}, "result": result}]

        gt.set_allowed(cands)
        executed = []
        orig = backend.call

        def spy(name, **kwargs):
            kwargs = fix_args(name, clause, kwargs)
            # Needle sometimes repeats a call in its loop; never run the same action twice.
            for c in executed:
                if c["name"] == name and c["args"] == kwargs:
                    return c["result"]
            res = orig(name, **kwargs)
            executed.append({"name": name, "args": kwargs, "result": res})
            return res

        backend.call = spy
        try:
            self.needle.reset()
            self.needle.run(clause, max_steps=3)
        finally:
            backend.call = orig
            gt.set_allowed(None)
        if not executed and len(cands) == 1:
            args = fallback_args(cands[0], clause)
            if args is not None:
                executed.append({"name": cands[0], "args": args, "result": gt._call(cands[0], **args)})
        return executed

    def route(self, query: str) -> RouteResult:
        t = time.time()
        gt.blocked_calls.clear()
        res = RouteResult(route="llm", query=query)
        if EXPLAIN_RE.search(query) and not OWN_KIT_CHECK_RE.search(query):
            res.reason = "explanation request"
        else:
            clauses = split_clauses(query)
            plan = [(c, candidates(c)) for c in clauses]
            if not any(cands for _, cands in plan) and not self.open_routing:
                res.reason = "no command trigger matched"
            else:
                for clause, cands in plan:
                    if not cands:
                        cands = list(TOOL_BY_NAME)      # open routing
                    res.calls.extend(self._run_clause(clause, cands))
                if res.calls:
                    res.route = "tools"
                    res.reason = f"{len(res.calls)} call(s) from {len(plan)} clause(s)"
                else:
                    res.reason = "command matched but Needle made no permitted call"
        res.blocked = list(gt.blocked_calls)
        res.results = [c.get("result") for c in res.calls]
        res.seconds = time.time() - t
        return res
