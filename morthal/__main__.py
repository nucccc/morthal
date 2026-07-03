"""Morthal CLI — Python code analysis toolkit"""

import argparse
import tempfile
from pathlib import Path

from .main import handle
from .utils.codebase import LocalCodebase, GitCodebase
from .utils.store import Store
from .vcs import normalize_url, clone_repo


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze Python codebases and generate reports",
    )
    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument(
        "--path", "-p",
        type=Path,
        default=None,
        help="Local directory to analyze (default: current directory)",
    )
    target_group.add_argument(
        "--github", "-g",
        type=str,
        default=None,
        help="GitHub URL — owner/repo, github.com/owner/repo, or full URL",
    )
    parser.add_argument(
        "--support-dir",
        "-s",
        type=Path,
        default='.morthal',
        help="Cache/working directory (default: {target}/.morthal for local, ./.morthal for GitHub)",
    )
    parser.add_argument(
        "--report",
        "-r",
        action="store_true",
        help="Generate HTML report in the support directory",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force re-collection, ignoring cached data",
    )
    parser.add_argument(
        "--history",
        "-H",
        action="store_true",
        help="Walk commit history and output CSV",
    )

    args = parser.parse_args()

    if args.github:
        # TODO: handle potential errors in case urls is invalid
        target = GitCodebase(args.github)
    else:
        target = LocalCodebase(args.path)

    store = Store(
        path=Path(args.support_dir),
        target=target.name,
        force=args.force
    )
    
    handle(
        target=target,
        store=store,
        report=args.report,
        history=args.history,
    )

    target.dispose()


if __name__ == "__main__":
    main()
