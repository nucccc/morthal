# Morthal HTML Reporter

Generate beautiful, interactive HTML reports from Python code analysis data.

## Features

- **Summary Statistics**: Overview of codebase metrics (functions, depth, annotations, etc.)
- **Technical Debt Detection**: Automatically highlights problematic code patterns:
  - Deep nesting (≥5 levels)
  - Long functions (>50 lines)
  - Missing type annotations
  - High complexity (>100 AST nodes)
- **Interactive Table**: Sortable, searchable function list with filters
- **Zero Dependencies**: Pure HTML/CSS/JavaScript - no external libraries needed
- **Self-Contained**: Single HTML file that works offline

## Usage

### From CSV File

```python
from morthal.reporter import HTMLReporter

# Generate report from CSV
reporter = HTMLReporter.from_csv('data.csv')
reporter.generate('report.html')
```

### From Polars DataFrame

```python
import polars as pl
from morthal.reporter import HTMLReporter

# Load and analyze data
df = pl.read_csv('data.csv')
reporter = HTMLReporter(df)
reporter.generate('my_report.html')
```

### Command Line

```bash
# Run the example script
python example_report.py
```

## Report Sections

### 1. Summary Cards
- Total functions analyzed
- Average/median nesting depth
- Average function length
- Argument annotation coverage
- Return type annotation coverage
- Deep nesting count
- Long function count
- Missing type hints count

### 2. Technical Debt Indicators
Highlights functions that need attention:
- **Critical**: Deep nesting + long functions
- **High Complexity**: Many AST nodes/expressions
- **No Type Hints**: Missing all annotations

### 3. Functions Table
Interactive table with:
- **Sorting**: Click column headers to sort
- **Search**: Filter by function name or file path
- **Quick Filters**:
  - All functions
  - Deep nesting (depth ≥3)
  - Long functions (>30 lines)
  - Missing annotations

## Customization

### Configure Thresholds

Modify the class constants in `html_reporter.py`:

```python
class HTMLReporter:
    DEPTH_HIGH = 5        # Critical depth threshold
    DEPTH_MEDIUM = 3      # Warning depth threshold
    LINES_LONG = 50       # Long function threshold
    COMPLEXITY_HIGH = 100 # High complexity threshold
```

## CSV Format

Expected columns in the input CSV:
- `name` - Function name
- `max_depth` - Maximum nesting depth
- `n_codelines` - Lines of code
- `n_exprs` - Number of expressions
- `n_nodes` - Number of AST nodes
- `n_func_args` - Total arguments
- `n_func_args_annotated` - Annotated arguments
- `return_annotated` - Boolean, return type annotated
- `fpath` - File path

## Examples

See `example_report.py` in the project root for usage examples.

## Output

The generated HTML report includes:
- Responsive design (works on mobile/desktop)
- Interactive sorting and filtering
- Color-coded depth indicators
- Annotation status indicators
- Hover effects and smooth transitions
- Single self-contained file (no external dependencies)

Open `report.html` in any modern web browser to view your analysis!
