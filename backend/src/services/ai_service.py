"""
AI Service

Loads the Vanguard AI pipeline once and serves queries.
"""

import logging

from core.pipeline.ai_pipeline import AIPipeline

logger = logging.getLogger(__name__)

_pipeline = None


def get_pipeline() -> AIPipeline:
    global _pipeline

    if _pipeline is None:
        logger.info("Initializing Vanguard AI Pipeline...")
        _pipeline = AIPipeline()
        _pipeline.initialize()
        logger.info("Vanguard AI Pipeline Ready.")

    return _pipeline


def ask(question: str):
    """
    Query the AI pipeline.
    """
    pipeline = get_pipeline()
    return pipeline.query(question)
