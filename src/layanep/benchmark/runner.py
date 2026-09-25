"""Benchmark runner: scores a classifier against the frozen ne-probe-v1 corpus.

Classifiers:
- ``stub``  always abstains (CI smoke, no weights);
- ``laya``  in-process Laya (``Agent.system_one``) with the natural-criteria
  choice question that measured best in the OrderWorkFlow probe;
- any callable in tests (oracle, failing, ...).

Metrics are model-only: accuracy, abstain accuracy, per-kind recall, latency
p50/p95, classifier errors. The composite/gap metrics from OrderWorkFlow need
the deterministic dialogue classifier and are intentionally out of scope here.
"""

from __future__ import annotations

import argparse
import math
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping, Sequence

from ..pins import MODEL_REPO, MODEL_REVISION, MULTILINGUAL_SUBFOLDER
from ..questions import COMMAND_LABEL_TO_KIND, command_question
from ..schema import LU_COMMAND_KINDS
from ..transliterate import detect_language
from .corpus import (
    BENCHMARK_REVISION,
    DEFAULT_CORPUS_PATH,
    ProbeCorpus,
    ProbeStep,
    load_corpus,
    validate_corpus,
)
from .report import build_report_json, build_report_markdown

REPO_ROOT = Path(__file__).resolve().parents[3]
REPORTS_DIR = REPO_ROOT / "reports"

ProbeClassifier = Callable[[ProbeStep, Mapping], "str | None"]


@dataclass(frozen=True)
class StepResult:
    case_id: str
    step_id: str
    language: str
    text: str
    expected: str | None
    predicted: str | None
    latency_ms: float | None
    error: str | None


@dataclass(frozen=True)
class KindStats:
    expected: int
    correct: int
    predicted: int
    false_positive: int


@dataclass(frozen=True)
class ProbeScore:
    classifier: str
    revision: str
    total: int
    correct: int
    abstain_total: int
    abstain_correct: int
    per_kind: Mapping[str, KindStats]
    latency_p50: float | None
    latency_p95: float | None
    errors: int
    results: tuple[StepResult, ...]


def stub_classifier(step: ProbeStep, business: Mapping) -> str | None:
    return None


def oracle_classifier(step: ProbeStep, business: Mapping) -> str | None:
    return step.expected


def _pinned_model_path(subfolder: str | None) -> str:
    """Local snapshot path for the pinned revision, else the repo id.

    ``laya.load`` has no ``revision`` argument, so the pin is enforced by
    loading the cached snapshot directory directly; when the snapshot is
    absent we fall back to the hub id (which downloads the current main).
    """
    cache_root = Path.home() / ".cache" / "huggingface" / "hub"
    try:
        from huggingface_hub import constants

        cache_root = Path(constants.HF_HUB_CACHE)
    except Exception:  # noqa: BLE001 - the pin is best-effort; loading is not
        pass
    snapshot = cache_root / f"models--{MODEL_REPO.replace('/', '--')}" / "snapshots" / MODEL_REVISION
    candidate = snapshot / subfolder if subfolder else snapshot
    return str(candidate) if candidate.is_dir() else MODEL_REPO


def laya_classifier(
    *,
    device: str | None = None,
    threshold: float = 0.5,
    threads: int | None = None,
) -> ProbeClassifier:
    import laya  # lazy: deterministic gates must never require the model extra

    if threads:
        import torch

        torch.set_num_threads(threads)
        torch.set_num_interop_threads(1)

    agent_en = laya.load(_pinned_model_path(None), device=device)
    agent_ml = laya.load(_pinned_model_path(MULTILINGUAL_SUBFOLDER), device=device)

    def classify(step: ProbeStep, business: Mapping) -> str | None:
        agent = agent_ml if detect_language(step.text) == "ne" else agent_en
        questions = {"command": command_question(str(business["name"])).to_dict()}
        result = agent.system_one({"body": step.text}, questions)
        answer = result["answers"]["command"]
        label = answer.get("choice")
        confidence = answer.get("answer_confidence", answer.get("confidence", 0.0))
        if not label or label == "none" or float(confidence) < threshold:
            return None
        kind = COMMAND_LABEL_TO_KIND.get(label)
        if kind is None:
            raise ValueError(f"unmapped Laya label {label!r}")
        return kind

    return classify


def run_probe(classifier: ProbeClassifier, corpus: ProbeCorpus, *, delay_ms: int = 0) -> list[StepResult]:
    results: list[StepResult] = []
    first = True
    for case in corpus.cases:
        business = corpus.business(case.menu_id)
        for step in case.steps:
            if delay_ms and not first:
                time.sleep(delay_ms / 1000)
            first = False
            predicted: str | None = None
            latency_ms: float | None = None
            error: str | None = None
            try:
                started = time.perf_counter()
                predicted = classifier(step, business)
                latency_ms = (time.perf_counter() - started) * 1000
                if predicted is not None and predicted not in LU_COMMAND_KINDS:
                    error = f"classifier returned unknown kind {predicted!r}"
                    predicted = None
            except Exception as exc:  # noqa: BLE001 - per-step failures are recorded, not raised
                error = f"{type(exc).__name__}: {exc}"
                predicted = None
            results.append(
                StepResult(
                    case_id=case.id,
                    step_id=step.id,
                    language=step.language,
                    text=step.text,
                    expected=step.expected,
                    predicted=predicted,
                    latency_ms=latency_ms,
                    error=error,
                )
            )
    return results


def _percentile(values: Sequence[float], percent: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(percent / 100 * len(ordered)) - 1))
    return ordered[index]


def score_probe(classifier: str, corpus: ProbeCorpus, results: Sequence[StepResult]) -> ProbeScore:
    counters = {
        key: {"expected": 0, "correct": 0, "predicted": 0, "false_positive": 0}
        for key in (*LU_COMMAND_KINDS, "none")
    }
    for result in results:
        expected_key = result.expected or "none"
        predicted_key = result.predicted or "none"
        counters[expected_key]["expected"] += 1
        counters[predicted_key]["predicted"] += 1
        if expected_key == predicted_key:
            counters[expected_key]["correct"] += 1
        else:
            counters[predicted_key]["false_positive"] += 1

    latencies = [result.latency_ms for result in results if result.latency_ms is not None]
    return ProbeScore(
        classifier=classifier,
        revision=corpus.revision,
        total=len(results),
        correct=sum(1 for result in results if result.predicted == result.expected),
        abstain_total=sum(1 for result in results if result.expected is None),
        abstain_correct=sum(1 for result in results if result.expected is None and result.predicted is None),
        per_kind={key: KindStats(**counts) for key, counts in counters.items()},
        latency_p50=_percentile(latencies, 50),
        latency_p95=_percentile(latencies, 95),
        errors=sum(1 for result in results if result.error),
        results=tuple(results),
    )


def _current_commit() -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return completed.stdout.strip() or None
    except Exception:  # noqa: BLE001 - a missing git checkout is not a failure
        return None


def _print_summary(score: ProbeScore) -> None:
    def rate(correct: int, total: int) -> str:
        return "n/a" if total == 0 else f"{correct / total * 100:.1f}%"

    def ms(value: float | None) -> str:
        return "n/a" if value is None else f"{value:.1f}ms"

    print(
        f"ne-probe [{score.classifier}]: {score.total} steps | "
        f"model {score.correct}/{score.total} ({rate(score.correct, score.total)}) | "
        f"abstain {score.abstain_correct}/{score.abstain_total} | "
        f"p50 {ms(score.latency_p50)} p95 {ms(score.latency_p95)} | "
        f"errors {score.errors}"
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the ne-probe-v1 benchmark.")
    parser.add_argument("--classifier", choices=("stub", "laya"), default="stub")
    parser.add_argument("--corpus", type=Path, default=None, help="corpus JSON (default data/benchmark/ne-probe-v1.json)")
    parser.add_argument("--device", default=None, help="Laya device (cpu, cuda, mps); default auto")
    parser.add_argument("--threshold", type=float, default=0.5, help="answer-confidence gate")
    parser.add_argument("--threads", type=int, default=None, help="torch intra-op threads for CPU runs")
    parser.add_argument("--delay-ms", type=int, default=0, help="pause between model steps")
    parser.add_argument("--no-write", action="store_true", help="print without writing reports/")
    args = parser.parse_args(argv)

    corpus_path = args.corpus or DEFAULT_CORPUS_PATH
    corpus = load_corpus(corpus_path)
    failures = validate_corpus(corpus)
    if failures:
        print("corpus INVALID:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    if args.classifier == "laya":
        classifier = laya_classifier(device=args.device, threshold=args.threshold, threads=args.threads)
    else:
        classifier = stub_classifier

    results = run_probe(classifier, corpus, delay_ms=args.delay_ms)
    score = score_probe(args.classifier, corpus, results)
    _print_summary(score)

    if not args.no_write:
        stem = (
            f"ne-probe-{args.classifier}"
            if corpus.revision == BENCHMARK_REVISION
            else f"{corpus.revision}-{args.classifier}"
        )
        meta = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "classifier": args.classifier,
            "corpus": str(corpus_path),
            "corpus_revision": corpus.revision,
            "commit": _current_commit(),
            "device": args.device or "auto",
            "threshold": args.threshold,
            "threads": args.threads,
        }
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        (REPORTS_DIR / f"{stem}.md").write_text(build_report_markdown(meta, score), encoding="utf-8")
        (REPORTS_DIR / f"{stem}.json").write_text(build_report_json(meta, score), encoding="utf-8")
        print(f"report: reports/{stem}.{{md,json}}")
    return 1 if score.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
