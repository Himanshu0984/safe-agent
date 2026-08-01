import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def decompose_question(big_question):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You break big questions into 3-5 small, specific sub-questions. "
                    "Return ONLY the sub-questions as a numbered list. No explanations."
                )
            },
            {"role": "user", "content": f"Big question: {big_question}"}
        ]
    )
    return response.choices[0].message.content

# Test it
big_q = "Summarize Project X"
print("🧠 Original question:", big_q)
print("\n📋 Sub-questions:\n")
print(decompose_question(big_q))