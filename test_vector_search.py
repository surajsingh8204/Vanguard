from pipeline.main_pipeline import run_pipeline
from models.bert_classifier import BertEmbedder


df, embeddings, vector_store = run_pipeline()

bert = BertEmbedder()

query = "Russia military sanctions"

query_vector = bert.encode_titles([query])[0]

indices, distances = vector_store.search(query_vector, k=5)

print("\nQuery:", query)

print("\nMost similar headlines:\n")

for i in indices:
    print("-", df.iloc[i]["title"])