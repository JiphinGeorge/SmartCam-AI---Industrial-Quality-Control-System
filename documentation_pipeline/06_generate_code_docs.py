import os
import ast
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
API_DOC_PATH = DOCS_DIR / "API_Documentation.md"
DB_DOC_PATH = DOCS_DIR / "Database_Documentation.md"

def generate_api_docs():
    routes = []
    routes_dir = ROOT / "app" / "routes"
    
    if routes_dir.exists():
        for py_file in routes_dir.glob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        docstring = ast.get_docstring(node) or "No description provided."
                        for dec in node.decorator_list:
                            if isinstance(dec, ast.Call) and hasattr(dec.func, 'attr') and dec.func.attr == 'route':
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
                                        "function": node.name,
                                        "docstring": docstring
                                    })
                                except Exception:
                                    pass
            except Exception:
                pass
                
    md = "# QualiVision AI — API Documentation\n\n"
    for r in sorted(routes, key=lambda x: x['path']):
        methods = ", ".join(r['methods'])
        md += f"## `{methods}` {r['path']}\n"
        md += f"- **Blueprint**: `{r['blueprint']}`\n"
        md += f"- **Function**: `{r['function']}`\n\n"
        md += f"**Description:**\n{r['docstring']}\n\n"
        md += "---\n\n"
        
    API_DOC_PATH.write_text(md, encoding='utf-8')
    print(f"[OK] Generated {API_DOC_PATH.name}")

def generate_db_docs():
    db_path = ROOT / "database" / "smartcam.db"
    md = "# QualiVision AI — Database Documentation\n\n"
    
    if not db_path.exists():
        md += "Database file not found."
    else:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
        tables = cursor.fetchall()
        
        for name, sql in tables:
            md += f"## Table: `{name}`\n\n"
            md += f"**Schema:**\n```sql\n{sql}\n```\n\n"
            
            cursor.execute(f"PRAGMA table_info({name})")
            columns = cursor.fetchall()
            md += "| CID | Name | Type | NotNull | Default | PK |\n"
            md += "|---|---|---|---|---|---|\n"
            for c in columns:
                md += f"| {c[0]} | `{c[1]}` | `{c[2]}` | {c[3]} | {c[4]} | {c[5]} |\n"
            md += "\n---\n\n"
        conn.close()
        
    DB_DOC_PATH.write_text(md, encoding='utf-8')
    print(f"[OK] Generated {DB_DOC_PATH.name}")

def main():
    print("="*50)
    print("Phase 6: Generating Code & DB Documentation")
    print("="*50)
    generate_api_docs()
    generate_db_docs()

if __name__ == "__main__":
    main()
