from morthal.analyze.collect import collect_codebase_data
from morthal.analyze.recap import build_repo_recap
from morthal.history import walk_commit_history
from morthal.reporter import HTMLReporter
from morthal.utils.codebase import Codebase
from morthal.utils.store import Store


def handle(
    target: Codebase,
    store: Store,
    report: bool,
    history: bool,
) -> None:

    if store.has_cached_recap:
        recap = store.load_recap()
    else:
        repo_data = collect_codebase_data(target.path)
        recap = build_repo_recap(repo_data)
        store.save_recap(recap)

    if report:
        reporter = HTMLReporter(recap)
        reporter.generate(store.path / "report.html")

    if history:
        print("Walking commit history ...")
        history = walk_commit_history(target.path)
        csv_path = store.path / "commit_history.csv"
        history.to_csv(csv_path)
        print(f"Commit history saved to: {csv_path.resolve()}")