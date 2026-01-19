"""
HTML Reporter for Morthal code analysis
Generates interactive HTML reports from function statistics
"""

from datetime import datetime
from pathlib import Path
from typing import Any

import polars as pl

from .templates import get_html_template


class HTMLReporter:
    """Generate HTML reports from code analysis data"""
    
    # Configurable thresholds for tech debt detection
    DEPTH_HIGH = 5
    DEPTH_MEDIUM = 3
    LINES_LONG = 50
    COMPLEXITY_HIGH = 100  # n_nodes threshold
    
    def __init__(self, df: pl.DataFrame):
        """
        Initialize reporter with a Polars DataFrame
        
        Args:
            df: DataFrame containing function statistics
        """
        self.df = df
        
    @classmethod
    def from_csv(cls, csv_path: str | Path) -> 'HTMLReporter':
        """
        Create reporter from CSV file
        
        Args:
            csv_path: Path to CSV file containing function statistics
            
        Returns:
            HTMLReporter instance
        """
        df = pl.read_csv(csv_path)
        return cls(df)
    
    def _generate_summary_cards(self) -> str:
        """Generate HTML for summary statistics cards"""
        total_funcs = len(self.df)
        avg_depth = self.df['max_depth'].mean()
        median_depth = self.df['max_depth'].median()
        avg_lines = self.df['n_codelines'].mean()
        
        # Calculate annotation coverage
        total_args = self.df['n_func_args'].sum()
        annotated_args = self.df['n_func_args_annotated'].sum()
        arg_coverage = (annotated_args / total_args * 100) if total_args > 0 else 0
        
        return_coverage = (self.df['return_annotated'].sum() / total_funcs * 100) if total_funcs > 0 else 0
        
        # Count tech debt indicators
        deep_funcs = len(self.df.filter(pl.col('max_depth') >= self.DEPTH_HIGH))
        long_funcs = len(self.df.filter(pl.col('n_codelines') > self.LINES_LONG))
        unannotated = len(self.df.filter(~pl.col('return_annotated')))
        
        cards = f"""
        <div class="summary-card">
            <h3>Total Functions</h3>
            <div class="value">{total_funcs}</div>
            <div class="subtext">analyzed in codebase</div>
        </div>
        
        <div class="summary-card">
            <h3>Average Depth</h3>
            <div class="value">{avg_depth:.1f}</div>
            <div class="subtext">median: {median_depth:.0f}</div>
        </div>
        
        <div class="summary-card">
            <h3>Average Lines</h3>
            <div class="value">{avg_lines:.0f}</div>
            <div class="subtext">per function</div>
        </div>
        
        <div class="summary-card">
            <h3>Argument Annotations</h3>
            <div class="value">{arg_coverage:.0f}%</div>
            <div class="subtext">{annotated_args} of {total_args} args</div>
        </div>
        
        <div class="summary-card">
            <h3>Return Annotations</h3>
            <div class="value">{return_coverage:.0f}%</div>
            <div class="subtext">{int(self.df['return_annotated'].sum())} of {total_funcs} funcs</div>
        </div>
        
        <div class="summary-card">
            <h3>Deep Nesting</h3>
            <div class="value">{deep_funcs}</div>
            <div class="subtext">depth ≥ {self.DEPTH_HIGH}</div>
        </div>
        
        <div class="summary-card">
            <h3>Long Functions</h3>
            <div class="value">{long_funcs}</div>
            <div class="subtext">&gt; {self.LINES_LONG} lines</div>
        </div>
        
        <div class="summary-card">
            <h3>Missing Return Type</h3>
            <div class="value">{unannotated}</div>
            <div class="subtext">functions without type hints</div>
        </div>
        """
        
        return cards
    
    def _generate_tech_debt_items(self) -> str:
        """Generate HTML for technical debt indicators"""
        items = []
        
        # Critical: Deep nesting AND long functions
        critical = self.df.filter(
            (pl.col('max_depth') >= self.DEPTH_HIGH) & 
            (pl.col('n_codelines') > self.LINES_LONG)
        ).sort('max_depth', descending=True).head(10)
        
        for row in critical.iter_rows(named=True):
            items.append(f"""
            <li class="tech-debt-item critical">
                <strong>🔴 Critical: {row['name']}</strong>
                Deep nesting ({row['max_depth']}) + Long function ({row['n_codelines']} lines)
                <div class="file-path">{row['fpath']}</div>
            </li>
            """)
        
        # High complexity functions
        complex_funcs = self.df.filter(
            pl.col('n_nodes') > self.COMPLEXITY_HIGH
        ).sort('n_nodes', descending=True).head(5)
        
        for row in complex_funcs.iter_rows(named=True):
            items.append(f"""
            <li class="tech-debt-item">
                <strong>⚠️ High Complexity: {row['name']}</strong>
                {row['n_nodes']} AST nodes, {row['n_exprs']} expressions
                <div class="file-path">{row['fpath']}</div>
            </li>
            """)
        
        # Functions with no type hints at all
        no_hints = self.df.filter(
            ~pl.col('return_annotated') & 
            (pl.col('n_func_args_annotated') == 0) &
            (pl.col('n_func_args') > 0)
        ).head(5)
        
        for row in no_hints.iter_rows(named=True):
            items.append(f"""
            <li class="tech-debt-item">
                <strong>📝 No Type Hints: {row['name']}</strong>
                {row['n_func_args']} arguments, 0 annotations
                <div class="file-path">{row['fpath']}</div>
            </li>
            """)
        
        if not items:
            return '<p style="color: #28a745; font-weight: bold;">✅ No significant technical debt detected!</p>'
        
        return f'<ul class="tech-debt-list">{"".join(items)}</ul>'
    
    def _get_depth_badge(self, depth: int) -> str:
        """Get HTML badge for depth level"""
        if depth >= self.DEPTH_HIGH:
            css_class = "depth-high"
        elif depth >= self.DEPTH_MEDIUM:
            css_class = "depth-medium"
        else:
            css_class = "depth-low"
        
        return f'<span class="depth-badge {css_class}">{depth}</span>'
    
    def _get_annotation_indicator(self, args_annotated: int, total_args: int, return_annotated: bool) -> str:
        """Get HTML indicator for annotation status"""
        if total_args == 0:
            indicator_class = "annotation-good" if return_annotated else "annotation-bad"
        elif args_annotated == total_args and return_annotated:
            indicator_class = "annotation-good"
        elif args_annotated > 0 or return_annotated:
            indicator_class = "annotation-partial"
        else:
            indicator_class = "annotation-bad"
        
        return_symbol = "✓" if return_annotated else "✗"
        annotation_text = f"{args_annotated}/{total_args} args, return {return_symbol}"
        
        return f'<span class="annotation-indicator {indicator_class}"></span>{annotation_text}'
    
    def _generate_table_rows(self) -> str:
        """Generate HTML table rows for all functions"""
        # Sort by depth by default
        sorted_df = self.df.sort('max_depth', descending=True)
        
        rows = []
        for row in sorted_df.iter_rows(named=True):
            depth_badge = self._get_depth_badge(row['max_depth'])
            annotation = self._get_annotation_indicator(
                row['n_func_args_annotated'],
                row['n_func_args'],
                row['return_annotated']
            )
            
            # Truncate file path for display
            file_path = str(row['fpath'])
            display_path = file_path if len(file_path) < 80 else "..." + file_path[-77:]
            
            rows.append(f"""
            <tr data-name="{row['name']}" 
                data-max_depth="{row['max_depth']}" 
                data-n_codelines="{row['n_codelines']}"
                data-n_exprs="{row['n_exprs']}"
                data-n_nodes="{row['n_nodes']}"
                data-n_func_args="{row['n_func_args']}"
                data-n_func_args_annotated="{row['n_func_args_annotated']}"
                data-return_annotated="{str(row['return_annotated']).lower()}">
                <td><strong>{row['name']}</strong></td>
                <td>{depth_badge}</td>
                <td>{row['n_codelines']}</td>
                <td>{row['n_exprs']}</td>
                <td>{row['n_nodes']}</td>
                <td>{row['n_func_args']}</td>
                <td>{annotation}</td>
                <td class="file-path" title="{file_path}">{display_path}</td>
            </tr>
            """)
        
        return "".join(rows)
    
    def generate(self, output_path: str | Path, **kwargs: Any) -> None:
        """
        Generate HTML report and save to file
        
        Args:
            output_path: Path where HTML report will be saved
            **kwargs: Additional configuration options (reserved for future use)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate all components
        summary_cards = self._generate_summary_cards()
        tech_debt_items = self._generate_tech_debt_items()
        table_rows = self._generate_table_rows()
        
        # Get template with all values filled
        html_content = get_html_template(
            timestamp=timestamp,
            summary_cards=summary_cards,
            tech_debt_items=tech_debt_items,
            table_rows=table_rows
        )
        
        # Write to file
        output_path = Path(output_path)
        output_path.write_text(html_content, encoding='utf-8')
        
        print(f"✅ Report generated: {output_path.absolute()}")
        print(f"📊 Analyzed {len(self.df)} functions")
