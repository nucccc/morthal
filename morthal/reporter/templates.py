"""
HTML templates for the code analysis reporter
"""

def get_css() -> str:
    """Returns the CSS styling (no template variables)"""
    return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        header p {
            font-size: 1.1em;
            opacity: 0.95;
        }
        
        .content {
            padding: 30px;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .summary-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .summary-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .summary-card h3 {
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        
        .summary-card .value {
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }
        
        .summary-card .subtext {
            font-size: 0.85em;
            color: #666;
            margin-top: 5px;
        }
        
        section {
            margin-bottom: 40px;
        }
        
        section h2 {
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }
        
        .controls {
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .search-box {
            flex: 1;
            min-width: 250px;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        .search-box:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .filter-btn {
            padding: 12px 20px;
            background: white;
            border: 2px solid #667eea;
            color: #667eea;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .filter-btn:hover {
            background: #667eea;
            color: white;
        }
        
        .filter-btn.active {
            background: #667eea;
            color: white;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        thead th {
            padding: 15px;
            text-align: left;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
            position: relative;
        }
        
        thead th:hover {
            background: rgba(255,255,255,0.1);
        }
        
        thead th.sortable::after {
            content: ' ⇅';
            opacity: 0.5;
            font-size: 0.8em;
        }
        
        thead th.sorted-asc::after {
            content: ' ↑';
            opacity: 1;
        }
        
        thead th.sorted-desc::after {
            content: ' ↓';
            opacity: 1;
        }
        
        tbody tr {
            border-bottom: 1px solid #f0f0f0;
            transition: background-color 0.2s;
        }
        
        tbody tr:hover {
            background-color: #f8f9fa;
        }
        
        tbody tr.hidden {
            display: none;
        }
        
        tbody td {
            padding: 12px 15px;
        }
        
        .depth-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.9em;
        }
        
        .depth-low { background: #d4edda; color: #155724; }
        .depth-medium { background: #fff3cd; color: #856404; }
        .depth-high { background: #f8d7da; color: #721c24; }
        
        .annotation-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 5px;
        }
        
        .annotation-good { background: #28a745; }
        .annotation-partial { background: #ffc107; }
        .annotation-bad { background: #dc3545; }
        
        .file-path {
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            color: #666;
            word-break: break-all;
        }
        
        .tech-debt-list {
            list-style: none;
        }
        
        .tech-debt-item {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
        }
        
        .tech-debt-item.critical {
            background: #f8d7da;
            border-left-color: #dc3545;
        }
        
        .tech-debt-item strong {
            color: #333;
            display: block;
            margin-bottom: 5px;
        }
        
        .tech-debt-item .file-path {
            margin-top: 5px;
        }
        
        .metric-bar {
            background: #e9ecef;
            height: 24px;
            border-radius: 12px;
            overflow: hidden;
            position: relative;
        }
        
        .metric-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.5s;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            color: white;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        footer {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .summary-grid {
                grid-template-columns: 1fr;
            }
            
            table {
                font-size: 0.85em;
            }
            
            thead th, tbody td {
                padding: 8px;
            }
        }
    """

def get_javascript() -> str:
    """Returns the JavaScript code (no template variables)"""
    return """
        // Table sorting functionality
        let sortDirection = {};
        
        document.querySelectorAll('thead th.sortable').forEach(header => {
            header.addEventListener('click', () => {
                const column = header.dataset.column;
                const table = document.getElementById('functionsTable');
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr:not(.hidden)'));
                
                // Toggle sort direction
                const isAsc = sortDirection[column] === 'asc';
                sortDirection[column] = isAsc ? 'desc' : 'asc';
                
                // Update header styling
                document.querySelectorAll('thead th').forEach(th => {
                    th.classList.remove('sorted-asc', 'sorted-desc');
                });
                header.classList.add(isAsc ? 'sorted-desc' : 'sorted-asc');
                
                // Sort rows
                rows.sort((a, b) => {
                    const aValue = a.dataset[column];
                    const bValue = b.dataset[column];
                    
                    // Try to parse as number
                    const aNum = parseFloat(aValue);
                    const bNum = parseFloat(bValue);
                    
                    let comparison = 0;
                    if (!isNaN(aNum) && !isNaN(bNum)) {
                        comparison = aNum - bNum;
                    } else {
                        comparison = aValue.localeCompare(bValue);
                    }
                    
                    return isAsc ? -comparison : comparison;
                });
                
                // Re-append sorted rows
                rows.forEach(row => tbody.appendChild(row));
            });
        });
        
        // Search functionality
        const searchBox = document.getElementById('searchBox');
        searchBox.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#functionsTable tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.classList.remove('hidden');
                } else {
                    row.classList.add('hidden');
                }
            });
        });
        
        // Filter functionality
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                // Update active state
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const filter = btn.dataset.filter;
                const rows = document.querySelectorAll('#functionsTable tbody tr');
                
                rows.forEach(row => {
                    const depth = parseInt(row.dataset.max_depth);
                    const lines = parseInt(row.dataset.n_codelines);
                    const argsAnnotated = parseInt(row.dataset.n_func_args_annotated);
                    const totalArgs = parseInt(row.dataset.n_func_args);
                    const returnAnnotated = row.dataset.return_annotated === 'true';
                    
                    let show = true;
                    
                    if (filter === 'deep') {
                        show = depth >= 3;
                    } else if (filter === 'long') {
                        show = lines > 30;
                    } else if (filter === 'unannotated') {
                        show = !returnAnnotated || argsAnnotated < totalArgs;
                    }
                    
                    if (show) {
                        row.classList.remove('hidden');
                    } else {
                        row.classList.add('hidden');
                    }
                });
                
                // Clear search when filtering
                searchBox.value = '';
            });
        });
        
        // Set "All" filter as active by default
        document.querySelector('.filter-btn[data-filter="all"]').classList.add('active');
    """

def get_html_template(timestamp: str, summary_cards: str, tech_debt_items: str, table_rows: str) -> str:
    """Returns the complete HTML document"""
    css = get_css()
    js = get_javascript()
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morthal Code Analysis Report</title>
    <style>{css}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Morthal Code Analysis Report</h1>
            <p>Technical Debt & Code Quality Analysis</p>
            <p style="font-size: 0.9em; margin-top: 10px;">Generated: {timestamp}</p>
        </header>
        
        <div class="content">
            <!-- Summary Section -->
            <section id="summary">
                <h2>Summary Statistics</h2>
                <div class="summary-grid">
                    {summary_cards}
                </div>
            </section>
            
            <!-- Tech Debt Section -->
            <section id="tech-debt">
                <h2>Technical Debt Indicators</h2>
                {tech_debt_items}
            </section>
            
            <!-- Functions Table -->
            <section id="functions">
                <h2>All Functions</h2>
                <div class="controls">
                    <input type="text" class="search-box" id="searchBox" placeholder="🔍 Search functions, files...">
                    <button class="filter-btn" data-filter="all">All</button>
                    <button class="filter-btn" data-filter="deep">Deep Nesting</button>
                    <button class="filter-btn" data-filter="long">Long Functions</button>
                    <button class="filter-btn" data-filter="unannotated">Missing Annotations</button>
                </div>
                <table id="functionsTable">
                    <thead>
                        <tr>
                            <th class="sortable" data-column="name">Function Name</th>
                            <th class="sortable" data-column="max_depth">Depth</th>
                            <th class="sortable" data-column="n_codelines">Lines</th>
                            <th class="sortable" data-column="n_exprs">Expressions</th>
                            <th class="sortable" data-column="n_nodes">Nodes</th>
                            <th class="sortable" data-column="n_func_args">Args</th>
                            <th>Annotations</th>
                            <th>File Path</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </section>
        </div>
        
        <footer>
            Generated by Morthal - Python Code Analysis Tool
        </footer>
    </div>
    
    <script>{js}</script>
</body>
</html>
"""
