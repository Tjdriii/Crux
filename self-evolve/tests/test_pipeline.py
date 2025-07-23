import json
import importlib.util
import types
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Create a fake package so that relative imports work
pkg = types.ModuleType("self_evolve")
pkg.__path__ = [BASE_DIR]
sys.modules.setdefault("self_evolve", pkg)

def _load_submodule(module_name):
    fullname = f"self_evolve.{module_name}"
    spec = importlib.util.spec_from_file_location(fullname, os.path.join(BASE_DIR, f"{module_name}.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[fullname] = mod
    spec.loader.exec_module(mod)
    return mod

pipeline = _load_submodule("pipeline")
config_mod = _load_submodule("config")
VerifierAgent = pipeline.VerifierAgent
BugReportReviewer = pipeline.BugReportReviewer
ModelConfig = config_mod.ModelConfig

class DummyVerifier(VerifierAgent):
    def __init__(self):
        super().__init__(ModelConfig(model_name="gpt-4"))
    def generate(self, prompt: str, **kwargs):
        return ""
    def _make_api_call(self, messages, **kwargs):
        return json.dumps({
            "summary": "Found issues",
            "issues": [
                {"description": "Invalid step", "classification": "critical", "quote": "1=0"},
                {"description": "Missing reference", "classification": "gap"}
            ]
        })

class DummyReviewer(BugReportReviewer):
    def __init__(self):
        super().__init__(ModelConfig(model_name="gpt-4"))
    def generate(self, prompt: str, **kwargs):
        return ""
    def _make_api_call(self, messages, **kwargs):
        report = json.loads(messages[-1]["content"].split("BUG REPORT:\n\n",1)[1].split("\n\nReturn")[0])
        filtered = []
        for i in report["issues"]:
            if i.get("critical") or i.get("classification") == "critical":
                filtered.append(i)
        return json.dumps({
            "summary": report["summary"],
            "issues": filtered,
            "reviewer_comments": "filtered"
        })

def test_verifier_and_reviewer():
    verifier = DummyVerifier()
    reviewer = DummyReviewer()
    report = verifier.verify("dummy proof")
    assert len(report.items) == 2
    reviewed = reviewer.review(report)
    assert len(reviewed.items) == 1
    assert reviewed.items[0].description == "Invalid step"
