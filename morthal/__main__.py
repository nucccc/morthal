from pathlib import Path

from .stats import collect_repo_data
from .analyzer import build_repo_recap
from .reporter import HTMLReporter

default_path = "/home/nucccc/cod/projs/sqlmodelgen/src"

repo_data = collect_repo_data(Path(default_path))

repo_data.funcs_df.write_csv("data.csv")

repo_recap = build_repo_recap(repo_data)

print(len(repo_data.funcs_df))

html_reporter = HTMLReporter(repo_recap)
html_reporter.generate(Path("morthal_recap.html"))