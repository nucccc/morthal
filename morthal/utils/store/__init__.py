import json
from datetime import datetime
from pathlib import Path

import polars as pl

from morthal.analyze.recap import CodeRecap


_CACHE_FILES = ["funcs.parquet", "recap.json", ".manifest.json"]


class Store:
    def __init__(self, path: Path, target: str, force: bool = False) -> None:
        self.path = path
        path.mkdir(parents=True, exist_ok=True)

        if force or not self._manifest_matches(target):
            self._clear_cache()
            self._write_manifest(target)

    def _manifest_matches(self, target: str) -> bool:
        try:
            return json.loads(self._manifest_path.read_text()).get("target") == target
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    def _write_manifest(self, target: str) -> None:
        self._manifest_path.write_text(
            json.dumps({"target": target, "analyzed_at": datetime.now().isoformat()})
        )

    def _clear_cache(self) -> None:
        for name in _CACHE_FILES:
            (self.path / name).unlink(missing_ok=True)

    @property
    def has_cached_recap(self) -> bool:
        return (self.path / "funcs.parquet").exists()

    def save_recap(self, recap: CodeRecap) -> None:
        recap.funcs_df.write_parquet(self.path / "funcs.parquet")
        with open(self.path / "recap.json", "w") as f:
            json.dump({
                "total_funcs": recap.total_funcs,
                "avg_depth": recap.avg_depth,
                "median_depth": recap.median_depth,
                "avg_lines": recap.avg_lines,
                "total_args": recap.total_args,
                "annotated_args": recap.annotated_args,
                "arg_coverage": recap.arg_coverage,
                "return_coverage": recap.return_coverage,
                "deep_funcs": recap.deep_funcs,
                "long_funcs": recap.long_funcs,
                "unannotated_funcs": recap.unannotated_funcs,
                "depth_threshold": recap.depth_threshold,
                "lines_threshold": recap.lines_threshold,
            }, f)

    def load_recap(self) -> CodeRecap:
        funcs_df = pl.read_parquet(self.path / "funcs.parquet")
        with open(self.path / "recap.json") as f:
            data = json.load(f)
        return CodeRecap(
            total_funcs=data["total_funcs"],
            avg_depth=data["avg_depth"],
            median_depth=data["median_depth"],
            avg_lines=data["avg_lines"],
            total_args=data["total_args"],
            annotated_args=data["annotated_args"],
            arg_coverage=data["arg_coverage"],
            return_coverage=data["return_coverage"],
            deep_funcs=data["deep_funcs"],
            long_funcs=data["long_funcs"],
            unannotated_funcs=data["unannotated_funcs"],
            depth_threshold=data["depth_threshold"],
            lines_threshold=data["lines_threshold"],
            funcs_df=funcs_df,
        )

    @property
    def _manifest_path(self) -> Path:
        return self.path / ".manifest.json"
    

    def load_history(self) -> pl.DataFrame:
        return pl.read_csv(self.path / 'commit_history.csv')
