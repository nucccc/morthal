"""Morthal CLI — Python code analysis toolkit"""

import argparse
import json
import tempfile
from datetime import datetime
from pathlib import Path

from .analyze.collect import collect_repo_data
from .analyze.recap import CodeRecap, Commit, RepoHistory, build_repo_recap
from .reporter import HTMLReporter
from .vcs import is_git_url, normalize_url, clone_repo, iter_pyfile_commits, extract_py_files


def _manifest_matches(path: Path, target: str) -> bool:
    try:
        return json.loads(path.read_text()).get("target") == target
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def _write_manifest(path: Path, target: str) -> None:
    path.write_text(
        json.dumps({"target": target, "analyzed_at": datetime.now().isoformat()})
    )


def _handle_local_dir(target: Path, args: argparse.Namespace) -> None:
    if not target.is_dir():
        raise SystemExit(f"target must be an existing directory: {target}")

    support_dir = args.support_dir or (target / ".morthal")
    support_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = support_dir / ".manifest.json"
    target_str = str(target.resolve())

    cached = (support_dir / "funcs.parquet").exists()

    if cached and not args.force and _manifest_matches(manifest_path, target_str):
        recap = CodeRecap.load(support_dir)
    else:
        repo_data = collect_repo_data(target)
        recap = build_repo_recap(repo_data)
        recap.save(support_dir)
        _write_manifest(manifest_path, target_str)

    if args.report:
        reporter = HTMLReporter(recap)
        reporter.generate(support_dir / "report.html")


def _handle_github_url(url: str, args: argparse.Namespace) -> None:
    url = normalize_url(url)
    print(f"Cloning {url} ...")

    with tempfile.TemporaryDirectory(prefix="morthal_") as tmp:
        clone_path = Path(tmp) / "repo"
        repo = clone_repo(url, clone_path)
        print(f"Cloned to {clone_path}")

        print("Analyzing latest snapshot ...")
        repo_data = collect_repo_data(clone_path)
        latest_recap = build_repo_recap(repo_data)
        print(f"Found {latest_recap.total_funcs} functions")

        if args.report:
            support_dir = args.support_dir or Path(".morthal")
            support_dir.mkdir(parents=True, exist_ok=True)
            reporter = HTMLReporter(latest_recap)
            reporter.generate(support_dir / "report.html")

        print("Walking commit history ...")
        history = RepoHistory(history=[])
        py_commits = list(iter_pyfile_commits(repo))

        for i, git_commit in enumerate(reversed(py_commits)):
            commit = Commit(
                hash=git_commit.hexsha,
                dt=datetime.fromtimestamp(git_commit.committed_date),
                author=git_commit.author.name,
                message=git_commit.message.strip(),
            )

            with tempfile.TemporaryDirectory(prefix="morthal_extract_") as xtmp:
                extract_py_files(repo, git_commit.hexsha, Path(xtmp))
                cd = collect_repo_data(Path(xtmp))
                cr = build_repo_recap(cd)
                history.history.append((commit, cr))

            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(py_commits)} commits")

        print(f"Processed {len(history.history)} commits")

        csv_path = Path("commit_history.csv")
        history.to_csv(csv_path)
        print(f"Commit history saved to: {csv_path.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze Python codebases and generate reports"
    )
    parser.add_argument("--target", "-t", type=str, help="Target directory or GitHub URL")
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

    if not args.target:
        parser.error("--target is required (local directory path or GitHub URL)")

    if is_git_url(args.target):
        _handle_github_url(args.target, args)
    else:
        _handle_local_dir(Path(args.target), args)


if __name__ == "__main__":
    main()
