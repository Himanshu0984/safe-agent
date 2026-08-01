import os
from dotenv import load_dotenv
from groq import Groq

# Load API key from .env file
load_dotenv()

# Create Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Ask the AI something
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": "Say hello in one sentence!"}
    ]
)

# Print the AI's answer
print("🤖 AI says:", response.choices[0].message.content)