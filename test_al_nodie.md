S C:\Users\works\Downloads\guardian_node_clean> python guardian_interpreter/test_gemma2_llm.py

============================================================
Guardian Node - Gemma 2 2B LLM Test Suite
============================================================
============================================================
Test 1: Loading Gemma 2 2B Model
============================================================
Model path: C:\Users\works\Downloads\guardian_node_clean\guardian_interpreter\models\gemma-2-2b-it-Q4_K_M.gguf
Context length: 8192
Threads: 4
Model size: 1.59 GB

Loading model...
llama_kv_cache_unified_iswa: using full-size SWA cache (ref: https://github.com/ggml-org/llama.cpp/pull/13194#issuecomment-2868343055)
✓ Model loaded successfully in 1.00 seconds

============================================================
Test 2: Gemma 2 2B Inference Test
============================================================

Security Question:
------------------------------------------------------------
C:\Users\works\AppData\Local\Programs\Python\Python310\lib\site-packages\llama_cpp\llama.py:1242: RuntimeWarning: Detected duplicate leading "<bos>" in prompt, this will likely reduce response quality, consider removing it...
  warnings.warn(
Response: While predicting the future is always tricky, here are 3 cybersecurity threats families should be particularly concerned about in 2024, based on current trends and expert analysis:

**1. AI-Powered Attacks:**

* **Description:**  Artificial Intelligence (AI) is becoming increasingly sophisticated, and malicious actors are leveraging it to automate attacks with greater speed, scale, and sophistication. Think of AI-powered phishing campaigns that adapt to individual user behavior, or ransomware strains that exploit vulnerabilities with uncanny efficiency.
* **Impact:** Increased complexity of attacks, hard to detect, and potentially devastating damage.
* **Examples:**  AI-generated malware, sophisticated phishing campaigns using AI-driven persona impersonation, targeted attacks exploiting AI-powered vulnerabilities.

**2. Supply Chain Attacks:**

* **Description:**  Attackers are increasingly targeting the supply chains of individuals and organizations. This involves infiltrating or manipulating a company's systems through compromised software, hardware, or third-party vendors. Think of an attack exploiting a vulnerability in a popular cloud service or an IoT device.
* **Impact:**  Disruption of essential services, compromised data, and potentially cascading failures impacting other systems.
* **Examples:**  Ransomware attacks exploiting vulnerabilities
Time: 10.57s | Tokens: 256 | Speed: 24.2 tok/s

Child Safety:
------------------------------------------------------------
Response: ##  Keeping Kids Safe Online: A Guide for Parents

The internet offers a world of opportunities for learning and connection, but it also comes with inherent dangers.  Here's a comprehensive guide to help parents navigate the online world with their children:

**1. Open Communication is Key:**

* **Talk about online risks:** Explain the dangers of cyberbullying, online predators, privacy breaches, and inappropriate content in age-appropriate terms.
* **Establish a safe space:** Create an open dialogue where children feel comfortable discussing any online concerns they might have.
* **Active Listening:**  Listen to their experiences without judgment, and let them know it's okay to ask for help.

**2. Set Clear Rules & Boundaries:**

* **Digital well-being:** Establish screen time limits, dedicated tech-free zones, and set expectations for device use. 
* **Privacy:** Discuss what information is personal and what is acceptable to share online. Explain the importance of strong passwords and recognizing phishing scams.
* **Age-appropriate content:** Set guidelines for content consumption, and monitor their activity using parental controls.

**3. Utilize Parental Controls & Tools:**

* **Device restrictions:** Many devices offer parental control features like website filtering
Time: 10.46s | Tokens: 256 | Speed: 24.5 tok/s

Guardian Node Introduction:
------------------------------------------------------------
Response: Hello! I'm Guardian Node, your family's cybersecurity protector, here to keep your digital world safe and secure.
Time: 1.30s | Tokens: 27 | Speed: 20.7 tok/s

============================================================
Test 3: Memory Usage Comparison
============================================================

Phi-3 Mini (old):
  Size: 2.23 GB
  Context: 4096 tokens

Gemma 2 2B (new):
  Size: 1.59 GB
  Context: 8192 tokens
  Savings: 653 MB smaller than Phi-3

============================================================
Test Summary
============================================================

Model Loading: ✓ PASSED
Security Question: ✓ PASSED (24.2 tok/s)
Child Safety: ✓ PASSED (24.5 tok/s)
Guardian Node Introduction: ✓ PASSED (20.7 tok/s)

============================================================
Total: 4/4 tests passed
✓ All tests PASSED! Gemma 2 2B is ready for production.
============================================================
PS C:\Users\works\Downloads\guardian_node_clean> python guardian_interpreter/test_voice.py
==================================================
Guardian Node Voice Interface Test
==================================================
Testing male voice (espeak-ng)...
✗ Male voice test FAILED: [WinError 2] The system cannot find the file specified

Testing female voice (espeak-ng)...
✗ Female voice test FAILED: [WinError 2] The system cannot find the file specified

Available voices:
✗ Failed to list voices: [WinError 2] The system cannot find the file specified

==================================================
Test Summary:
==================================================
Male Voice: ✗ FAILED
Female Voice: ✗ FAILED
Voice List: ✗ FAILED

✗ Some voice tests FAILED
PS C:\Users\works\Downloads\guardian_node_clean> python guardian_interpreter/main.py
Warning: Could not import Guardian components: No module named 'guardian_interpreter'
🛡️ Starting Guardian Node...
💻 Running in CLI mode...
WARNING:guardian:Guardian CLI initialized with fallback manager
Guardian Family Assistant CLI. Type 'help' for commands.
guardian-family>