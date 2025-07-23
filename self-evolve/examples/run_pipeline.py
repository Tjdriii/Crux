#!/usr/bin/env python3
"""Command line interface for the verification pipeline."""
import argparse
import os
from datetime import datetime

from .. import PipelineManager, PipelineConfig
from ..config import FrameworkConfig, ModelConfig, WorkerConfig


def parse_args():
    p = argparse.ArgumentParser(description="Run verification pipeline")
    p.add_argument("--problem_file", required=True, help="Path to problem text")
    p.add_argument("--num_drafts", type=int, default=int(os.getenv("NUM_DRAFTS", 2)))
    p.add_argument("--max_iterations", type=int, default=int(os.getenv("MAX_ITERS", 3)))
    p.add_argument("--verification_runs", type=int, default=int(os.getenv("VERIFICATION_RUNS", 2)))
    p.add_argument("--output_dir", default=os.getenv("OUTPUT_DIR", "pipeline_results"))
    return p.parse_args()


def load_problem(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    args = parse_args()
    problem = load_problem(args.problem_file)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.output_dir, timestamp)
    os.makedirs(out_dir, exist_ok=True)

    models = {
        "verifier": ModelConfig(model_name=os.getenv("VERIFIER_MODEL", "gpt-4")),
        "reviewer": ModelConfig(model_name=os.getenv("REVIEWER_MODEL", "gpt-4")),
    }
    pipeline_cfg = PipelineConfig(
        num_drafts=args.num_drafts,
        max_iterations=args.max_iterations,
        verification_runs=args.verification_runs,
        models=models,
        log_dir=out_dir,
    )

    framework_cfg = FrameworkConfig()
    manager = PipelineManager(pipeline_cfg, framework_cfg)
    result = manager.run(problem)
    if result.accepted:
        print("Proof accepted!")
        with open(os.path.join(out_dir, "accepted_proof.txt"), "w", encoding="utf-8") as f:
            f.write(result.proof or "")
    else:
        print("No proof was accepted.")


if __name__ == "__main__":
    main()
