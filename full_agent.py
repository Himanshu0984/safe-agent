import os
import json
from dotenv import load_dotenv
from groq import Groq
from pii_redactor import redact_pii
from input_guard import is_safe
from cost_tracker import CostTracker
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tracker = CostTracker()

# ===== Load Data =====
# LIVE Gmail API
from gmail_api import fetch_recent_emails
print("📡 Fetching live Gmail data...")
gmail = fetch_recent_emails(max_results=5)
print(f"✅ Loaded {len(gmail)} Gmail emails\n")
    # ===== LIVE notion API =====
from notion_api import fetch_notion_data
print("📡 Fetching live Notion data...")
notion = fetch_notion_data()
print(f"✅ Loaded {len(notion)} Notion pages\n")
with open("mock_data/jira.json") as f:
    jira = json.load(f)

# Build cited context
context = "=== SOURCES ===\n\n"
for i, e in enumerate(gmail):
    context += f"[GMAIL-{i+1}] From {e['from']}, Subject: {e['subject']}\n{e['body']}\n\n"
for i, p in enumerate(notion):
    context += f"[NOTION-{i+1}] {p['page']}: {p['content']}\n\n"
for i, t in enumerate(jira):
    context += f"[JIRA-{i+1}] {t['ticket']}: {t['title']} | Status: {t['status']} | Assignee: {t.get('assignee','?')} | Blocker: {t.get('blocker','None')}\n\n"

# ===== Step 1: Decompose =====
def decompose(question):
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You break a question into EXACTLY 3-4 short sub-questions. "
                    "Rules:\n"
                    "- Return ONLY sub-questions, one per line\n"
                    "- No numbering, no bullets, no explanations\n"
                    "- Each sub-question must end with '?'\n"
                    "- Focus on: goals, tasks, blockers, deadlines, people"
                )
            },
            {"role": "user", "content": f"Question: {question}"}
        ]
    )
    tracker.track(r)  # 💰 NEW LINE
    lines = r.choices[0].message.content.split("\n")
    sub_qs = [line.strip() for line in lines if "?" in line]
    return sub_qs[:4]  # max 4

# ===== Step 2: Answer each sub-question =====
def answer(sub_q):
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Answer only from sources. Cite tag like [GMAIL-1]. Say 'I don't know' if missing."},
            {"role": "user", "content": f"Sources:\n{context}\n\nQuestion: {sub_q}"}
        ]
    )
    tracker.track(r)  # 💰 NEW LINE
    raw_answer = r.choices[0].message.content
    # 🛡️ GUARDRAIL: Redact PII before returning
    return redact_pii(raw_answer)

# ===== Step 3: Synthesize final =====
def synthesize(question, mini_answers):
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Combine these mini-answers into ONE clean summary. Keep citations like [GMAIL-1]."},
            {"role": "user", "content": f"Question: {question}\n\nMini-answers:\n{mini_answers}"}
        ]
    )
    tracker.track(r)  # 💰 NEW LINE
    return r.choices[0].message.content

# ===== RUN THE AGENT =====
big_question = "Summarize my recent emails and highlight any security alerts"

print("🎯 QUESTION:", big_question)

# 🛡️ INPUT GUARDRAIL
print("\n🛡️  Running input guardrail...")
safe, reason = is_safe(big_question)
if not safe:
    print(f"🚨 BLOCKED: {reason}")
    exit()
print("✅ Input is safe, proceeding...\n")
print("\n" + "="*50)

print("\n📋 STEP 1 — DECOMPOSE:")
sub_qs = decompose(big_question)
print(sub_qs)

print("\n🔍 STEP 2 — ANSWER EACH:")
mini = ""
for line in sub_qs:
    if line.strip():
        print(f"\n➡️  {line}")
        a = answer(line)
        print(f"   {a}")
        mini += f"{line}\n{a}\n\n"

print("\n" + "="*50)
print("\n✅ FINAL SUMMARY:\n")
print(synthesize(big_question, mini))
tracker.report()