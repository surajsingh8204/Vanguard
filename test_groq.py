import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

headlines = [
    "Iran threatens closure of Strait of Hormuz",
    "Oil prices surge amid Middle East tensions",
    "US deploys additional naval forces to Gulf",
    "European leaders warn of energy supply disruptions"
]

prompt = f"""
Analyze the following headlines and summarize the narrative:

{chr(10).join(headlines)}
"""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

print(response.choices[0].message.content)