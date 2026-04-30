"""Regression test: ensure comments don't appear in LaTeX output."""
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from emit_structure import parse_page, process_body_text

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
    # This would need to load actual tex files
    import glob
    
    for tex_file in glob.glob("tex/**/*.tex", recursive=True):
        content = Path(tex_file).read_text(errors="replace")
        # Allow % comments (LaTeX) but not <!-- comments (HTML)
        if "<!-- " in content and content.count("<!--") > 0:
            # Count actual occurrences of HTML comments (excluding those in strings)
            import re
            comments = re.findall(r"<!--\s*(?!.*\)\s*-->)", content)
            if comments:
                print(f"✗ Found HTML comments in {tex_file}:")
                for comment in comments[:3]:
                    print(f"  {comment}")
                return False
    print("✓ latex_output_no_html_comments passed")
    return True


if __name__ == "__main__":
    test_parse_page_strips_metadata_comments()
    test_process_body_text_removes_orphaned_comments()
    if test_latex_output_no_html_comments():
        print("\n✓ All regression tests passed")
    else:
        print("\n✗ Regression test failed")
        sys.exit(1)
