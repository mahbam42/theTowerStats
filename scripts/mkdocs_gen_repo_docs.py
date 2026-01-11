"""Generate MkDocs pages for repository Markdown files.

Reads curated repo-root Markdown documents and writes virtual pages under
docs/repo/ so MkDocs can include them without symlinks.
"""

from __future__ import annotations

from pathlib import Path

import mkdocs_gen_files  # type: ignore[import-not-found]

REPO_FILES = (
    "readme.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "VERSIONING.md",
)


def generate_repo_docs() -> None:
    """Create virtual MkDocs pages for repository Markdown documents."""
    repo_root = Path(__file__).resolve().parents[1]
    target_dir = Path("repo")

    for source_name in REPO_FILES:
        source_path = repo_root / source_name
        if not source_path.exists():
            raise FileNotFoundError(f"Missing repository document: {source_name}")

        target_path = target_dir / source_name
        with mkdocs_gen_files.open(target_path, "w") as target_file:
            target_file.write(source_path.read_text(encoding="utf-8"))
        mkdocs_gen_files.set_edit_path(target_path, source_path)


generate_repo_docs()
