import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SCRIPTS = [
    "00_audit_project.py",
    "01_brand_assets.py",
    "02_capture_screenshots.py",
    "03_generate_diagrams.py",
    "04_generate_charts.py",
    "05_generate_report.py",
    "06_generate_code_docs.py",
    "07_generate_user_docs.py",
    "08_generate_presentation.py",
    "09_export_documents.py",
    "10_validate_documentation.py",
]

def main():
    print("="*60)
    print("   QualiVision AI — Enterprise Documentation Pipeline")
    print("="*60)
    
    # Check dependencies before running full pipeline
    try:
        import markdown
        import matplotlib
        import seaborn
        from pptx import Presentation
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[ERROR] Missing required Python packages.")
        print("Please run: pip install markdown matplotlib seaborn python-pptx playwright pytest-playwright pdfkit python-docx")
        print("And then: playwright install chromium")
        sys.exit(1)
        
    python_exe = sys.executable
    
    for script in SCRIPTS:
        script_path = ROOT / script
        if not script_path.exists():
            print(f"[WARN] Script {script} not found, skipping...")
            continue
            
        print(f"\n>>> Running {script} ...")
        result = subprocess.run([python_exe, str(script_path)], cwd=str(ROOT.parent))
        
        if result.returncode != 0:
            print(f"[ERROR] {script} failed with exit code {result.returncode}")
            print("Pipeline aborted.")
            sys.exit(result.returncode)
            
    print("\n" + "="*60)
    print("   Documentation Pipeline Executed Successfully!")
    print("="*60)

if __name__ == "__main__":
    main()
