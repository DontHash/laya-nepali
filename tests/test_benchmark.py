"""Benchmark corpus, scoring, reports, and the ported transliterator."""

from __future__ import annotations

from pathlib import Path

from layanep.benchmark.corpus import BENCHMARK_REVISIONS, load_corpus, validate_corpus
from layanep.benchmark.report import build_report_json, build_report_markdown
from layanep.benchmark.runner import (
    StepPrediction,
    oracle_classifier,
    run_probe,
    score_probe,
    stub_classifier,
)
from layanep.domains.clothing.questions import (
    CLOTHING_COMMAND_LABEL_TO_KIND,
    CLOTHING_LU_COMMAND_KINDS,
)
from layanep.glossary import ORDERING_DICT
from layanep.schema import LU_COMMAND_KINDS
from layanep.transliterate import detect_language, transliterate_to_devanagari

DEVA_V2_PATH = Path(__file__).resolve().parents[1] / "data" / "benchmark" / "ne-bench-deva-v2.json"
CL_BENCH_PATH = Path(__file__).resolve().parents[1] / "data" / "benchmark" / "cl-bench-v1.json"


def test_corpus_is_valid() -> None:
    corpus = load_corpus()
    assert validate_corpus(corpus) == []
    assert corpus.revision in BENCHMARK_REVISIONS
    assert len(corpus.steps) >= 60


def test_deva_v2_corpus_is_valid() -> None:
    corpus = load_corpus(DEVA_V2_PATH)
    assert validate_corpus(corpus) == []
    assert corpus.revision == "ne-bench-deva-v2"
    assert {step.language for step in corpus.steps} == {"ne"}
    assert len(corpus.steps) >= 220
    abstain = [step for step in corpus.steps if step.expected is None]
    assert len(abstain) >= 60
    assert len({case.menu_id for case in corpus.cases}) == 2
    covered = {step.expected for step in corpus.steps if step.expected}
    assert set(LU_COMMAND_KINDS) <= covered


def test_corpus_covers_the_vocabulary() -> None:
    corpus = load_corpus()
    expected = {step.expected for step in corpus.steps if step.expected}
    assert set(LU_COMMAND_KINDS) <= expected
    languages = {step.language for step in corpus.steps}
    assert languages == {"en", "ne-rom", "ne"}


def test_cl_bench_corpus_is_valid() -> None:
    corpus = load_corpus(CL_BENCH_PATH)
    assert validate_corpus(corpus) == []
    assert corpus.revision == "cl-bench-v1"
    assert len(corpus.steps) >= 800
    abstain = [step for step in corpus.steps if step.expected is None]
    assert len(abstain) >= 250
    covered = {step.expected for step in corpus.steps if step.expected}
    assert set(CLOTHING_LU_COMMAND_KINDS) <= covered
    assert {step.language for step in corpus.steps} == {"en", "ne-rom", "ne"}


def test_prediction_confidence_scores_ece_and_unsafe() -> None:
    corpus = load_corpus(CL_BENCH_PATH)

    def perfect(step, business):
        del business
        if step.expected is None:
            return StepPrediction(None, confidence=0.99, p_none=0.9)
        return StepPrediction(step.expected, confidence=0.9, p_none=0.001)

    score = score_probe("perfect", corpus, run_probe(perfect, corpus))
    assert score.correct == score.total
    assert score.unsafe == 0
    assert score.ece is not None
    assert 0.05 <= score.ece <= 0.15  # always right at confidence 0.9


def test_unsafe_counts_false_commands_on_abstain_steps() -> None:
    corpus = load_corpus(CL_BENCH_PATH)

    def trigger(step, business):
        del step, business
        return StepPrediction("social.greet", confidence=0.99, p_none=0.01)

    score = score_probe("trigger", corpus, run_probe(trigger, corpus))
    assert score.unsafe == score.abstain_total


def test_policy_simulation_flags_unsafe_auto_serves() -> None:
    corpus = load_corpus(CL_BENCH_PATH)
    kind_to_label = {kind: label for label, kind in CLOTHING_COMMAND_LABEL_TO_KIND.items()}

    def honest(step, business):
        del business
        if step.expected is None:
            return StepPrediction(None, confidence=0.99, p_none=0.9, label=None, needs_staff=False, abstain=True)
        return StepPrediction(
            step.expected,
            confidence=0.95,
            p_none=0.01,
            label=kind_to_label[step.expected],
            needs_staff=False,
            abstain=False,
        )

    safe = score_probe("honest", corpus, run_probe(honest, corpus), policy_domain="clothing")
    assert safe.auto_served > 0
    assert safe.unsafe_auto == 0

    def overtrigger(step, business):
        del step, business
        return StepPrediction("social.greet", 0.99, 0.01, "greet", False, False)

    risky = score_probe("overtrigger", corpus, run_probe(overtrigger, corpus), policy_domain="clothing")
    assert risky.auto_served == risky.total
    assert risky.unsafe_auto >= risky.abstain_total


def test_oracle_scores_100_percent() -> None:
    corpus = load_corpus()
    score = score_probe("oracle", corpus, run_probe(oracle_classifier, corpus))
    assert score.correct == score.total
    assert score.errors == 0


def test_stub_scores_only_abstains() -> None:
    corpus = load_corpus()
    score = score_probe("stub", corpus, run_probe(stub_classifier, corpus))
    assert score.correct == score.abstain_correct
    assert score.abstain_correct == score.abstain_total
    assert score.errors == 0


def test_errors_are_recorded_per_step() -> None:
    corpus = load_corpus()

    def failing(step, business):
        raise RuntimeError("provider down")

    score = score_probe("failing", corpus, run_probe(failing, corpus))
    assert score.errors == score.total


def test_unknown_kind_is_an_error() -> None:
    corpus = load_corpus()
    score = score_probe("mutating", corpus, run_probe(lambda step, business: "ordering.add_item", corpus))
    assert score.errors == score.total


def test_report_renders() -> None:
    corpus = load_corpus()
    score = score_probe("oracle", corpus, run_probe(oracle_classifier, corpus))
    meta = {
        "generated_at": "2026-09-24T00:00:00Z",
        "classifier": "oracle",
        "commit": "test",
        "device": "cpu",
        "threshold": 0.5,
    }
    markdown = build_report_markdown(meta, score)
    assert "Nepali probe report" in markdown
    assert "| social.greet |" in markdown
    payload = build_report_json(meta, score)
    assert '"classifier": "oracle"' in payload


def test_transliterator_wiring() -> None:
    key = next(key for key in ORDERING_DICT if " " not in key and key.isascii())
    assert transliterate_to_devanagari(key) == ORDERING_DICT[key]
    assert detect_language(key) == "ne-rom"
    assert transliterate_to_devanagari("xyzzy") == "xyzzy"
    assert detect_language("") is None


def test_detect_language_script_split() -> None:
    assert detect_language("मोमोको मूल्य कति हो?") == "ne"
    assert detect_language("hello there") == "en"
