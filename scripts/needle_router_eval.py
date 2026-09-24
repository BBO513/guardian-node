"""
Needle 3 router evaluation for Guardian Node.

Runs Guardian-style requests through either raw Needle 3 (all tools, no gating) or
the NeedleRouter (guardian_interpreter/needle_router.py), with tools stubbed so nothing
is actually scanned or switched. Scores tool choice + arguments, and whether
non-commands correctly fall through to Phi-4.

Case sets:
  dev      - the original 26 requests (triggers were written with these in view)
  heldout  - new phrasings written after the triggers, never tuned against
  fresh    - written before the age / Wi-Fi / scan-type fixes ran (checks they generalise)
  fresh2   - written after fixing the fresh-set failures, before re-running (the honest check)

Usage (on the Pi, inside the venv, from the repo root):
    python scripts/needle_router_eval.py --mode router --set all [--weights needle3.cact] [--json out.json]
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("NEEDLE_TELEMETRY", "0")

from guardian_interpreter import guardian_tools as gt  # noqa: E402

# (query, expected calls). Expected call = (name, {arg: value}) where value None = any.
# Empty list = no tool; should fall through to Phi-4.
DEV = [
    ("turn off the bedroom lights", [("turn_off", {"device": "lights_bedroom"})]),
    ("switch the kettle on", [("turn_on", {"device": "kettle"})]),
    ("lights on in the living room please", [("turn_on", {"device": "lights_living"})]),
    ("set the air con to 21 degrees", [("set_temperature", {"device": "ac", "temperature": 21})]),
    ("is the hot water on?", [("get_device_status", {"device": "hot_water"})]),
    ("turn off the kettle and the living room lights",
     [("turn_off", {"device": "kettle"}), ("turn_off", {"device": "lights_living"})]),
    ("it's bedtime, turn off the bedroom lights and switch off the ac",
     [("turn_off", {"device": "lights_bedroom"}), ("turn_off", {"device": "ac"})]),
    ("heat up the water for a shower", [("turn_on", {"device": "hot_water"})]),
    ("scan the network", [("scan_network", {"scan_type": None})]),
    ("what devices are connected to my wifi?", [("scan_network", {"scan_type": None})]),
    ("do a full scan of the network including open ports", [("scan_network", {"scan_type": "full"})]),
    ("check my router is secure", [("check_router", {})]),
    ("is my wifi password strong enough?", [("check_wifi_security", {})]),
    ("check the parental controls are working", [("check_parental_controls", {})]),
    ("are my smart cameras and speakers safe?", [("check_iot_devices", {})]),
    ("check the router and then scan the network",
     [("check_router", {}), ("scan_network", {"scan_type": None})]),
    ("I got a text saying my parcel is held, pay £1.99 at royal-mail-redelivery.co, is it a scam?",
     [("analyze_threat", {"content": None})]),
    ("my son got an email from paypa1.com asking him to confirm his password",
     [("analyze_threat", {"content": None})]),
    ("teach my 8 year old about strong passwords",
     [("start_child_lesson", {"age_group": "child", "topic": None})]),
    ("start a lesson for my teenager about online scams",
     [("start_child_lesson", {"age_group": "teen", "topic": None})]),
    ("what is phishing?", []),
    ("why should I use a password manager?", []),
    ("explain what a VPN does in simple terms", []),
    ("how do hackers get into home networks?", []),
    ("write me a poem about cats", []),
    ("what's the weather tomorrow?", []),
]

HELDOUT = [
    ("switch off the air conditioning", [("turn_off", {"device": "ac"})]),
    ("can you turn the kettle off", [("turn_off", {"device": "kettle"})]),
    ("bedroom lights on", [("turn_on", {"device": "lights_bedroom"})]),
    ("make it 19 degrees in here", [("set_temperature", {"device": "ac", "temperature": 19})]),
    ("did I leave the kettle on?", [("get_device_status", {"device": "kettle"})]),
    ("turn on the hot water and the kettle",
     [("turn_on", {"device": "hot_water"}), ("turn_on", {"device": "kettle"})]),
    ("who's on my wifi right now?", [("scan_network", {"scan_type": None})]),
    ("check for open ports on my network", [("scan_network", {"scan_type": "port"})]),
    ("has my router been hacked?", [("check_router", {})]),
    ("how secure is my wifi?", [("check_wifi_security", {})]),
    ("audit the screen time settings", [("check_parental_controls", {})]),
    ("is our baby monitor secure?", [("check_iot_devices", {})]),
    ("someone texted me a link bit.ly/3xYz saying I won an iphone", [("analyze_threat", {"content": None})]),
    ("is this email legit: your netflix account is suspended, click here to verify",
     [("analyze_threat", {"content": None})]),
    ("make a game for my 7 year old about stranger danger",
     [("start_child_lesson", {"age_group": "child", "topic": None})]),
    ("my daughter is 15, give her a lesson on privacy settings",
     [("start_child_lesson", {"age_group": "teen", "topic": None})]),
    ("what's the difference between WPA2 and WPA3?", []),
    ("how do I make a strong password?", []),
    ("tell me a joke", []),
    ("is it safe to use public wifi?", []),
    ("what does a firewall do?", []),
    ("should I let my kid have tiktok?", []),
    ("who invented the internet?", []),
    ("thanks guardian", []),
]


# Written after the age / Wi-Fi / scan-type fixes were planned but before they ran,
# to check those fixes generalise rather than just patch the failed sentences.
FRESH = [
    ("teach my 10 year old how to spot fake websites",
     [("start_child_lesson", {"age_group": "child", "topic": None})]),
    ("my son is 14, can you do a lesson on gaming scams",
     [("start_child_lesson", {"age_group": "teen", "topic": None})]),
    ("a quiz about passwords for my 6-year-old", [("start_child_lesson", {"age_group": "child", "topic": None})]),
    ("start a privacy activity for my twelve year old",
     [("start_child_lesson", {"age_group": "child", "topic": None})]),
    ("my teenage daughter needs a lesson on sharing photos",
     [("start_child_lesson", {"age_group": "teen", "topic": None})]),
    ("lesson on cyberbullying for a year 9 student", [("start_child_lesson", {"age_group": "teen", "topic": None})]),
    ("run a stranger danger game for my little boy", [("start_child_lesson", {"age_group": "child", "topic": None})]),
    ("my 13 year old wants to learn about social media safety",
     [("start_child_lesson", {"age_group": "teen", "topic": None})]),
    ("how safe is our wifi?", [("check_wifi_security", {})]),
    ("is my home wifi secure enough?", [("check_wifi_security", {})]),
    ("how protected is my router?", [("check_router", {})]),
    ("how secure are my smart cameras?", [("check_iot_devices", {})]),
    ("any open ports on my devices?", [("scan_network", {"scan_type": "port"})]),
    ("scan everything, ports too", [("scan_network", {"scan_type": "full"})]),
    ("quick scan to see what's on the network", [("scan_network", {"scan_type": "ping"})]),
    ("switch the lounge lights off", [("turn_off", {"device": "lights_living"})]),
    ("is the air con still running?", [("get_device_status", {"device": "ac"})]),
    ("kettle on and bedroom lights off",
     [("turn_on", {"device": "kettle"}), ("turn_off", {"device": "lights_bedroom"})]),
    ("my mum got a text from 'DVLA' saying her licence is suspended", [("analyze_threat", {"content": None})]),
    ("is this a scam? you have won a free cruise, reply YES", [("analyze_threat", {"content": None})]),
    ("is it ok to use hotel wifi?", []),
    ("is public wifi dangerous?", []),
    ("how do I make my wifi more secure?", []),
    ("what makes a wifi password strong?", []),
    ("what's a good age for a first phone?", []),
    ("good night guardian", []),
    ("why is the kettle so loud?", []),
]


# Written after the fresh-set failures were fixed and before re-running: the honest check
# on those fixes (FRESH itself was used to find bugs, so it no longer counts as unseen).
FRESH2 = [
    ("give my nine year old a lesson about online games", [("start_child_lesson", {"age_group": "child", "topic": None})]),
    ("my girl is 16, teach her about fake profiles", [("start_child_lesson", {"age_group": "teen", "topic": None})]),
    ("a password game for the little ones", [("start_child_lesson", {"age_group": "child", "topic": None})]),
    ("my year 10 son needs a lesson on sextortion", [("start_child_lesson", {"age_group": "teen", "topic": None})]),
    ("how locked down is our router?", [("check_router", {})]),
    ("how safe are our smart speakers?", [("check_iot_devices", {})]),
    ("is our wireless network secure?", [("check_wifi_security", {})]),
    ("is free wifi at the airport safe?", []),
    ("is it risky to use the library wifi?", []),
    ("port scan the network please", [("scan_network", {"scan_type": "port"})]),
    ("do a thorough scan", [("scan_network", {"scan_type": "full"})]),
    ("what's on my network right now?", [("scan_network", {"scan_type": "ping"})]),
    ("shut off the front room lights", [("turn_off", {"device": "lights_living"})]),
    ("boil the kettle and turn the air con on",
     [("turn_on", {"device": "kettle"}), ("turn_on", {"device": "ac"})]),
    ("is the boiler on?", [("get_device_status", {"device": "hot_water"})]),
    ("got a whatsapp from an unknown number asking for a code, is it a scam?",
     [("analyze_threat", {"content": None})]),
    ("what's the safest router brand?", []),
    ("can you recommend parental control apps?", []),
    ("how old should my kid be for instagram?", []),
    ("thanks, that's all", []),
]


def _arg_ok(expected, actual):
    for k, v in expected.items():
        if k not in actual:
            return False
        if v is None:
            continue
        a = actual[k]
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            try:
                if abs(float(a) - float(v)) > 0.01:
                    return False
            except (TypeError, ValueError):
                return False
        elif str(a).lower() != str(v).lower():
            return False
    return True


def score(expected, calls):
    names_ok = [c["name"] for c in calls] == [e[0] for e in expected]
    args_ok = names_ok and all(_arg_ok(e[1], c["args"]) for e, c in zip(expected, calls))
    return names_ok, args_ok


class RawNeedle:
    """Needle 3 on its own: all tools, no gating (the baseline)."""

    def __init__(self, weights, system=None):
        from needle import Needle
        for t in gt.TOOLS:          # no engine triggers: Needle decides entirely on its own
            t._needle_tool.pop("triggers", None)
        self.n = Needle(tools=gt.TOOLS, weights=weights, system=system)

    def calls(self, query):
        backend = gt.get_backend()
        backend.calls.clear()
        self.n.reset()
        self.n.run(query)
        return list(backend.calls)


class Routed:
    def __init__(self, weights, open_routing=False):
        from guardian_interpreter.needle_router import NeedleRouter
        self.r = NeedleRouter(weights=weights, open_routing=open_routing)

    def calls(self, query):
        gt.get_backend().calls.clear()
        res = self.r.route(query)
        return [{"name": c["name"], "args": c["args"]} for c in res.calls]


def evaluate(runner, name, cases):
    rows = []
    print(f"\n##### {name} ({len(cases)} cases) #####")
    for query, expected in cases:
        t = time.time()
        try:
            calls, err = runner.calls(query), None
        except Exception as e:
            calls, err = [], f"{type(e).__name__}: {e}"
        dt = time.time() - t
        names_ok, args_ok = score(expected, calls)
        rows.append({"set": name, "query": query, "expected": [{"name": e[0], "args": e[1]} for e in expected],
                     "calls": calls, "seconds": round(dt, 3), "tool_ok": names_ok, "args_ok": args_ok,
                     "error": err})
        mark = "PASS" if args_ok else ("TOOL" if names_ok else "FAIL")
        got = ", ".join(f"{c['name']}({', '.join(f'{k}={v!r}' for k, v in c['args'].items())})"
                        for c in calls) or "— (to Phi-4)"
        print(f"[{mark}] {query}\n       got: {got}   {dt:.2f}s" + (f"  ERROR {err}" if err else ""))
    return rows


def summary(rows, label):
    cmd = [x for x in rows if x["expected"]]
    chat = [x for x in rows if not x["expected"]]
    secs = sorted(x["seconds"] for x in rows)
    print(f"\n=== {label} ===")
    print(f"Overall exact (tool + args):          {sum(x['args_ok'] for x in rows)}/{len(rows)}")
    print(f"Commands - right tool(s):             {sum(x['tool_ok'] for x in cmd)}/{len(cmd)}")
    print(f"Commands - right args too:            {sum(x['args_ok'] for x in cmd)}/{len(cmd)}")
    print(f"Non-commands correctly sent to Phi-4: {sum(x['tool_ok'] for x in chat)}/{len(chat)}")
    print(f"Latency: median {secs[len(secs) // 2]:.2f}s, max {secs[-1]:.2f}s")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["raw", "router"], default="router")
    p.add_argument("--set", choices=["dev", "heldout", "fresh", "fresh2", "all"], default="all")
    p.add_argument("--weights", default="needle3.cact")
    p.add_argument("--system", default=None, help="system prompt (raw mode)")
    p.add_argument("--open-routing", action="store_true", help="router: let Needle route untriggered clauses")
    p.add_argument("--json", default=None)
    args = p.parse_args()

    gt.set_backend(gt.RecordingBackend())
    t = time.time()
    runner = RawNeedle(args.weights, args.system) if args.mode == "raw" else Routed(args.weights, args.open_routing)
    print(f"Mode={args.mode} weights={args.weights} loaded in {time.time() - t:.2f}s with {len(gt.TOOLS)} tools")

    rows = []
    if args.set in ("dev", "all"):
        rows += evaluate(runner, "dev", DEV)
    if args.set in ("heldout", "all"):
        rows += evaluate(runner, "heldout", HELDOUT)
    if args.set in ("fresh", "all"):
        rows += evaluate(runner, "fresh", FRESH)
    if args.set in ("fresh2", "all"):
        rows += evaluate(runner, "fresh2", FRESH2)
    for s in ("dev", "heldout", "fresh", "fresh2"):
        sub = [r for r in rows if r["set"] == s]
        if sub:
            summary(sub, f"{args.mode} / {s}")

    if args.json:
        with open(args.json, "w") as f:
            json.dump(rows, f, indent=2, default=str)
        print(f"Wrote {args.json}")


if __name__ == "__main__":
    main()
