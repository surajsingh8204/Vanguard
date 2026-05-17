import os
import shutil

# New architecture folders
folders = [
    "embeddings",
    "vectorstore",
    "retrieval",
    "intelligence",
    "analytics",
    "utils",
    "tests"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

print("Created new architecture folders")

# Move files to new modules
moves = {
    "models/bert_classifier.py": "embeddings/bert_embedder.py",
    "models/vector_store.py": "vectorstore/faiss_store.py",
    "models/narrative_cluster.py": "analytics/narrative_cluster.py",
    "models/llm_engine.py": "intelligence/narrative_llm.py",
}

for src, dst in moves.items():

    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved {src} → {dst}")

print("File restructuring complete")

# Optional cleanup
if os.path.exists("models"):
    print("Old models folder can be removed manually if empty.")