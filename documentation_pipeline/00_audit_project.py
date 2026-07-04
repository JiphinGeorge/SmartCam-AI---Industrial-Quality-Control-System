import os
import ast
import sqlite3
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
DOCS_DIR.mkdir(exist_ok=True)
AUDIT_REPORT_PATH = DOCS_DIR / "AUDIT_REPORT.md"

def count_files_and_loc():
    stats = defaultdict(lambda: {"count": 0, "loc": 0})
    ignored_dirs = {'.git', 'venv310', '__pycache__', 'node_modules', 'dataset', 'dataset_original', 'models', 'reports', 'exports', 'documentation_pipeline'}
    
    for root, dirs, files in os.walk(ROOT):
        # Modify dirs in place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        
        for file in files:
            ext = Path(file).suffix.lower()
            if ext in ['.py', '.html', '.css', '.js', '.md']:
                filepath = Path(root) / file
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        stats[ext]["count"] += 1
                        stats[ext]["loc"] += len(lines)
                except Exception:
                    pass
    return stats

def analyze_flask_routes():
    routes = []
    routes_dir = ROOT / "app" / "routes"
    if not routes_dir.exists():
        return routes
        
    for py_file in routes_dir.glob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for dec in node.decorator_list:
                        if isinstance(dec, ast.Call) and hasattr(dec.func, 'attr') and dec.func.attr == 'route':
                            # It's a route
                            try:
                                path = dec.args[0].value
                                methods = ['GET']
                                for kw in dec.keywords:
                                    if kw.arg == 'methods':
                                        methods = [el.value for el in kw.value.elts]
                                routes.append({
                                    "blueprint": py_file.stem,
                                    "path": path,
                                    "methods": methods,
                                    "function": node.name
                                })
                            except Exception:
                                pass
        except Exception as e:
            print(f"Error parsing {py_file}: {e}")
    return routes

def analyze_database():
    db_path = ROOT / "database" / "smartcam.db"
    schema = {}
    if not db_path.exists():
        return schema
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for name, sql in tables:
            if name != "sqlite_sequence":
                cursor.execute(f"PRAGMA table_info({name})")
                columns = cursor.fetchall()
                schema[name] = {
                    "sql": sql,
                    "columns": [{"cid": c[0], "name": c[1], "type": c[2]} for c in columns]
                }
        conn.close()
    except Exception as e:
        print(f"Error analyzing database: {e}")
    return schema

def main():
    print("="*50)
    print("Phase 0: Executing Complete Project Audit")
    print("="*50)
    
    file_stats = count_files_and_loc()
    flask_routes = analyze_flask_routes()
    db_schema = analyze_database()
    
    report = f"# QualiVision AI — Codebase Audit Report\n\n"
    report += f"**Audit Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    report += "## 1. File Statistics & LOC\n\n"
    report += "| Extension | File Count | Lines of Code |\n"
    report += "|---|---|---|\n"
    for ext, stat in sorted(file_stats.items()):
        report += f"| `{ext}` | {stat['count']} | {stat['loc']:,} |\n"
        
    report += "\n## 2. Flask API Routes\n\n"
    report += "| Blueprint | Methods | Path | Function |\n"
    report += "|---|---|---|---|\n"
    for r in sorted(flask_routes, key=lambda x: (x['blueprint'], x['path'])):
        methods = ", ".join(r['methods'])
        report += f"| `{r['blueprint']}` | `{methods}` | `{r['path']}` | `{r['function']}` |\n"
        
    report += "\n## 3. Database Schema\n\n"
    if not db_schema:
        report += "No SQLite database found or readable at `database/smartcam.db`.\n"
    else:
        for table, data in db_schema.items():
            report += f"### Table: `{table}`\n"
            report += "| Column | Type |\n"
            report += "|---|---|\n"
            for col in data['columns']:
                report += f"| `{col['name']}` | `{col['type']}` |\n"
            report += "\n"
            
    report += "\n## 4. Documentation Coverage Assessment\n\n"
    report += "- [x] Codebase audited successfully.\n"
    report += "- [ ] API Documentation generated.\n"
    report += "- [ ] DB Schema documented.\n"
    report += "- [ ] UI Screenshots captured.\n"
    
    AUDIT_REPORT_PATH.write_text(report, encoding='utf-8')
    print(f"✅ Audit complete. Report saved to {AUDIT_REPORT_PATH.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
