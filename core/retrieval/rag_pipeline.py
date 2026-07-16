from langchain_core.prompts import PromptTemplate
from langchain import LLMChain
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatGroq


class NarrativeRAG:

    def __init__(self, vector_store):

        self.vector_store = vector_store

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.llm = ChatGroq(
            model="llama3-70b-8192"
        )

        template = """
You are a geopolitical intelligence analyst.

Context:
{context}

Question:
{question}

Provide a narrative analysis including:
- main narrative
- actors involved
- possible geopolitical implications
"""

        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=template
        )

        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt
        )

    def analyze(self, query):

        docs = self.vector_store.similarity_search(query, k=5)

        context = "\n".join([d.page_content for d in docs])

        return self.chain.run({
            "context": context,
            "question": query
        })