from groq import Groq
import os
from dotenv import load_dotenv
from matplotlib.style import context

load_dotenv()


class RAGEngine:

    def __init__(self):

        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

    def generate(

        self,

        retrieval_context,

        query,

        strategic_context=None

   ):



        print("\n========== RAG DEBUG ==========")
        print("API KEY EXISTS:", bool(os.getenv("GROQ_API_KEY")))
        print("MODEL:", "llama-3.1-8b-instant")
        print("QUERY:", query[:50])
        print("CONTEXT CHARS:", len(retrieval_context))
        print("CONTEXT WORDS:", len(retrieval_context.split()))
        print("===============================\n")


        prompt = f"""
You are a professional intelligence analyst.

PRIMARY EVIDENCE
================

{retrieval_context}

OPTIONAL STRATEGIC SIGNALS
==========================

{strategic_context}

QUESTION
========

{query}

Instructions:

1. Answer using PRIMARY EVIDENCE first.
2. Use STRATEGIC SIGNALS only when directly relevant.
3. Ignore unrelated narratives.
4. Do not force strategic signals into the answer.
5. If evidence is insufficient, say:
   "Insufficient data from retrieved sources."
"""

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content