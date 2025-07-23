"""Verification pipeline integrating Self-Evolve agents with verifier and reviewer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json
import os
import time
import logging

from .models.base_model import BaseModel
from .models.professor_model import ProfessorModel
from .models.evaluator_model import EvaluatorModel
from .models.graduate_worker import GraduateWorker
from .config import FrameworkConfig, WorkerConfig, ModelConfig
from .utils import setup_logging, get_logger


@dataclass
class BugReportItem:
    """Single issue found by the verifier."""
    description: str
    critical: bool  # True if critical error, False if gap/minor
    quote: Optional[str] = None


@dataclass
class BugReport:
    """Bug report produced by the verifier."""
    summary: str
    items: List[BugReportItem] = field(default_factory=list)
    raw_log: Optional[str] = None


@dataclass
class ReviewedReport:
    """Bug report after reviewer passes."""
    summary: str
    items: List[BugReportItem] = field(default_factory=list)
    reviewer_comments: Optional[str] = None


class VerifierAgent(BaseModel):
    """LLM-based verifier that inspects a proof and reports issues."""

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.logger = get_logger(self.__class__.__name__)

    def verify(self, proof_text: str, **kwargs) -> BugReport:
        instructions = (
            "You are a meticulous mathematical proof verifier. "
            "Read the provided proof in LaTeX format and output a JSON bug report. "
            "Classify each issue as a 'critical error' if it invalidates the proof, "
            "or as a 'justification gap' for missing reasoning that should be filled."
        )
        user_prompt = f"PROOF:\n\n{proof_text}\n\nReturn a JSON object with fields 'summary' and 'issues'."
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": user_prompt},
        ]
        response = self._make_api_call(messages, temperature=0, stream=False, **kwargs)
        self.logger.debug(f"Verifier raw response: {response}")
        try:
            report_json = json.loads(response)
            items = [
                BugReportItem(
                    description=i.get("description", ""),
                    critical=i.get("classification", "").lower() == "critical",
                    quote=i.get("quote"),
                )
                for i in report_json.get("issues", [])
            ]
            return BugReport(summary=report_json.get("summary", ""), items=items, raw_log=response)
        except Exception as e:
            self.logger.error(f"Failed to parse verifier output: {e}")
            return BugReport(summary="Parsing error", items=[], raw_log=response)


class BugReportReviewer(BaseModel):
    """Agent that filters and comments on bug reports."""

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.logger = get_logger(self.__class__.__name__)

    def review(self, report: BugReport, **kwargs) -> ReviewedReport:
        instructions = (
            "You are a senior mathematician reviewing a bug report from a proof verifier. "
            "Filter out any issues that are obviously spurious or minor. "
            "If an issue is misclassified, correct it. Provide short reviewer comments."
        )
        report_str = json.dumps({
            "summary": report.summary,
            "issues": [
                {"description": i.description, "critical": i.critical, "quote": i.quote}
                for i in report.items
            ]
        }, ensure_ascii=False, indent=2)
        user_prompt = f"BUG REPORT:\n\n{report_str}\n\nReturn corrected JSON with optional 'reviewer_comments'."
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": user_prompt},
        ]
        response = self._make_api_call(messages, temperature=0, stream=False, **kwargs)
        self.logger.debug(f"Reviewer raw response: {response}")
        try:
            data = json.loads(response)
            items = [
                BugReportItem(
                    description=i.get("description", ""),
                    critical=bool(i.get("critical", False)),
                    quote=i.get("quote"),
                )
                for i in data.get("issues", [])
            ]
            return ReviewedReport(
                summary=data.get("summary", report.summary),
                items=items,
                reviewer_comments=data.get("reviewer_comments"),
            )
        except Exception as e:
            self.logger.error(f"Failed to parse reviewer output: {e}")
            return ReviewedReport(summary="Parsing error", items=[], reviewer_comments=str(e))


@dataclass
class PipelineConfig:
    num_drafts: int = 2
    max_iterations: int = 3
    verification_runs: int = 2
    models: Dict[str, ModelConfig] = field(default_factory=dict)
    log_dir: str = "pipeline_logs"


@dataclass
class PipelineResult:
    accepted: bool
    proof: Optional[str]
    logs: Dict[str, Any] = field(default_factory=dict)


class PipelineManager:
    """Orchestrates the full verification pipeline."""

    def __init__(self, config: PipelineConfig, framework_cfg: FrameworkConfig):
        self.config = config
        self.framework_cfg = framework_cfg
        setup_logging(log_level="INFO", json_logs=True)
        self.logger = get_logger(self.__class__.__name__)
        self.verifier = VerifierAgent(config.models.get("verifier", ModelConfig()))
        self.reviewer = BugReportReviewer(config.models.get("reviewer", ModelConfig()))

    def _verify_and_review(self, proof: str) -> ReviewedReport:
        report = self.verifier.verify(proof)
        self.logger.info(json.dumps({"event": "verification", "summary": report.summary}))
        reviewed = self.reviewer.review(report)
        self.logger.info(json.dumps({"event": "review", "summary": reviewed.summary}))
        return reviewed

    def run(self, problem_text: str) -> PipelineResult:
        os.makedirs(self.config.log_dir, exist_ok=True)
        professor = ProfessorModel(self.framework_cfg)
        drafts = []
        for i in range(self.config.num_drafts):
            try:
                session = professor.self_evolve(problem_text, max_iterations=self.framework_cfg.max_iterations)
                drafts.append(session.final_answer)
                with open(os.path.join(self.config.log_dir, f"draft_{i+1}.txt"), "w", encoding="utf-8") as f:
                    f.write(session.final_answer)
            except Exception as e:
                self.logger.error(f"Failed to generate draft {i+1}: {e}")
        for idx, draft in enumerate(drafts, start=1):
            proof = draft
            for iteration in range(self.config.max_iterations):
                reviewed = self._verify_and_review(proof)
                critical_items = [it for it in reviewed.items if it.critical]
                log_path = os.path.join(self.config.log_dir, f"draft_{idx}_iter_{iteration+1}.json")
                with open(log_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "proof": proof,
                        "review": {
                            "summary": reviewed.summary,
                            "issues": [it.__dict__ for it in reviewed.items],
                            "comments": reviewed.reviewer_comments,
                        }
                    }, f, ensure_ascii=False, indent=2)
                if not critical_items:
                    # run additional verification passes
                    passes = 0
                    for _ in range(self.config.verification_runs):
                        final_review = self._verify_and_review(proof)
                        if any(it.critical for it in final_review.items):
                            break
                        passes += 1
                    if passes == self.config.verification_runs:
                        return PipelineResult(accepted=True, proof=proof)
                    # else continue loop with new issues
                # Construct refinement prompt
                bug_text = "\n".join(f"- {'CRITICAL' if it.critical else 'GAP'}: {it.description}" for it in critical_items)
                refine_prompt = f"The verifier found the following issues:\n{bug_text}\nPlease correct the proof while keeping valid parts." 
                worker = GraduateWorker(self.framework_cfg, worker_id=f"{idx}_{iteration}")
                result = worker.solve_specialized_task("proof repair", refine_prompt)
                proof = result.get("final_answer", proof)
            self.logger.info(f"Draft {idx} exhausted without acceptance")
        return PipelineResult(accepted=False, proof=None)

