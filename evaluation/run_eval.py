import os
import sys
import json
import time

# Add parent folder to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from input_guard import is_safe
from pii_redactor import redact_pii
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ===== Load test cases =====
with open("evaluation/datasets/test_cases.json") as f:
    test_cases = json.load(f)

# ===== Load mock data (same as agent) =====
with open("mock_data/gmail.json") as f:
    gmail = json.load(f)
with open("mock_data/notion.json") as f:
    notion = json.load(f)
with open("mock_data/jira.json") as f:
    jira = json.load(f)

context = "=== SOURCES ===\n\n"
for i, e in enumerate(gmail):
    context += f"[GMAIL-{i+1}] From {e['from']}, Subject: {e['subject']}\n{e['body']}\n\n"
for i, p in enumerate(notion):
    context += f"[NOTION-{i+1}] {p['page']}: {p['content']}\n\n"
for i, t in enumerate(jira):
    context += f"[JIRA-{i+1}] {t['ticket']}: {t['title']} | Status: {t['status']} | Assignee: {t.get('assignee','?')} | Blocker: {t.get('blocker','None')}\n\n"


def ask_agent(question):
    """Simplified agent for evaluation."""
    # Guardrail check
    safe, reason = is_safe(question)
    if not safe:
        return {"blocked": True, "answer": f"BLOCKED: {reason}"}
    
    # Answer
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Answer only from sources. Cite [GMAIL-1] etc. Say 'I don't know' if missing."},
            {"role": "user", "content": f"Sources:\n{context}\n\nQuestion: {question}"}
        ]
    )
    raw = r.choices[0].message.content
    clean = redact_pii(raw)
    return {"blocked": False, "answer": clean}


# ===== RUN EVALUATION =====
print("🧪 Running Evaluation Suite\n" + "="*60)

results = {"pass": 0, "fail": 0, "details": []}
total_latency = 0

for tc in test_cases:
    print(f"\n[Test {tc['id']}] ({tc['category']}) {tc['question'][:60]}")
    
    start = time.time()
    result = ask_agent(tc["question"])
    latency = time.time() - start
    total_latency += latency
    
    answer = result["answer"]
    blocked = result["blocked"]
    
    # Check pass/fail
    failures = []
    
    # Check: should this be blocked?
    if tc["should_be_blocked"] and not blocked:
        failures.append("Should have been blocked but wasn't")
    if not tc["should_be_blocked"] and blocked:
        failures.append("Blocked but should have been allowed")
    
    # Check: must_contain
    for keyword in tc["must_contain"]:
        if keyword.lower() not in answer.lower():
            failures.append(f"Missing keyword: '{keyword}'")
    
    # Check: must_not_contain
    for keyword in tc["must_not_contain"]:
        if keyword.lower() in answer.lower():
            failures.append(f"Leaked keyword: '{keyword}'")
    
    # Report
    if failures:
        results["fail"] += 1
        print(f"   ❌ FAIL ({latency:.1f}s)")
        for f in failures:
            print(f"      → {f}")
    else:
        results["pass"] += 1
        print(f"   ✅ PASS ({latency:.1f}s)")
    
    results["details"].append({
        "id": tc["id"],
        "passed": len(failures) == 0,
        "failures": failures,
        "latency": round(latency, 2)
    })


# ===== FINAL REPORT =====
total = len(test_cases)
accuracy = (results["pass"] / total) * 100
avg_latency = total_latency / total

print("\n" + "="*60)
print("📊 FINAL REPORT")
print("="*60)
print(f"✅ Passed:      {results['pass']}/{total}")
print(f"❌ Failed:      {results['fail']}/{total}")
print(f"🎯 Accuracy:    {accuracy:.1f}%")
print(f"⏱️  Avg Latency: {avg_latency:.2f}s")
print("="*60)

# Save report
with open("evaluation/last_report.json", "w") as f:
    json.dump({
        "accuracy": accuracy,
        "passed": results["pass"],
        "failed": results["fail"],
        "avg_latency": avg_latency,
        "details": results["details"]
    }, f, indent=2)

print("\n💾 Report saved to evaluation/last_report.json")