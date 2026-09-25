"""Benchmark corpus, scoring, reports, and the ported transliterator."""

from __future__ import annotations

from layanep.benchmark.corpus import BENCHMARK_REVISION, load_corpus, validate_corpus
from layanep.benchmark.report import build_report_json, build_report_markdown
from layanep.benchmark.runner import oracle_classifier, run_probe, score_probe, stub_classifier
from layanep.glossary import ORDERING_DICT
from layanep.schema import LU_COMMAND_KINDS
from layanep.transliterate import detect_language, transliterate_to_devanagari


def test_corpus_is_valid() -> None:
    corpus = load_corpus()
    assert validate_corpus(corpus) == []
    assert corpus.revision == BENCHMARK_REVISION
    assert len(corpus.steps) >= 60


def test_corpus_covers_the_vocabulary() -> None:
    corpus = load_corpus()
    expected = {step.expected for step in corpus.steps if step.expected}
    assert set(LU_COMMAND_KINDS) <= expected
    languages = {step.language for step in corpus.steps}
    assert languages == {"en", "ne-rom", "ne"}


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
