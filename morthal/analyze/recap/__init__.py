'''
analyzer shall account for tha analysis of collected function data
'''

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import polars as pl

from morthal.analyze.collect import CodeData


@dataclass
class CodeRecap:
    """Summary statistics for repository analysis"""
    total_funcs: int
    avg_depth: float
    median_depth: float
    avg_lines: float
    total_args: int
    annotated_args: int
    arg_coverage: float  # percentage
    return_coverage: float  # percentage
    deep_funcs: int  # functions with depth >= threshold
    long_funcs: int  # functions with lines > threshold
    unannotated_funcs: int  # functions without return type
    
    # Store thresholds used for calculations
    depth_threshold: int
    lines_threshold: int

    funcs_df: pl.DataFrame

    def save(self, path: Path):
        self.funcs_df.write_parquet(path / "funcs.parquet")
        with open(path / "fpath.json", "w") as f:
            json.dump({
                'total_funcs':self.total_funcs,
                'avg_depth':self.avg_depth,
                'median_depth':self.median_depth,
                'avg_lines':self.avg_lines,
                'total_args':self.total_args,
                'annotated_args':self.annotated_args,
                'arg_coverage':self.arg_coverage,
                'return_coverage':self.return_coverage,
            }, f)
        



def build_repo_recap(
    repo_data: CodeData,
    depth_high: int = 5,
    lines_long: int = 50
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
    
    # Basic stats
    total_funcs = len(df)
    avg_depth = float(df[depth_col].mean() or 0.0)  # type: ignore
    median_depth = float(df[depth_col].median() or 0.0)  # type: ignore
    avg_lines = float(df['n_codelines'].mean() or 0.0)  # type: ignore
    
    # Annotation coverage
    total_args = int(df['n_func_args'].sum())  # type: ignore
    annotated_args = int(df['n_func_args_annotated'].sum())  # type: ignore
    arg_coverage = (annotated_args / total_args * 100) if total_args > 0 else 0.0
    return_coverage = (df['return_annotated'].sum() / total_funcs * 100) if total_funcs > 0 else 0.0
    
    # Tech debt indicators
    deep_funcs = len(df.filter(pl.col(depth_col) >= depth_high))
    long_funcs = len(df.filter(pl.col('n_codelines') > lines_long))
    unannotated_funcs = len(df.filter(~pl.col('return_annotated')))
    
    return CodeRecap(
        total_funcs=total_funcs,
        avg_depth=avg_depth,
        median_depth=median_depth,
        avg_lines=avg_lines,
        total_args=total_args,
        annotated_args=annotated_args,
        arg_coverage=arg_coverage,
        return_coverage=return_coverage,
        deep_funcs=deep_funcs,
        long_funcs=long_funcs,
        unannotated_funcs=unannotated_funcs,
        depth_threshold=depth_high,
        lines_threshold=lines_long,
        funcs_df=df
    )


dataclass
class Commit:
    hash: str
    dt: datetime



@dataclass
class RepoHistory:
    history: list[tuple[Commit, CodeRecap]]