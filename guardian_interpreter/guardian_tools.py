"""
Guardian Node tool definitions for the Needle 3 command router.

Each tool is a Needle @tool (signature + docstring = the schema Needle reads) with
trigger regexes. Triggers are matched by NeedleRouter to decide *whether* a request
is a command at all; Needle then fills in the arguments.

Tools call into a backend object so the same schema serves the live app
(GuardianBackend -> SmartHomeControl / skills / protocols), the evaluation script
and fine-tuning data generation (a recording stub). Swap it with set_backend().
"""

import logging
from typing import Any, Dict, Literal

from needle import tool

logger = logging.getLogger(__name__)

# Device ids match SmartHomeControl mock devices (smart_home.py)
Device = Literal["kettle", "ac", "hot_water", "lights_living", "lights_bedroom"]

DEVICE_WORDS = r"(kettle|air ?con|a/?c\b|ac\b|air conditioner|hot water|boiler|heater|lights?|lamps?)"


class GuardianBackend:
    """Runs tool calls against the real Guardian modules."""

    def __init__(self, smart_home=None):
        self._smart_home = smart_home

    @property
    def smart_home(self):
        if self._smart_home is None:
            from guardian_interpreter.smart_home import create_smart_home_control
            self._smart_home = create_smart_home_control()
        return self._smart_home

    def call(self, name: str, **kwargs) -> Any:
        if name == "turn_on":
            return self.smart_home.turn_on(kwargs["device"])
        if name == "turn_off":
            return self.smart_home.turn_off(kwargs["device"])
        if name == "set_temperature":
            return self.smart_home.set_temperature(kwargs["device"], kwargs["temperature"])
        if name == "get_device_status":
            return self.smart_home.get_status(kwargs["device"])
        if name == "scan_network":
            from guardian_interpreter.skills import lan_scanner
            return lan_scanner.run(None, kwargs.get("scan_type", "ping"))
        if name == "check_router":
            from guardian_interpreter.skills import router_checker
            return router_checker.run(None, "security")
        if name == "check_wifi_security":
            from guardian_interpreter.protocols import wifi_security_protocol
            return wifi_security_protocol.analyze()
        if name == "check_parental_controls":
            from guardian_interpreter.protocols import parental_control_protocol
            return parental_control_protocol.analyze()
        if name == "check_iot_devices":
            from guardian_interpreter.protocols import iot_security_protocol
            return iot_security_protocol.analyze()
        if name == "analyze_threat":
            return scam_red_flags(kwargs["content"])
        if name == "start_child_lesson":
            from guardian_interpreter.skills import child_education_skill
            # the skill keys its content on school-stage words, not "child"/"teen"
            stage = "elementary" if kwargs["age_group"] == "child" else "high school"
            return child_education_skill.run(f"{stage} {kwargs['topic']}")
        raise ValueError(f"unknown tool {name}")


SCAM_SIGNS = [
    (r"\b(urgent|immediately|within 24 hours|today only|act now|final notice|suspended|locked|expire[sd]?)\b",
     "pressure to act fast"),
    (r"\b(pay|payment|fee|refund|voucher|gift card|bank details|card details|crypto|bitcoin|send (me |us )?(£|\$)?\d+)\b",
     "asks for money or payment details"),
    (r"\b(password|passcode|pin|login|log in|verify|confirm your|security code|one[- ]time code|\bcode\b)",
     "asks you to log in, verify or share a code"),
    (r"https?://|\bwww\.|\bbit\.ly\b|\btinyurl\b|\b[\w-]+\.(xyz|top|info|click|link|co|net)\b", "contains a link"),
    (r"\b(won|winner|congratulations|prize|free)\b", "too-good-to-be-true offer"),
    (r"\b(hi mum|hi dad|new number|my phone broke)\b", "'new number' family impersonation"),
    (r"\b(hmrc|dvla|royal mail|dpd|evri|amazon|netflix|paypal|apple|microsoft|bank)\b",
     "claims to be a well-known organisation"),
    (r"[a-z]+[0-9][a-z]*\.(com|net|co)\b|\b(paypa1|amaz0n|app1e|micros0ft)\b", "lookalike web address"),
]


def scam_red_flags(content: str) -> Dict[str, Any]:
    """Instant, offline red-flag check on a suspicious message (the LLM explains the verdict)."""
    import re
    flags = [label for pattern, label in SCAM_SIGNS if re.search(pattern, content, re.IGNORECASE)]
    level = "high" if len(flags) >= 3 else "medium" if flags else "low"
    return {"status": f"{level} scam risk", "red_flags": flags, "content": content,
            "recommendations": ["Don't click links or reply; contact the organisation using a number or app you "
                                "already trust."] if flags else []}


class RecordingBackend:
    """Records calls instead of running them (evaluation / dry runs)."""

    def __init__(self):
        self.calls = []

    def call(self, name: str, **kwargs) -> Dict[str, Any]:
        self.calls.append({"name": name, "args": kwargs})
        return {"ok": True, "tool": name, **kwargs}


_backend = RecordingBackend()
# When set, only these tool names may execute; anything else Needle picks is blocked.
_allowed = None
blocked_calls = []


def set_backend(backend) -> None:
    global _backend
    _backend = backend


def get_backend():
    return _backend


def set_allowed(names) -> None:
    global _allowed
    _allowed = set(names) if names is not None else None


def _call(name, **kwargs):
    if _allowed is not None and name not in _allowed:
        blocked_calls.append({"name": name, "args": kwargs})
        return {"ok": False, "error": f"{name} not permitted for this request"}
    try:
        return _backend.call(name, **kwargs)
    except Exception as e:
        logger.error(f"Tool {name} failed: {e}")
        return {"ok": False, "error": str(e)}


@tool(triggers=[r"\b(turn|switch|put|flick)\s+(on|the|my|\w+\s+on)\b.*" + DEVICE_WORDS,
                r"\b(turn|switch|put)\s+.*\bon\b",
                DEVICE_WORDS + r".*\bon\b(?!\?)(?! yet)",
                r"\b(heat up|boil)\b"])
def turn_on(device: Device) -> dict:
    """Turn on a smart home device. Devices: kettle, ac (air conditioner), hot_water (hot water heater),
    lights_living (living room lights), lights_bedroom (bedroom lights)."""
    return _call("turn_on", device=device)


@tool(triggers=[r"\b(turn|switch|shut|put)\s+(\w+\s+){0,5}off\b",
                r"\b(turn|switch|shut|put)\s+off\b",
                DEVICE_WORDS + r".*\boff\b(?!\?)"])
def turn_off(device: Device) -> dict:
    """Turn off a smart home device. Devices: kettle, ac (air conditioner), hot_water (hot water heater),
    lights_living (living room lights), lights_bedroom (bedroom lights)."""
    return _call("turn_off", device=device)


@tool(triggers=[r"\b(set|make|put|change)\b.*\b(temp|temperature|air ?con|ac|a/c|thermostat)\b.*\d",
                r"\b\d{2}\s*(degrees|°)"])
def set_temperature(device: Literal["ac"], temperature: float) -> dict:
    """Set the target temperature in Celsius of the air conditioner (ac)."""
    return _call("set_temperature", device=device, temperature=temperature)


@tool(triggers=[r"^\s*(is|are)\s+(the\s+)?" + DEVICE_WORDS + r".*\b(on|off|running)\b",
                r"\b(status|state)\s+of\b.*" + DEVICE_WORDS,
                r"\b(did i|have i)\s+(leave|left)\b.*" + DEVICE_WORDS])
def get_device_status(device: Device) -> dict:
    """Check whether a smart home device is on or off, and its current settings."""
    return _call("get_device_status", device=device)


@tool(triggers=[r"\bscan\b",
                r"\bwhat(\s+devices|'s|\s+is)\b.*\b(connected|on)\b.*\b(wifi|wi-fi|network)\b",
                r"\bwho('s|\s+is)\s+(on|connected to)\s+(my|the|our)\s+(wifi|wi-fi|network)\b",
                r"\b(list|show)\b.*\bdevices\b.*\b(network|wifi|wi-fi|connected)\b",
                r"\bopen ports?\b"])
def scan_network(scan_type: Literal["ping", "port", "full"] = "ping") -> dict:
    """Scan the home network to list connected devices. ping = quick device list,
    port = check open ports, full = both."""
    return _call("scan_network", scan_type=scan_type)


@tool(triggers=[r"\b(check|test|audit|secure|inspect|look at)\b.*\brouter\b",
                r"\b(safe|secure|protected|private|locked down|hacked)\b.*\b(my|our|the)\s+(home\s+)?router\b",
                r"\brouter\b.*\b(secure|safe|ok|okay|hacked|password|firmware|settings)\b"])
def check_router() -> dict:
    """Check the home router / gateway security: default passwords, admin access, firmware."""
    return _call("check_router")


@tool(triggers=[r"\b(check|test|audit)\b.*\b(wifi|wi-fi|wireless)\b(?!.*\bdevices\b)",
                r"\b(safe|secure|protected|private|locked down|hacked)\b.*\b(my|our|the)\s+(home\s+)?(wifi|wi-fi|wireless|network)\b",
                r"\b(wifi|wi-fi|wireless)\b.*\b(secure|safe|encrypt\w*|wpa\d?|password)\b(?!.*\bmanager\b)"])
def check_wifi_security() -> dict:
    """Check the Wi-Fi network security: encryption type (WPA2/WPA3), password strength, guest network."""
    return _call("check_wifi_security")


@tool(triggers=[r"\bparental controls?\b",
                r"\b(content|web|dns)\s+filter",
                r"\b(check|audit|test)\b.*\b(screen ?time|bedtime)\b"])
def check_parental_controls() -> dict:
    """Audit parental controls: content filtering, DNS filtering, screen time and bedtime restrictions."""
    return _call("check_parental_controls")


@tool(triggers=[r"\b(smart|iot)\s+(devices?|cameras?|speakers?|tvs?|plugs?|doorbells?|home)\b.*\b(safe|secure|check|hacked|ok|okay)\b",
                r"\b(safe|secure|protected|private|locked down|hacked)\b.*\b(my|our|the)\s+(home\s+)?(smart\s+)?(cameras?|speakers?|tvs?|doorbells?|plugs?|gadgets|baby monitor|iot devices|smart devices)\b",
                r"\b(check|audit|test|secure)\b.*\b(smart|iot)\s+(devices?|cameras?|speakers?|tvs?|plugs?|doorbells?)\b",
                r"\b(cameras?|baby monitor|doorbell|alexa|echo|google home)\b.*\b(safe|secure|hacked)\b"])
def check_iot_devices() -> dict:
    """Audit smart/IoT devices (cameras, speakers, smart TVs) for default passwords and outdated firmware."""
    return _call("check_iot_devices")


@tool(triggers=[r"\b(got|received|getting|sent|texted|emailed)\b.*\b(text|sms|email|e-mail|message|call|link|dm|pop-?up|letter)\b",
                r"\b(is (this|that)|this is|looks like)\b.*\b(scam|phishing|legit|real|fake|genuine|safe)\b",
                r"\bis it (a |an )?(scam|phishing|legit|real|fake|genuine)\b",
                r"\b(suspicious|dodgy|weird|strange)\s+(text|email|e-mail|message|link|website|site|call|pop-?up)\b",
                r"https?://|\bwww\.|\b[\w-]+\.(com|co|net|org|uk|info|xyz|top|co\.uk)\b"])
def analyze_threat(content: str) -> dict:
    """Analyse a suspicious message, email, text, link or pop-up the user received for scams or phishing.
    content is the suspicious text or link."""
    return _call("analyze_threat", content=content)


KID_WORDS = (r"(kid|kids|child|children|son|daughter|boy|girl|teen|teens|teenager|teenage|little ones?|"
             r"(\d{1,2}|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen)"
             r"[ -]years?[ -]old|year \d)")


@tool(triggers=[r"\b(teach|lesson|activity|game|quiz|learn)\b.*\b" + KID_WORDS + r"\b",
                r"\b" + KID_WORDS + r"\b.*\b(lesson|activity|game|quiz|learn about|teach)\b"])
def start_child_lesson(age_group: Literal["child", "teen"], topic: str) -> dict:
    """Start an interactive cybersecurity lesson/activity for a child (under 13) or teen,
    e.g. passwords, strangers online, cyberbullying, privacy, scams."""
    return _call("start_child_lesson", age_group=age_group, topic=topic)


TOOLS = [turn_on, turn_off, set_temperature, get_device_status, scan_network, check_router,
         check_wifi_security, check_parental_controls, check_iot_devices, analyze_threat,
         start_child_lesson]
