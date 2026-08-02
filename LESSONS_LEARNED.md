# 🧠 Lessons Learned — Bugs & Fixes

Real problems I hit while building Safe-Agent, and how I solved them.

---

## Bug #1: LLM Classifier was Non-Deterministic

**What happened:**  
My evaluation suite gave different results on the same input. Test 9 
("What is John's phone number?") sometimes blocked, sometimes passed.

**Root cause:**  
The LLM security classifier uses default `temperature=1`, which means 
random sampling — same input can give different outputs.

**Fix:**  
Set `temperature=0` on all classifier calls to make them deterministic.
Also added keyword patterns as a fast, deterministic first-line defense.

**Lesson:**  
LLM-based components need deterministic settings AND rule-based fallbacks 
for anything security-critical.

---

## Bug #2: PII Leaked in Cited Agent (Phone Number in Output)

**What happened:**  
Even with a system prompt saying "redact PII," the model output 
"+91-9876543210" in the final answer.

**Root cause:**  
Prompt-based redaction is unreliable. LLMs don't always follow instructions.

**Fix:**  
Added Microsoft Presidio as a post-processing layer. Every answer passes 
through `redact_pii()` before being returned to the user.

**Lesson:**  
Never trust an LLM to enforce security rules. Use deterministic tools 
as the last line of defense.

---

## Bug #3: Decomposer Hallucinated Unrelated Sub-Questions

**What happened:**  
When I asked "Summarize Project X," the decomposer returned questions 
about "mobile expense apps" — completely unrelated!

**Root cause:**  
The system prompt was too vague ("break into sub-questions"). The LLM 
filled the gap with generic examples.

**Fix:**  
- Tightened the system prompt with strict rules (numbered list, ends with '?')
- Added output parsing that filters lines missing '?'
- Limited to max 4 sub-questions

**Lesson:**  
Vague prompts → creative LLMs → bad outputs. Be explicit and enforce 
structure at parse time.

---

## Bug #4: GitHub Actions Failed on First Run

**What happened:**  
CI pipeline failed with `ModuleNotFoundError: No module named 'input_guard'`.

**Root cause:**  
I accidentally created nested folders (`evaluation/evaluation/run_eval.py`), 
breaking Python's relative imports.

**Fix:**  
- Reorganized folder structure
- Added `sys.path.insert()` in `run_eval.py` to include project root

**Lesson:**  
Always run scripts from project root and set up paths explicitly.

---

## Bug #5: PII Filter Too Aggressive on Assignee Names

**What happened:**  
Presidio redacted "Sarah" and "Mike" (project assignees) as PII, making 
answers less useful.

**Root cause:**  
Presidio treats ALL person names as PII by default.

**Fix (planned):**  
- Maintain a whitelist of internal team members
- Only redact names not in the whitelist

**Lesson:**  
Security guardrails have utility trade-offs. Real systems need 
context-aware filtering.