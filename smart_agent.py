import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load all mock data
with open("mock_data/gmail.json") as f:
    gmail = json.load(f)
with open("mock_data/notion.json") as f:
    notion = json.load(f)
with open("mock_data/jira.json") as f:
    jira = json.load(f)

# Combine all data into one big text
context = f"""
GMAIL DATA:
{json.dumps(gmail, indent=2)}

NOTION DATA:
{json.dumps(notion, indent=2)}

JIRA DATA:
{json.dumps(jira, indent=2)}
"""

# User's question
user_question = "What's for lunch today?"

# Send data + question to AI
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Answer ONLY using the provided data."},
        {"role": "user", "content": f"Data:\n{context}\n\nQuestion: {user_question}"}
    ]
)

print("🤖 AI says:\n", response.choices[0].message.content)