"""
Iterative LLM Framework

A framework for improving LLM responses through iterative refinement
using evaluator feedback as direct context enhancement.
"""

__version__ = "2.0.0"
__author__ = "Iterative LLM Framework Team"

try:
    from .pipeline import (
        VerifierAgent,
        BugReportReviewer,
        PipelineManager,
        PipelineConfig,
        PipelineResult,
    )
except Exception:  # pragma: no cover - allow partial imports during setup
    VerifierAgent = BugReportReviewer = PipelineManager = PipelineConfig = PipelineResult = None
