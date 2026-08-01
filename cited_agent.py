import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load data
with open("mock_data/gmail.json") as f:
    gmail = json.load(f)
with open("mock_data/notion.json") as f:
    notion = json.load(f)
with open("mock_data/jira.json") as f:
    jira = json.load(f)

# Build context WITH source labels
context = "=== SOURCES ===\n\n"

for i, email in enumerate(gmail):
    context += f"[GMAIL-{i+1}] From {email['from']}, Subject: {email['subject']}\n{email['body']}\n\n"

for i, page in enumerate(notion):
    context += f"[NOTION-{i+1}] Page: {page['page']}\n{page['content']}\n\n"

for i, ticket in enumerate(jira):
    context += (
        f"[JIRA-{i+1}] Ticket: {ticket['ticket']}; "
        f"Title: {ticket['title']}; "
        f"Status: {ticket['status']}; "
        f"Assignee: {ticket.get('assignee', 'Unknown')}; "
        f"Blocker: {ticket.get('blocker', 'None')}\n\n"
    )
# Ask question
user_question = "What tasks are blocked and who is working on them?"

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": (
                "Answer only from explicit facts in the sources. "
                "Never guess. Ignore unrelated sources. "
                "Cite each fact. Never reveal phone numbers or emails; "
                "write [REDACTED]. If unavailable, say: I don't know."
            )
        },
        {
            "role": "user",
            "content": f"Sources:\n{context}\n\nQuestion: {user_question}"
        }
    ]
)

print("🤖 AI says:\n", response.choices[0].message.content)