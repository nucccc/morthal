import json
from datetime import datetime
from pathlib import Path

import polars as pl

from morthal.analyze.recap import CodeRecap, FuncsRecap


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
        (self.path / "recap.json").write_text(
            json.dumps(recap.funcs_recap.model_dump())
        )

    def load_recap(self) -> CodeRecap:
        funcs_df = pl.read_parquet(self.path / "funcs.parquet")
        data = json.loads((self.path / "recap.json").read_text())
        return CodeRecap(funcs_recap=FuncsRecap(**data), funcs_df=funcs_df)

    @property
    def _manifest_path(self) -> Path:
        return self.path / ".manifest.json"
    

    def load_history(self) -> pl.DataFrame:
        return pl.read_csv(self.path / 'commit_history.csv')
