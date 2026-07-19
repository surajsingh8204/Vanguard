from __future__ import annotations

import json
import logging
import tempfile
import unittest
from pathlib import Path

from pipeline.orchestrator import PipelineConfig, PipelineOrchestrator, PipelineState


class PipelineOrchestratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = PipelineConfig.load("pipeline/config.yaml")
        self.orchestrator = PipelineOrchestrator(
            self.config,
            logging.getLogger("vanguard.pipeline.tests"),
            dry_run=True,
        )

    def test_streams_json_array_across_read_boundaries(self) -> None:
        records = [
            {"index": index, "content": "x" * 250_000}
            for index in range(9)
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.json"
            path.write_text(json.dumps(records), encoding="utf-8")
            loaded = list(self.orchestrator._iter_json_array(path))
        self.assertEqual(records, loaded)

    def test_state_is_atomic_and_resumable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            state = PipelineState(path)
            state.begin_run()
            state.start_stage("ingestion")
            state.update_stage("ingestion", article_count=500)

            restored = PipelineState(path)
            self.assertEqual("running", restored.stage("ingestion")["status"])
            self.assertEqual(500, restored.stage("ingestion")["article_count"])

    def test_auto_batch_size_respects_configured_bounds(self) -> None:
        batch_size = self.orchestrator._resolve_batch_size("ingestion", 25_000)
        auto = self.config.section("ingestion")["auto_batch"]
        self.assertGreaterEqual(batch_size, auto["minimum"])
        self.assertLessEqual(batch_size, auto["maximum"])


if __name__ == "__main__":
    unittest.main()
