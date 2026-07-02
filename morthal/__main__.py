"""Morthal CLI — Python code analysis toolkit"""

import argparse
import tempfile
from pathlib import Path

from .main import handle
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
        default=None,
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
        url = normalize_url(args.github)
        print(f"Cloning {url} ...")
        with tempfile.TemporaryDirectory(prefix="morthal_") as tmp:
            clone_path = Path(tmp) / "repo"
            clone_repo(url, clone_path)
            print(f"Cloned to {clone_path}")
            if not args.support_dir:
                args.support_dir = Path(".morthal")
            handle(
                target_path=clone_path,
                support_path=args.support_dir,
                force=args.force,
                report=args.report,
                history=args.history,
            )
    else:
        target_path = args.path or Path(".")
        if not args.support_dir:
            args.support_dir = target_path / ".morthal"
        handle(
            target_path=target_path,
            support_path=args.support_dir,
            force=args.force,
            report=args.report,
            history=args.history,
        )


if __name__ == "__main__":
    main()
