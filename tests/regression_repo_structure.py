#!/usr/bin/env python3
"""
Regression test for repository tidiness and build structure.

Validates:
1. No PDF files outside build/output/
2. No LaTeX temp files in root directory
3. No test artifacts in root directory
4. .gitignore properly configured
5. Expected directory structure exists
"""

import os
import sys
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).parent.parent
ALLOWED_PDF_LOCATIONS = {REPO_ROOT / "build" / "output", REPO_ROOT / "source"}


def test_no_pdfs_in_root():
    """Verify no PDFs in root directory."""
    root_files = list(REPO_ROOT.glob("*.pdf"))
    assert not root_files, f"Found PDFs in root: {root_files}"
    print("✓ No PDFs in root directory")


def test_no_pdfs_in_tex_directory():
    """Verify no PDFs in tex/ directory."""
    tex_files = list((REPO_ROOT / "tex").glob("*.pdf"))
    assert not tex_files, f"Found PDFs in tex/: {tex_files}"
    print("✓ No PDFs in tex/ directory")


def test_no_latex_temp_in_root():
    """Verify no LaTeX temp files in root."""
    temp_extensions = ["*.aux", "*.log", "*.bcf", "*.blg", "*.fdb_latexmk"]
    for pattern in temp_extensions:
        files = list(REPO_ROOT.glob(pattern))
        assert not files, f"Found LaTeX temp files in root ({pattern}): {files}"
    print("✓ No LaTeX temp files in root")


def test_no_test_artifacts_in_root():
    """Verify no test artifacts in root."""
    test_patterns = [
        "test_inscription_*",
        "extracted_ch3_*",
        "texput.*",
    ]
    for pattern in test_patterns:
        files = list(REPO_ROOT.glob(pattern))
        assert not files, f"Found test artifacts in root ({pattern}): {files}"
    print("✓ No test artifacts in root")


def test_required_directories_exist():
    """Verify required directories exist."""
    required_dirs = [
        REPO_ROOT / "tex",
        REPO_ROOT / "tex" / "chapters",
        REPO_ROOT / "scripts",
        REPO_ROOT / "tests",
        REPO_ROOT / "build" / "output",
        REPO_ROOT / "data",
    ]
    for dir_path in required_dirs:
        assert dir_path.exists(), f"Missing required directory: {dir_path}"
        assert dir_path.is_dir(), f"Expected directory but found file: {dir_path}"
    print(f"✓ All required directories exist ({len(required_dirs)} checked)")


def test_build_script_exists():
    """Verify scripts/build.sh exists and is executable."""
    build_script = REPO_ROOT / "scripts" / "build.sh"
    assert build_script.exists(), f"Missing scripts/build.sh"
    assert os.access(build_script, os.X_OK), f"scripts/build.sh is not executable"
    print("✓ scripts/build.sh exists and is executable")


def test_gitignore_exists():
    """Verify .gitignore exists."""
    gitignore = REPO_ROOT / ".gitignore"
    assert gitignore.exists(), "Missing .gitignore"
    assert gitignore.is_file(), ".gitignore is not a file"
    print("✓ .gitignore exists")


def test_gitignore_covers_artifacts():
    """Verify .gitignore covers key artifact types."""
    gitignore = REPO_ROOT / ".gitignore"
    content = gitignore.read_text()
    
    required_patterns = [
        "*.aux",
        "*.log",
        "*.bcf",
        "*.pdf",
    ]
    
    for pattern in required_patterns:
        assert pattern in content, f".gitignore missing pattern: {pattern}"
    
    print(f"✓ .gitignore covers artifact types ({len(required_patterns)} patterns)")


def test_main_tex_exists():
    """Verify tex/main.tex exists."""
    main_tex = REPO_ROOT / "tex" / "main.tex"
    assert main_tex.exists(), "Missing tex/main.tex"
    assert main_tex.is_file(), "tex/main.tex is not a file"
    print("✓ tex/main.tex exists")


def test_no_nested_pdfs_in_build_except_output():
    """Verify PDFs only exist in build/output (not build/tex, build/logs, etc)."""
    build_dir = REPO_ROOT / "build"
    if not build_dir.exists():
        return
    
    for pdf_file in build_dir.glob("**/*.pdf"):
        parent_parts = pdf_file.parent.parts
        build_idx = parent_parts.index("build")
        subdir = parent_parts[build_idx + 1] if len(parent_parts) > build_idx + 1 else None
        assert subdir == "output", f"Found PDF in wrong location: {pdf_file}"
    
    print("✓ All PDFs in build/ are in build/output/")


def main():
    """Run all regression tests."""
    tests = [
        test_no_pdfs_in_root,
        test_no_pdfs_in_tex_directory,
        test_no_latex_temp_in_root,
        test_no_test_artifacts_in_root,
        test_required_directories_exist,
        test_build_script_exists,
        test_gitignore_exists,
        test_gitignore_covers_artifacts,
        test_main_tex_exists,
        test_no_nested_pdfs_in_build_except_output,
    ]
    
    print("=" * 60)
    print("Repository Tidiness Regression Tests")
    print("=" * 60)
    
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed += 1
    
    print("=" * 60)
    if failed == 0:
        print(f"✓ All {len(tests)} tests passed")
        print("=" * 60)
        return 0
    else:
        print(f"✗ {failed}/{len(tests)} tests failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
