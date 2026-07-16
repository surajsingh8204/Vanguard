from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Don't touch these folders
SKIP_DIRS = {
    ".git",
    ".github",
    ".vscode",
    ".idea",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".agents",
    "backend",
    "frontend",
    "docker",
    "docs",
    "data_lake",
    "venv",
    ".venv",
}

REPLACEMENTS = {

    # from imports
    "from core.analytics": "from core.analytics",
    "from core.artifacts": "from core.artifacts",
    "from core.clustering": "from core.clustering",
    "from core.config": "from core.config",
    "from core.embeddings": "from core.embeddings",
    "from core.evaluation_logs": "from core.evaluation_logs",
    "from core.experiments": "from core.experiments",
    "from core.ingestion": "from core.ingestion",
    "from core.intelligence": "from core.intelligence",
    "from core.logger": "from core.logger",
    "from core.models": "from core.models",
    "from core.outputs": "from core.outputs",
    "from core.pipeline": "from core.pipeline",
    "from core.processing": "from core.processing",
    "from core.retrieval": "from core.retrieval",
    "from core.utils": "from core.utils",
    "from core.vectorstore": "from core.vectorstore",
    "from core.visualization": "from core.visualization",

    # import imports
    "import core.analytics": "import core.analytics",
    "import core.artifacts": "import core.artifacts",
    "import core.clustering": "import core.clustering",
    "import core.config": "import core.config",
    "import core.embeddings": "import core.embeddings",
    "import core.evaluation_logs": "import core.evaluation_logs",
    "import core.experiments": "import core.experiments",
    "import core.ingestion": "import core.ingestion",
    "import core.intelligence": "import core.intelligence",
    "import core.logger": "import core.logger",
    "import core.models": "import core.models",
    "import core.outputs": "import core.outputs",
    "import core.pipeline": "import core.pipeline",
    "import core.processing": "import core.processing",
    "import core.retrieval": "import core.retrieval",
    "import core.utils": "import core.utils",
    "import core.vectorstore": "import core.vectorstore",
    "import core.visualization": "import core.visualization",
}

updated = 0

for py_file in ROOT.rglob("*.py"):

    if any(part in SKIP_DIRS for part in py_file.parts):
        continue

    text = py_file.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    original = text

    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)

    if text != original:
        py_file.write_text(
            text,
            encoding="utf-8",
        )

        print(f"Updated: {py_file}")

        updated += 1

print("\n" + "=" * 60)
print(f"Updated {updated} Python files")
print("=" * 60)