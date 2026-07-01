"""Morthal CLI — Python code analysis toolkit"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from .analyze.collect import collect_repo_data
from .analyze.recap import CodeRecap, build_repo_recap
from .reporter import HTMLReporter


def _manifest_matches(path: Path, target: str) -> bool:
    try:
        return json.loads(path.read_text()).get("target") == target
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def _write_manifest(path: Path, target: str) -> None:
    path.write_text(
        json.dumps({"target": target, "analyzed_at": datetime.now().isoformat()})
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze Python codebases and generate reports"
    )
    parser.add_argument("--target", "-t", type=Path, help="Target directory to analyze")
    parser.add_argument(
        "--support-dir",
        "-s",
        type=Path,
        default=None,
        help="Cache/working directory (default: {target}/.morthal)",
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

    args = parser.parse_args()

    if not args.target.is_dir():
        parser.error(f"target must be an existing directory: {args.target}")

    support_dir = args.support_dir or (args.target / ".morthal")
    support_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = support_dir / ".manifest.json"
    target_str = str(args.target.resolve())

    cached = (support_dir / "funcs.parquet").exists()

    if cached and not args.force and _manifest_matches(manifest_path, target_str):
        recap = CodeRecap.load(support_dir)
    else:
        repo_data = collect_repo_data(args.target)
        recap = build_repo_recap(repo_data)
        recap.save(support_dir)
        _write_manifest(manifest_path, target_str)

    if args.report:
        reporter = HTMLReporter(recap)
        reporter.generate(support_dir / "report.html")


if __name__ == "__main__":
    main()
