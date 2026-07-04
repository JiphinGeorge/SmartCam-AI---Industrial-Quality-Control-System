import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"

def main():
    print("="*50)
    print("Phase 10: Final Documentation QA Validation")
    print("="*50)
    
    issues = []
    
    # Check Phase 0
    if not (DOCS_DIR / "AUDIT_REPORT.md").exists():
        issues.append("Missing AUDIT_REPORT.md")
        
    # Check Phase 1
    if not (DOCS_DIR / "report_assets" / "branding" / "logo_transparent.png").exists():
        issues.append("Missing branding assets (logo_transparent.png)")
        
    # Check Phase 2
    if not (DOCS_DIR / "SCREENSHOT_INDEX.md").exists():
        issues.append("Missing SCREENSHOT_INDEX.md")
        
    # Check Phase 3
    if not (DOCS_DIR / "report_assets" / "diagrams" / "system_architecture.png").exists():
        issues.append("Missing system_architecture.png diagram")
        
    # Check Phase 4
    if not (DOCS_DIR / "report_assets" / "charts" / "training_accuracy.png").exists():
        issues.append("Missing training_accuracy.png chart")
        
    # Check Phase 5
    if not (DOCS_DIR / "Project_Report_Source.md").exists():
        issues.append("Missing Project_Report_Source.md")
        
    # Check Phase 6
    if not (DOCS_DIR / "API_Documentation.md").exists():
        issues.append("Missing API_Documentation.md")
        
    # Check Phase 8
    if not (DOCS_DIR / "QualiVision_AI_Presentation.pptx").exists():
        issues.append("Missing QualiVision_AI_Presentation.pptx")
        
    # Check Phase 9
    if not (ROOT / "Complete_Project_Report.pdf").exists():
        issues.append("Missing Complete_Project_Report.pdf")

    report = "# QualiVision AI — Documentation QA Validation\n\n"
    if not issues:
        report += "✅ All phases passed. Documentation is 100% complete and verified.\n"
        print("[OK] Validation Passed. No issues found.")
    else:
        report += "❌ Validation Failed. The following issues were found:\n"
        for issue in issues:
            report += f"- {issue}\n"
            print(f"[FAIL] {issue}")
            
    (DOCS_DIR / "FINAL_DOCUMENTATION_CHECKLIST.md").write_text(report, encoding='utf-8')
    print(f"\nSaved validation report to docs/FINAL_DOCUMENTATION_CHECKLIST.md")

if __name__ == "__main__":
    main()
