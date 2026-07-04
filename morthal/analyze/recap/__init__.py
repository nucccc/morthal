'''
analyzer shall account for tha analysis of collected function data
'''

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import polars as pl
from pydantic import BaseModel

from morthal.analyze.collect import CodeData


class RecapFields(BaseModel):
    """Scalar summary statistics — no DataFrame, trivially serializable"""
    total_funcs: int
    avg_depth: float
    median_depth: float
    avg_lines: float
    avg_node_depth_per_func: float
    avg_node_depth: float
    total_args: int
    annotated_args: int
    arg_coverage: float
    return_coverage: float
    unannotated_funcs: int


@dataclass
class CodeRecap:
    recap: RecapFields
    funcs_df: pl.DataFrame

    def __getattr__(self, name: str):
        return getattr(self.recap, name)


def build_repo_recap(
    repo_data: CodeData,
) -> CodeRecap:
    """
    Build a repository recap with summary statistics from repo data.
    
    Args:
        repo_data: RepoData containing the functions DataFrame
        depth_high: Threshold for considering a function as deeply nested
        lines_long: Threshold for considering a function as long
        
    Returns:
        RepoRecap with all calculated summary statistics
    """
    df = repo_data.funcs_df
    
    # Determine which depth column to use (max_depth or max_stmt_depth)
    depth_col = 'max_stmt_depth'

    total_nodes = df['n_nodes'].sum()
    
    # Basic stats
    total_funcs = len(df)
    avg_depth = float(df[depth_col].mean() or 0.0)  # type: ignore
    median_depth = float(df[depth_col].median() or 0.0)  # type: ignore
    avg_lines = float(df['n_codelines'].mean() or 0.0)  # type: ignore
    avg_node_depth_per_func = float(df[depth_col].mean() or 0.0)
    avg_node_depth = float((df['avg_node_depth'] * df['n_nodes']).sum() / total_nodes) if total_nodes != 0 else 0.0

    # Annotation coverage
    total_args = int(df['n_func_args'].sum())  # type: ignore
    annotated_args = int(df['n_func_args_annotated'].sum())  # type: ignore
    arg_coverage = (annotated_args / total_args * 100) if total_args > 0 else 0.0
    return_coverage = (df['return_annotated'].sum() / total_funcs * 100) if total_funcs > 0 else 0.0

    # Tech debt indicators
    unannotated_funcs = len(df.filter(~pl.col('return_annotated')))
    
    return CodeRecap(
        recap=RecapFields(
            total_funcs=total_funcs,
            avg_depth=avg_depth,
            median_depth=median_depth,
            avg_lines=avg_lines,
            avg_node_depth_per_func=avg_node_depth_per_func,
            avg_node_depth=avg_node_depth,
            total_args=total_args,
            annotated_args=annotated_args,
            arg_coverage=arg_coverage,
            return_coverage=return_coverage,
            unannotated_funcs=unannotated_funcs,
        ),
        funcs_df=df,
    )


@dataclass
class Commit:
    hash: str
    dt: datetime
    author: str
    message: str


@dataclass
class RepoHistory:
    history: list[tuple[Commit, CodeRecap]]

    def to_csv(self, path: Path) -> None:
        import polars as pl
        rows = [
            {
                'commit_hash': c.hash,
                'datetime': c.dt.isoformat(),
                'author': c.author,
                'message': c.message,
                'total_funcs': r.total_funcs,
                'avg_depth': r.avg_depth,
                'median_depth': r.median_depth,
                'avg_lines': r.avg_lines,
                'total_args': r.total_args,
                'annotated_args': r.annotated_args,
                'arg_coverage': r.arg_coverage,
                'return_coverage': r.return_coverage,
                'unannotated_funcs': r.unannotated_funcs,
            }
            for c, r in self.history
        ]
        pl.DataFrame(rows).write_csv(path)
