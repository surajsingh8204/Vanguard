from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()


class RAGEngine:

    def __init__(self):

        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

    def generate(self, context, query):

        prompt = f"""
You MUST answer ONLY from the provided context.
Do NOT use external knowledge.

Context:
{context}

Question:
{query}

If answer not found in context, say:
"Insufficient data from retrieved sources."
"""

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content