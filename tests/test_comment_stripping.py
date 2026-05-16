"""Regression test: ensure comments don't appear in LaTeX output."""
import importlib.util
import sys
from pathlib import Path

EMIT_STRUCTURE_PATH = Path(__file__).parent.parent / "scripts" / "06_emit_structure.py"
SPEC = importlib.util.spec_from_file_location("emit_structure", EMIT_STRUCTURE_PATH)
emit_structure = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(emit_structure)

parse_page = emit_structure.parse_page
process_body_text = emit_structure.process_body_text

def test_parse_page_strips_metadata_comments():
    """Test that parse_page skips leading metadata comments."""
    md = """<!-- source: scan p. 018, printed p. 1, section: frontmatter/preamble -->
<!-- substrate: google-vision -->
<!-- running-head-removed: 'PREAMBLE' -->
<!-- edge-lines-dropped: 1 -->

Preamble
Some text here."""
    
    page = parse_page(md)
    
    # Body should start with "Preamble", not with any comments
    assert page["body"].startswith("Preamble"), f"Body should start with 'Preamble', got: {page['body'][:50]}"
    assert "<!-- substrate" not in page["body"], "substrate comment should not be in body"
    assert "<!-- running-head" not in page["body"], "running-head comment should not be in body"
    assert "<!-- edge-lines" not in page["body"], "edge-lines comment should not be in body"
    print("✓ parse_page_strips_metadata_comments passed")


def test_process_body_text_removes_orphaned_comments():
    """Test that process_body_text removes any remaining comments."""
    body = """<!-- substrate: google-vision -->

Preamble
Some text here."""
    
    result = process_body_text(body)
    
    # No HTML comments should be left in the output
    assert "<!-- substrate" not in result, "substrate comment should be removed"
    assert "<!-- " not in result or "@@FOOTNOTE@@" in result, "no other HTML comments should remain"
    print("✓ process_body_text_removes_orphaned_comments passed")


def test_latex_output_no_html_comments():
    """Test that LaTeX output contains no HTML comments."""
    import glob
    import re

    offenders = []
    for tex_file in glob.glob("tex/**/*.tex", recursive=True):
        content = Path(tex_file).read_text(errors="replace")
        if "<!-- " in content and content.count("<!--") > 0:
            comments = re.findall(r"<!--\s*(?!.*\)\s*-->)", content)
            if comments:
                offenders.append((tex_file, comments[:3]))

    assert not offenders, "Found HTML comments in:\n" + "\n".join(
        f"{tex_file}: {comments}" for tex_file, comments in offenders
    )


if __name__ == "__main__":
    try:
        test_parse_page_strips_metadata_comments()
        test_process_body_text_removes_orphaned_comments()
        test_latex_output_no_html_comments()
        print("\n✓ All regression tests passed")
    except AssertionError:
        print("\n✗ Regression test failed")
        sys.exit(1)
