from pathlib import Path

from .stats import collect_repo_data

default_path = "/home/nucccc/cod/projs/sqlmodelgen"

repo_data = collect_repo_data(Path(default_path))

repo_data.funcs_df.write_csv("data.csv")

