"""
Generate Guardian Node fine-tuning data for Needle 3 (offline, template-based; no cloud).

Output JSONL rows in Needle's finetune format:
  {"query": ..., "tools": [schemas], "reasoning": ..., "answers": [{"name": ..., "arguments": {...}}]}

About a third of rows are questions/chit-chat with "answers": [] so the model learns
to decline (those go to Phi-4). Every query in the evaluation sets
(scripts/needle_router_eval.py DEV + HELDOUT) is excluded.

Usage:
    python scripts/needle_finetune/make_dataset.py --n 2000 --out guardian_train.jsonl
"""

import argparse
import copy
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
os.environ.setdefault("NEEDLE_TELEMETRY", "0")

from guardian_interpreter import guardian_tools as gt  # noqa: E402
import needle_router_eval as ev  # noqa: E402

SCHEMAS = []
for t in gt.TOOLS:
    s = copy.deepcopy(t._needle_tool)
    s.pop("triggers", None)
    SCHEMAS.append(s)

DEVICES = {
    "kettle": ["kettle", "the kettle"],
    "ac": ["air con", "aircon", "the ac", "the a/c", "air conditioner", "air conditioning", "the air con"],
    "hot_water": ["hot water", "the hot water", "water heater", "the immersion", "the boiler"],
    "lights_living": ["living room lights", "lounge lights", "front room lights", "the living room lamp",
                      "lights in the living room", "the lounge lamp"],
    "lights_bedroom": ["bedroom lights", "the bedroom lamp", "lights in the bedroom", "bedroom light",
                       "the lights in my bedroom"],
}
POLITE_PRE = ["", "", "", "please ", "can you ", "could you ", "hey guardian, ", "guardian ", "ok ", "quickly "]
POLITE_POST = ["", "", "", " please", " for me", " thanks", " now", " right now"]
ON_TPL = ["turn on {d}", "switch on {d}", "turn {d} on", "switch {d} on", "{d} on", "power up {d}",
          "put {d} on", "start {d}", "fire up {d}", "get {d} going"]
OFF_TPL = ["turn off {d}", "switch off {d}", "turn {d} off", "switch {d} off", "{d} off", "power down {d}",
           "shut off {d}", "kill {d}", "put {d} off", "shut {d} off"]
STATUS_TPL = ["is {d} on", "is {d} on?", "is {d} still on?", "did someone leave {d} on?", "is {d} off?",
              "what's the status of {d}", "check if {d} is on", "is {d} running?", "have i left {d} on"]
TEMP_TPL = ["set the {d} to {t} degrees", "set {d} to {t}", "make it {t} degrees", "change the temperature to {t}",
            "put the {d} on {t}", "i want it at {t} degrees", "set the temperature to {t} celsius",
            "cool the room to {t}", "{d} to {t} degrees please"]
AC_WORDS = ["air con", "aircon", "ac", "air conditioner", "thermostat"]
CONNECT = [" and ", " and then ", ", then ", " then ", " and also ", ", and "]

SCAN = {
    "ping": ["scan my network", "run a network scan", "what's connected to our wifi", "list the devices on my network",
             "show me everything on the network", "any new devices on the wifi?",
             "do a quick scan of the network", "scan for devices", "how many devices are on my wifi right now"],
    "port": ["scan for open ports", "check which ports are open on my network", "do a port scan",
             "are there any open ports on the network", "run a port scan on my devices"],
    "full": ["do a full network scan", "run a complete scan with ports", "full scan of everything on the network",
             "deep scan my network including ports", "run the full scan"],
}
NOARG = {
    "check_router": ["check the router", "is my router safe", "audit my router", "run a router security check",
                     "is the router using the default password", "check my router firmware",
                     "make sure my router is secure", "could my router be hacked", "test the router security",
                     "look at my router settings for problems"],
    "check_wifi_security": ["check my wifi security", "is my wifi encrypted", "is our wifi using wpa3",
                            "check the wireless network is secure", "test my wifi password strength",
                            "audit the wifi settings", "is the guest wifi set up safely", "check wifi encryption",
                            "check how safe our home wifi setup is", "make sure the wifi is locked down"],
    "check_parental_controls": ["check parental controls", "are the content filters on", "audit the kids' screen time limits",
                                "is the dns filtering working", "check the bedtime restrictions are active",
                                "make sure the parental filters are working", "test the web filter",
                                "review the screen time settings", "are the kids' internet limits working"],
    "check_iot_devices": ["check my smart devices", "are the security cameras safe", "audit the smart tv",
                          "is the ring doorbell secure", "check the smart plugs for default passwords",
                          "are my iot devices up to date", "is alexa secure", "check the smart speakers",
                          "could someone hack the baby camera", "audit all the smart home gadgets"],
}
SCAMS = [
    "your parcel could not be delivered, pay the £2.99 fee at dpd-reschedule.info",
    "HMRC: you are due a tax refund of £412, claim at hmrc-refunds.co",
    "your amazon account is locked, verify your card at amaz0n-secure.net",
    "hi mum my phone broke this is my new number can you send me £200",
    "congratulations you've won a £500 tesco voucher, click to claim",
    "your bank has flagged a payment, call 0800 000 111 to cancel it",
    "netflix: payment failed, update your details at netflix-billing.xyz",
    "apple id suspended, log in at appleid-verify.top to restore",
    "you have an unpaid toll charge, pay now at tollpay-uk.com",
    "microsoft support: your pc has a virus, call this number immediately",
    "free robux generator, just enter your roblox password",
    "your package is waiting, confirm your address http://bit.ly/pk9z",
    "crypto investment doubling your money in 24 hours, join now",
    "your paypal account will be closed unless you confirm at paypal-help.co",
    "instagram: someone tried to log in, verify at insta-security.net",
]
SCAM_PRE = ["i got a text saying \"{m}\" is it real?", "is this a scam: {m}", "my dad got an email: {m}",
            "someone messaged my daughter: {m}", "got this message, is it legit? {m}", "check this for me: {m}",
            "is this phishing? {m}", "i received this email today: {m}", "my son got a dm saying {m}",
            "should i trust this text: {m}", "a pop-up said {m}", "we got a call and then a text: {m}"]
TOPICS = ["passwords", "stranger danger", "cyberbullying", "online privacy", "scams", "phishing",
          "safe gaming", "social media safety", "sharing photos online", "screen time", "fake news",
          "talking to strangers online", "privacy settings", "downloading apps safely", "digital footprint"]
LESSON_TPL = ["teach {k} about {t}", "start a lesson on {t} for {k}", "create a game about {t} for {k}",
              "i want {k} to learn about {t}", "can you do a {t} activity with {k}", "quiz {k} on {t}",
              "run a {t} lesson for {k}", "help {k} learn {t}", "a fun activity about {t} for {k}"]
REFUSALS = [
    # security explanations (Phi-4)
    "what is a router", "what does wpa3 mean", "explain two factor authentication",
    "why do i need antivirus", "what is malware", "how do scammers get my number", "how do i spot a fake website", "why is my wifi slow", "what is ransomware",
    "how do smart plugs work", "should i use the same password everywhere", "how can i keep my kids safe online", "what age should kids get a phone", "why do apps want my location", "what is identity theft", "what's the best way to back up photos", "what happens if my router gets hacked",
    "how do i know if my phone has a virus", "what is a scam text", "what does encryption do",
    "is it bad to leave the kettle on", "how much power does the air con use", "what's a smart home",
    "what is cyberbullying", "how do i talk to my teen about sexting", "what is a botnet",
    "how often should i change my wifi password", "tell me about online grooming warning signs",
    "is bluetooth safe", "why are default passwords dangerous", # chit-chat / off-topic
    "hello", "thank you", "good morning guardian", "tell me a story", "what's the capital of france",
    "sing a song", "what time is it", "who are you", "what can you do", "i'm bored", "how are you today",
    "what's 12 times 8", "recommend a film", "what's for dinner", "write a haiku about dogs",
    "set an alarm for 7am", "play some music", "order a pizza", "call mum",
    "what's the news today", "translate hello into spanish", "who won the football", "tell me a fun fact",
    "remind me to buy milk", "goodnight", "you're awesome", "what year is it", "how tall is everest",
]
REFUSAL_WRAP = ["{q}", "{q}?", "hey guardian {q}", "can you tell me {q}", "{q} please", "quick question, {q}",
                "guardian, {q}", "i was wondering {q}", "ok so {q}", "my wife asked {q}", "my kid wants to know {q}",
                "um {q}", "{q} thanks", "just curious, {q}", "do you know {q}"]


def age_group(a):
    return "child" if a < 13 else "teen"


def pol(s):
    return (random.choice(POLITE_PRE) + s + random.choice(POLITE_POST)).strip()


def row(query, answers, reasoning):
    return {"query": query, "tools": SCHEMAS, "reasoning": reasoning, "answers": answers}


def call(name, **args):
    return {"name": name, "arguments": args}


def gen_onoff():
    dev = random.choice(list(DEVICES))
    on = random.random() < 0.5
    tpl = random.choice(ON_TPL if on else OFF_TPL)
    name = "turn_on" if on else "turn_off"
    q = pol(tpl.format(d=random.choice(DEVICES[dev])))
    return row(q, [call(name, device=dev)], f"{name.replace('_', ' ')} {dev}")


def gen_multi():
    devs = random.sample(list(DEVICES), 2)
    same = random.random() < 0.6
    ons = [random.random() < 0.5] * 2 if same else [True, False] if random.random() < 0.5 else [False, True]
    parts, answers = [], []
    for i, (dev, on) in enumerate(zip(devs, ons)):
        name = "turn_on" if on else "turn_off"
        if i == 1 and same and random.random() < 0.5:
            parts.append(random.choice(DEVICES[dev]))           # "turn off the kettle and the lights"
        else:
            parts.append(random.choice(ON_TPL if on else OFF_TPL).format(d=random.choice(DEVICES[dev])))
        answers.append(call(name, device=dev))
    q = pol(parts[0] + random.choice(CONNECT) + parts[1])
    if random.random() < 0.2:
        q = random.choice(["it's bedtime, ", "we're going out, ", "i'm home, ", "morning, "]) + q
    return row(q, answers, "two actions: " + ", ".join(f"{a['name']} {a['arguments']['device']}" for a in answers))


def gen_status():
    dev = random.choice(list(DEVICES))
    q = pol(random.choice(STATUS_TPL).format(d=random.choice(DEVICES[dev])))
    return row(q, [call("get_device_status", device=dev)], f"status of {dev}")


def gen_temp():
    t = random.randint(16, 28)
    q = pol(random.choice(TEMP_TPL).format(d=random.choice(AC_WORDS), t=t))
    return row(q, [call("set_temperature", device="ac", temperature=t)], f"set ac to {t}")


def gen_scan():
    st = random.choices(["ping", "port", "full"], weights=[3, 1, 1])[0]
    return row(pol(random.choice(SCAN[st])), [call("scan_network", scan_type=st)], f"{st} scan of the network")


def gen_noarg():
    name = random.choice(list(NOARG))
    return row(pol(random.choice(NOARG[name])), [call(name)], name.replace("_", " "))


def gen_two_checks():
    a, b = random.sample(list(NOARG) + ["scan_network"], 2)
    def phrase(n):
        return random.choice(SCAN["ping"]) if n == "scan_network" else random.choice(NOARG[n])
    answers = [call(n, scan_type="ping") if n == "scan_network" else call(n) for n in (a, b)]
    return row(pol(phrase(a) + random.choice(CONNECT) + phrase(b)), answers, f"two checks: {a}, {b}")


def gen_threat():
    m = random.choice(SCAMS)
    q = random.choice(SCAM_PRE).format(m=m)
    return row(q, [call("analyze_threat", content=m)], "user received a suspicious message; analyse it")


def gen_lesson():
    a = random.randint(5, 17)
    k, g = random.choice([
        (f"my {a} year old", age_group(a)), (f"my {a}-year-old", age_group(a)), (f"our {a} year old", age_group(a)),
        (f"my son who is {a}", age_group(a)), (f"my daughter, who's {a},", age_group(a)),
        ("the kids", "child"), ("my little one", "child"), ("the children", "child"),
        ("my teenager", "teen"), ("my teen", "teen"), ("the teens", "teen")])
    topic = random.choice(TOPICS)
    q = pol(random.choice(LESSON_TPL).format(k=k, t=topic))
    return row(q, [call("start_child_lesson", age_group=g, topic=topic)], f"{g} lesson on {topic}")


def gen_refusal():
    q = random.choice(REFUSAL_WRAP).format(q=random.choice(REFUSALS))
    return row(q, [], "question or chat, no tool applies; answer in words")


GENERATORS = [(gen_onoff, 16), (gen_multi, 8), (gen_status, 6), (gen_temp, 6), (gen_scan, 7),
              (gen_noarg, 12), (gen_two_checks, 4), (gen_threat, 7), (gen_lesson, 8), (gen_refusal, 30)]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=2000)
    p.add_argument("--out", default="guardian_train.jsonl")
    p.add_argument("--seed", type=int, default=7)
    args = p.parse_args()
    random.seed(args.seed)

    excluded = {q.strip().lower().rstrip("?") for q, _ in ev.DEV + ev.HELDOUT}
    fns, weights = zip(*GENERATORS)
    seen, rows, tries = {}, [], 0
    while len(rows) < args.n and tries < args.n * 50:
        tries += 1
        r = random.choices(fns, weights=weights)[0]()
        key = r["query"].strip().lower().rstrip("?")
        if key in excluded:
            continue
        # refusals may repeat (up to 3x) so ~a third of the data teaches "no tool"
        if seen.get(key, 0) >= (3 if not r["answers"] else 1):
            continue
        seen[key] = seen.get(key, 0) + 1
        rows.append(r)
    with open(args.out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    refusals = sum(1 for r in rows if not r["answers"])
    print(f"wrote {len(rows)} rows to {args.out} ({refusals} refusals, {len(rows) - refusals} with calls)")


if __name__ == "__main__":
    main()
