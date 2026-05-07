"""Regression checks for appendix anchors and duplicated internal crossrefs."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

APPENDICES = {
    "app01": REPO_ROOT / "tex" / "appendices" / "app01.tex",
    "app02": REPO_ROOT / "tex" / "appendices" / "app02.tex",
    "app03": REPO_ROOT / "tex" / "appendices" / "app03.tex",
    "app04": REPO_ROOT / "tex" / "appendices" / "app04.tex",
    "app05": REPO_ROOT / "tex" / "appendices" / "app05.tex",
}

CH01 = REPO_ROOT / "tex" / "chapters" / "ch01.tex"
CH02 = REPO_ROOT / "tex" / "chapters" / "ch02.tex"
CH03 = REPO_ROOT / "tex" / "chapters" / "ch03.tex"
CH04 = REPO_ROOT / "tex" / "chapters" / "ch04.tex"
CH05 = REPO_ROOT / "tex" / "chapters" / "ch05.tex"


def test_appendix_internal_section_labels_exist():
    expected = {
        "app01": ["sec:appendices-app01:2", "sec:appendices-app01:3", "sec:appendices-app01:4"],
        "app02": ["sec:appendices-app02:1", "sec:appendices-app02:2", "sec:appendices-app02:3"],
        "app03": [
            "sec:appendices-app03:1",
            "sec:appendices-app03:2",
            "sec:appendices-app03:3",
            "sec:appendices-app03:4",
        ],
        "app04": [
            "sec:appendices-app04:1",
            "sec:appendices-app04:2",
            "sec:appendices-app04:3",
            "sec:appendices-app04:4",
            "sec:appendices-app04:5",
            "sec:appendices-app04:6",
        ],
        "app05": [
            "sec:appendices-app05:1",
            "sec:appendices-app05:2",
            "sec:appendices-app05:3",
            "sec:appendices-app05:4",
            "sec:appendices-app05:5",
            "sec:appendices-app05:6",
        ],
    }

    for key, labels in expected.items():
        text = APPENDICES[key].read_text(encoding="utf-8")
        missing = [label for label in labels if f"\\appendixsectionlabel{{{label}}}" not in text]
        assert not missing, f"Missing appendix labels in {key}: {missing}"


def test_no_malformed_double_section_refs_remain():
    offenders = []
    for path in (REPO_ROOT / "tex").glob("**/*.tex"):
        text = path.read_text(encoding="utf-8")
        if "see see sec." in text or "cf. cf. sec." in text:
            offenders.append(str(path.relative_to(REPO_ROOT)))

    assert not offenders, "Malformed duplicated section refs remain:\n" + "\n".join(offenders)


def test_appendix_crossrefs_show_ref_plus_ocr_copy():
    assert (
        "appendix \\ref{app:1}, sec. \\ref{sec:appendices-app01:4} (appendix 1, sec. 4)"
        in CH01.read_text(encoding="utf-8")
    )
    assert (
        "appendix \\ref{app:5}, sec. \\ref{sec:appendices-app05:2} (appendix 5, sec. 2)"
        in CH02.read_text(encoding="utf-8")
    )
    assert (
        "appendix \\ref{app:4}, sec. \\ref{sec:appendices-app04:6} (appendix 4, sec. 6)"
        in CH03.read_text(encoding="utf-8")
    )
    assert (
        "appendix \\ref{app:4}, sec. \\ref{sec:appendices-app04:5} (appendix 4, sec. 5)"
        in CH04.read_text(encoding="utf-8")
    )
    assert (
        "appendix \\ref{app:5}, sec. \\ref{sec:appendices-app05:2} (appendix 5, sec. 2)"
        in CH05.read_text(encoding="utf-8")
    )
