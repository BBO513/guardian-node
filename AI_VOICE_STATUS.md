# Guardian Node — AI, Voice & Raspberry Pi Status

*Last updated: 25 September 2026 · Branch: `clean-rewrite-investor-ready` · Latest commit: `1104514`*

This document records the work done to (1) evaluate and adopt **Needle 3** as Guardian's fast
command AI, (2) get Guardian running on a **Raspberry Pi 5**, and (3) build an offline **voice**
pipeline — plus what is still needed.

---

## 1. Summary

Guardian now uses **two offline AI models that do different jobs**:

| Model | Job | Size | Speed on Pi 5 |
|---|---|---|---|
| **Needle 3** (Cactus Compute, Apache 2.0) | Decides *what to do*: lights, scans, security checks, scam checks, lessons | 34 MB base / 63 MB fine-tuned | ~0.3 s per request, ~100 MB RAM |
| **Phi-4-mini** (Microsoft, Q4_K_M GGUF) | *Explains things* to the family in plain words | 2.4 GB | ~4.3 tokens/s, first words in ~3 s (streamed) |

A **command router** sits in front: commands run instantly via Needle; everything else goes to
Phi-4. Voice uses **Kokoro** (natural neural voice) with Piper as fallback. Everything runs
offline on the Pi — no cloud.

**Headline results (on the Pi 5):**

| | Before | Now |
|---|---|---|
| "Turn off the air con" (voice) | ~45 s (Phi-4 had to answer) | Spoken reply in ~3 s (Kokoro) / 0.2 s (Piper) |
| Command routing accuracy (97 test requests) | 11/26 raw Needle | 97/97 (see §4 for the honest caveat) |
| Spoken answer to a question | ~45 s silence, then speech | First words ~8–10 s, no gaps, done in ~13–15 s |
| Scam message check | "couldn't find specific information" | Instant red flags + Phi-4 verdict |

---

## 2. Hardware & environment

### Raspberry Pi 5 (test device)
- 8 GB RAM, 4 cores, 64 GB SD card (~49 GB free) · Debian 13 "trixie", 64-bit (aarch64) · Python 3.13
- Address `192.168.1.11`, user `arge`, passwordless SSH from the Windows PC (key `~/.ssh/id_ed25519`)
- Repo: `~/guardian-node` (git clone, tracks GitHub) · Python venv: `~/guardian-node/.venv`
- Audio: **USB headset** ("USB Audio", 48 kHz only) via PipeWire; HDMI audio unused (no display attached)

### Windows PC (development + training)
- NVIDIA RTX 2060 (12 GB) · WSL Ubuntu with a Needle training env at `~/needle-train/.venv`
  (Python 3.12, JAX + CUDA 12)

### Files on the Pi that are NOT in git (large models)

| Path | What | Size |
|---|---|---|
| `models/microsoft_Phi-4-mini-instruct-Q4_K_M.gguf` | Phi-4-mini LLM | 2.4 GB |
| `needle3.cact` | Needle 3 base model | 34 MB |
| `models/guardian_needle.cact` | Needle 3 fine-tuned on Guardian data | 63 MB |
| `models/kokoro/kokoro-v1.0.fp16.onnx` (+ `.onnx`, `.int8.onnx`) | Kokoro voice model (fp16 is used) | 170 MB |
| `models/kokoro/voices-v1.0.bin` | Kokoro voices | 27 MB |
| `guardian_interpreter/voice/piper_voices/*.onnx` | 6 Piper voices (fallback) | 61–116 MB each |

### Installed on the Pi
- **System (apt):** `build-essential cmake python3-dev portaudio19-dev libportaudio2 espeak-ng flac`
- **Python (venv):** `cactus-needle==3.0.4`, `llama-cpp-python 0.3.35` (compiled on the Pi),
  `kokoro-onnx 0.6.1`, `onnxruntime 1.30`, `piper-tts 1.8.0`, `SpeechRecognition 3.17`,
  `pocketsphinx 5.1.1`, `PyAudio 0.2.14`, `sounddevice`, `pyttsx3`, `PySide6 6.11`, `psutil`

---

## 3. What was built

### 3.1 Needle command router — `guardian_interpreter/needle_router.py`
Out of the box, Needle 3 called a tool for *everything* (even "write me a poem") — 0/6 questions
correctly declined. So routing is gated by rules, and Needle fills in details:

1. **Explanation gate** — "what is…", "why…", "explain…", "is it safe to use public wifi?",
   "recommend…" → Phi-4. But "how safe is **my** wifi/router" → a check (own-kit rule).
2. **Compound commands split** — "turn off the kettle and the living room lights" → two actions
   (verb carried over). Only splits when every part is a command.
3. **Trigger regexes pick candidate tools**; no candidate → Phi-4.
4. **Needle fills arguments**, restricted to the candidates (anything else it picks is blocked).
5. **Facts read from the words override Needle:** child's age ("8 year old", "is 15", "twelve",
   "year 9", "teenage", "little"), device ("lounge" → living room, "boiler" → hot water),
   scan type ("ports" → port scan, "thorough" → full).
6. **Safety:** the same action never runs twice; if Needle declines a clear command, arguments are
   read from the words instead.
7. `describe()` turns results into a short reply (full text for chat, short for speech);
   `followup_prompt()` hands scam checks to Phi-4 for a plain-English verdict.

### 3.2 Guardian tools — `guardian_interpreter/guardian_tools.py`
11 tools, each a Needle `@tool` with trigger phrases and a pluggable backend
(`GuardianBackend` = real modules, `RecordingBackend` = dry run for tests):

`turn_on`, `turn_off`, `set_temperature`, `get_device_status` (SmartHomeControl) ·
`scan_network` (lan_scanner) · `check_router` (router_checker) · `check_wifi_security`,
`check_parental_controls`, `check_iot_devices` (protocols) · `analyze_threat` (new offline
**scam red-flag check**: urgency, payment requests, links, lookalike domains, "hi mum new number"…) ·
`start_child_lesson` (child_education_skill, age-appropriate content).

### 3.3 GUI integration — `guardian_gui.py`
- Router loads in ~1 s at startup, **independently of Phi-4**, so commands work while Phi-4 is
  still loading. If `cactus-needle` is missing, the GUI falls back to Phi-4 only.
- **Chat:** commands answer instantly; questions **stream** word-by-word from Phi-4.
- **Voice:** commands spoken back immediately; questions answered in 2–3 short spoken sentences.
  Phi-4 and Kokoro **take turns on the CPU** (write a sentence → render it → write the next while
  it plays), which removed 12-second gaps caused by both competing for the 4 cores.
- `GuardianLLM.stream_response()` added in `llm_integration.py` (llama.cpp streaming).

### 3.4 Voice — `guardian_interpreter/voice/voice_interface.py`
- **TTS order:** Kokoro (most natural) → Piper (fast) → pyttsx3. All offline.
- Kokoro fp16 model runs at ~1.1× real time on the Pi (int8 was 3× slower).
- `synthesize()` / `play_file()` split so audio can be prepared ahead of playback.
- **Loudness boost** (soft limiter) for quiet headsets.
- **Playback via PipeWire (`pw-play`)** on Linux, which resamples Piper/Kokoro audio to the
  headset's 48 kHz (direct playback failed with "invalid sample rate").
- **Speech recognition:** still pocketsphinx (offline) — **not accurate enough** (see §6).

### 3.5 Needle fine-tuning pipeline — `scripts/needle_finetune/`
| File | Purpose |
|---|---|
| `make_dataset.py` | Generates 2,000 offline training examples from templates (~30% "no tool" questions); excludes every test sentence |
| `setup_wsl.sh` / `train_wsl.sh` | One-time WSL GPU setup / train + export on the RTX 2060 (batch 4; batch 16 ran out of GPU memory) |
| `train_cloud.sh` | Self-contained training for **any Linux GPU box** (cloud GPU, Colab, RunPod…) |

Training: LoRA on the frozen 20-layer base, 3 epochs, final validation loss 0.0135, ~30 min on the 2060.
Note: the local build has **no confidence head** (Cactus's paid platform keeps it) and exports 4-bit
(63 MB) rather than Cactus's 2-bit.

### 3.6 Tests
- `scripts/needle_router_eval.py` — 97 real requests in 4 sets (dev / heldout / fresh / fresh2),
  modes `raw` (Needle alone) or `router`. Tools are stubbed, nothing is actually switched or scanned.
- `tests/test_needle_router.py` — 9 fast rule-layer regression tests (0.03 s), including a check that
  catches the broken-regex bug we hit (a `\b` that turned into a backspace, then a letter "b").

### 3.7 Other fixes
- `requirements.txt` (both): `cactus-needle==3.0.4` pinned — **3.0.5 asks for an engine build (3.0.2)
  that Cactus hasn't published**, so `needle fetch` 404s.
- Needle telemetry turned off by the router (`NEEDLE_TELEMETRY=0`) to match "no telemetry".
- `.gitignore`: 20 GB of local backups (`Found backup of guardian_node/`, `guardian_node_v1/`) and
  training data; `.gitattributes`: `*.sh` kept with Linux line endings.

### Commits
| Commit | What |
|---|---|
| `e1b5347` | Switch to Phi-4-mini, GUI chat panel, Piper voice, parental-control fixes (pre-existing work) |
| `ced1a80` | Needle router, Guardian tools, eval suite, fine-tuning pipeline |
| `ae35348` | GUI chat + voice through the router; streamed LLM answers; scam check; lessons fix |
| `b7e0d88` | Voice playback via PipeWire (48 kHz USB headsets) |
| `1104514` | Kokoro voice, loudness boost, LLM/voice CPU turn-taking, short spoken answers |

---

## 4. Evaluation history (on the Pi)

| Setup | Original 26 | Held-out 24 | Fresh 27 | Fresh2 20 | Questions → Phi-4 |
|---|---|---|---|---|---|
| Raw Needle 3 (no router) | 11 | – | – | – | 0/6 |
| Raw fine-tuned Needle | 22 | 16 | – | – | 14/14 |
| Router v1 + base Needle | 24 | 21 | 16 | – | 13/14 |
| Router v1 + fine-tuned | 25 | 20 | 17 | – | 13/14 |
| Router final + base | 26 | 24 | 27 | 20 | all |
| **Router final + fine-tuned (in use)** | **26** | **24** | **27** | **20** | **all** |

**Honest caveat:** every set has now been used to find bugs, so 97/97 shows the fixes hold, not
that the router generalises. The last *clean* measurement was **Fresh2 before its fixes: 15/20 (75%)**.
Expect roughly 75–90% on truly new phrasing until trained on real family requests.

With the rule layer doing ages/devices/scan types, base and fine-tuned Needle score the same; the
fine-tuned model is kept because on its own it correctly declines questions (14/14 vs 0/6).

---

## 5. How to run & configure

```bash
# On the Pi
cd ~/guardian-node && git pull && source .venv/bin/activate
python guardian_gui.py                                     # GUI (needs a display / touchscreen)
python -m unittest tests.test_needle_router                # fast regression tests
python scripts/needle_router_eval.py --mode router --weights models/guardian_needle.cact
```

| Environment variable | Default | Purpose |
|---|---|---|
| `GUARDIAN_TTS` | `kokoro` | `kokoro` or `piper` |
| `GUARDIAN_KOKORO_VOICE` | `bf_emma` | Kokoro voice (`bf_isabella`, `bm_george`, `bm_lewis`, `af_heart`, `am_michael`, …) |
| `GUARDIAN_KOKORO_DIR` | `models/kokoro` | Where Kokoro model files live |
| `GUARDIAN_VOICE_GAIN` | `2.5` | Loudness boost (1.0 = off) |
| `PIPER_VOICE_NAME` | `en_US-lessac-medium` | Piper fallback voice |
| `GUARDIAN_CONTEXT_LENGTH` / `GUARDIAN_THREADS` | `8192` / `4` | Phi-4 context and CPU threads |
| `NEEDLE_TELEMETRY` | `0` (set by router) | Needle usage counts off |

Headset volume: `wpctl set-volume @DEFAULT_AUDIO_SINK@ 1.0` (was 40%; now 100%).

**Retraining Needle on a cloud GPU:** clone the repo on the GPU box →
`bash scripts/needle_finetune/train_cloud.sh [epochs] [batch]` → copy `out/guardian_needle.cact`
to the Pi's `models/` → rerun the eval.

---

## 6. Known issues & limitations

1. **Speech recognition is poor.** pocketsphinx got 1/5 synthetic commands right ("switch the kettle
   on" → "which the cattle and") and misheard a real mic test ("turn off the bed really wants").
   The router can't act on wrong words. **Biggest remaining problem.**
2. **Kokoro command replies take ~3 s** (Piper: 0.2 s). Fine, but noticeable.
3. **Kokoro voice not chosen yet** — defaulting to `bf_emma`.
4. **Model files aren't installable yet:** Kokoro, Needle and the fine-tuned model are only on the Pi;
   `download_model.sh/.ps1` only fetch Phi-4.
5. **`requirements.txt` is missing the voice packages** (`kokoro-onnx`, `piper-tts`, `SpeechRecognition`,
   `pocketsphinx`, `PyAudio`, `sounddevice`) and the apt packages aren't in the install script.
6. **CLI (`main.py`) still uses old keyword matching** — only the GUI and voice use the router.
7. **Real scans not yet run from the Pi** — network scan / router / Wi-Fi checks were tested dry.
8. **Phi-4 uses ~5.8 GB RAM at 8192 context** — tight next to Needle + Kokoro on an 8 GB Pi.
9. **Phi-4 can invent facts** — it made up a reporting website once; the scam prompt now forbids it,
   but other answers aren't guarded.
10. **Fine-tuned Needle has no confidence score** (local training can't train it).
11. **GUI not yet tried on a real screen/touchscreen** — tested headless only.
12. **Voice licensing not reviewed** — Piper voices have mixed dataset licences; Kokoro is Apache 2.0.
    Needs checking before selling a product.
13. **GitHub connectivity from this network is intermittent** (pushes sometimes time out; retry later).

---

## 7. Next steps (in priority order)

| # | Task | Why | Effort |
|---|---|---|---|
| 1 | **Replace pocketsphinx with Whisper** (`faster-whisper` base.en, offline), keep pocketsphinx as fallback; rerun the synthetic-voice test + a real mic test | Voice commands are unusable while recognition is this poor | ~half a day |
| 2 | **Pick the Kokoro voice** (A–F) and set it as the default | Product decision | 5 min |
| 3 | **Installer:** add Kokoro + Needle model downloads to `download_model.sh/.ps1`; add voice pip packages to `requirements.txt` and apt packages to `install.sh` | A fresh Pi can't reproduce this setup yet | ~2 h |
| 4 | **Run Guardian on a real screen / touchscreen** and test chat + voice end-to-end with the headset | Only tested headless so far | ~1 h |
| 5 | **Live test scans and checks** on the home network from the Pi | Tools only tested as dry runs | ~1 h |
| 6 | **Collect real family phrasings** (typed + spoken), add them to training + a new unseen test set, **retrain on the cloud GPU** | Only real requests show true accuracy (last clean score 75%) | ongoing |
| 7 | **Route the CLI (`main.py`) through the router** | Consistency | ~1 h |
| 8 | **Lower Phi-4 context to 4096** (or try a smaller LLM for voice) and measure RAM/speed | Memory headroom on 8 GB | ~1 h |
| 9 | **Wake word** ("Hey Guardian") so voice is hands-free | Product feature | ~1 day |
| 10 | **Licence review** (Piper voices, Kokoro, Needle, Phi-4) before any commercial release | Investor/legal readiness | – |
| 11 | Optional: **Cactus platform fine-tune** to keep the confidence head and 2-bit export | Smaller model + usable confidence | paid |
| 12 | Upgrade `cactus-needle` once Cactus publishes engine 3.0.2 | 3.0.5 currently broken | 5 min |

---

## 8. Useful facts learned

- Needle 3's benchmark claims (beats DeepSeek V4 Flash) apply **only after fine-tuning, on narrow
  mobile tool-calling sets**. On Guardian's own tools, raw Needle scored 11/26 — the video's advice to
  test on your own tools was right.
- Needle runs each instance as a separate ~100 MB worker process — use **one shared instance**.
- On a Pi 5, **Phi-4 and a neural voice can't both run at full speed** — they must take turns.
- The Pi's USB headset only accepts 48 kHz; always play through PipeWire, not the raw device.
- `\b` inside a normal (non-raw) Python string becomes a backspace — keep regexes in raw strings.
