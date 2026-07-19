from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

import numpy as np
from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)


class EmbeddingService:

    def __init__(
        self,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        *,
        batch_size=32,
        device=None,
        checkpoint_dir=None,
        save_every_batch=False,
    ):

        print("Loading embedding model...")

        if batch_size <= 0:
            raise ValueError("embedding batch_size must be greater than zero")

        self.model_name = model_name
        self.batch_size = int(batch_size)
        self.checkpoint_dir = Path(checkpoint_dir) if checkpoint_dir else None
        self.save_every_batch = bool(save_every_batch)
        self.model = SentenceTransformer(
            model_name,
            device=None if device in (None, "auto") else device,
        )

    def embed(self, texts):

        texts = list(texts)
        if not texts:
            return np.empty((0, self.model.get_sentence_embedding_dimension()))

        if not self.save_every_batch or self.checkpoint_dir is None:
            return self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=len(texts) > self.batch_size,
            )

        return self._embed_with_checkpoints(texts)

    def _embed_with_checkpoints(self, texts):
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        fingerprint = self._fingerprint(texts)
        manifest_path = self.checkpoint_dir / "manifest.json"
        manifest = self._load_manifest(manifest_path)

        if (
            manifest.get("fingerprint") != fingerprint
            or manifest.get("batch_size") != self.batch_size
            or manifest.get("model_name") != self.model_name
        ):
            self._clear_checkpoint_batches()
            manifest = {
                "fingerprint": fingerprint,
                "model_name": self.model_name,
                "batch_size": self.batch_size,
                "total_texts": len(texts),
                "completed_batches": [],
            }
            self._write_manifest(manifest_path, manifest)

        completed = set(manifest.get("completed_batches", []))
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size
        embeddings = []

        for batch_index in range(total_batches):
            batch_number = batch_index + 1
            batch_path = self.checkpoint_dir / f"batch_{batch_number:06d}.npy"
            start = batch_index * self.batch_size
            batch = texts[start:start + self.batch_size]

            if batch_number in completed and batch_path.exists():
                batch_embeddings = np.load(batch_path, allow_pickle=False)
                logger.info(
                    "Embedding batch %s / %s restored from checkpoint",
                    batch_number,
                    total_batches,
                )
            else:
                batch_embeddings = self.model.encode(
                    batch,
                    batch_size=self.batch_size,
                    show_progress_bar=False,
                )
                self._write_numpy(batch_path, np.asarray(batch_embeddings))
                completed.add(batch_number)
                manifest["completed_batches"] = sorted(completed)
                self._write_manifest(manifest_path, manifest)
                logger.info(
                    "Embedding batch %s / %s completed (%s / %s texts)",
                    batch_number,
                    total_batches,
                    min(start + len(batch), len(texts)),
                    len(texts),
                )

            embeddings.append(np.asarray(batch_embeddings))

        return np.concatenate(embeddings, axis=0)

    def _fingerprint(self, texts):
        digest = hashlib.sha256()
        digest.update(self.model_name.encode("utf-8"))
        for text in texts:
            encoded = str(text).encode("utf-8", errors="replace")
            digest.update(len(encoded).to_bytes(8, "big"))
            digest.update(encoded)
        return digest.hexdigest()

    def _load_manifest(self, path):
        if not path.exists():
            return {}
        try:
            with path.open("r", encoding="utf-8") as handle:
                value = json.load(handle)
            return value if isinstance(value, dict) else {}
        except (OSError, json.JSONDecodeError):
            logger.warning("Ignoring invalid embedding checkpoint manifest: %s", path)
            return {}

    def _write_manifest(self, path, manifest):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = path.with_suffix(".tmp")
        with temporary_path.open("w", encoding="utf-8") as handle:
            json.dump(manifest, handle, indent=2)
            handle.write("\n")
        temporary_path.replace(path)

    def _write_numpy(self, path, value):
        with NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            suffix=".npy",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            np.save(handle, value, allow_pickle=False)
        temporary_path.replace(path)

    def _clear_checkpoint_batches(self):
        for path in self.checkpoint_dir.glob("batch_*.npy"):
            path.unlink(missing_ok=True)
