import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("GROQ_API_KEY nahi mili!")
    exit()

client = Groq(api_key=api_key)

response = client.chat.completions.create(
model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "Explain customer complaint management in one simple sentence."
        }
    ],
)

print(response.choices[0].message.content)