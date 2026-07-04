import os
import sys
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SCREENSHOT_DIR = ROOT / "docs" / "report_assets" / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
INDEX_PATH = ROOT / "docs" / "SCREENSHOT_INDEX.md"

def capture_screenshots():
    print("="*50)
    print("Phase 2: Automated Screenshot Capture")
    print("="*50)

    # 1. Start the Flask App
    print("Starting Flask application on port 5000...")
    env = os.environ.copy()
    env["FLASK_APP"] = "app.py"
    env["FLASK_ENV"] = "development"
    
    python_exe = str(ROOT / "venv310" / "Scripts" / "python.exe")
    if not os.path.exists(python_exe):
        python_exe = "python"
        
    process = subprocess.Popen(
        [python_exe, "app.py"],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    time.sleep(5)  # Wait for Flask to boot

    screenshots_taken = []
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            # Desktop Viewport
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()
            
            base_url = "http://localhost:5000"
            
            def snap(name, path, full_page=False):
                page.goto(f"{base_url}{path}")
                time.sleep(1) # Wait for animations/charts
                filename = f"{name}.png"
                filepath = SCREENSHOT_DIR / filename
                page.screenshot(path=str(filepath), full_page=full_page)
                screenshots_taken.append(filename)
                print(f"[OK] Captured {filename}")

            # 1. Login Page
            page.goto(f"{base_url}/login")
            time.sleep(1)
            filepath = SCREENSHOT_DIR / "01_login.png"
            page.screenshot(path=str(filepath))
            screenshots_taken.append("01_login.png")
            print("[OK] Captured 01_login.png")
            
            # Perform Login
            page.fill("input[name='username']", "admin")
            page.fill("input[name='password']", "admin123")
            page.click("button[type='submit']")
            page.wait_for_url(f"{base_url}/dashboard")
            
            # 2. Dashboard
            time.sleep(2) # Charts take a moment
            filepath = SCREENSHOT_DIR / "02_dashboard.png"
            page.screenshot(path=str(filepath), full_page=True)
            screenshots_taken.append("02_dashboard.png")
            print("[OK] Captured 02_dashboard.png")
            
            # Core Pages
            snap("03_live_monitoring", "/live")
            snap("04_inspection_studio", "/inspection")
            snap("05_history", "/history")
            snap("06_analytics", "/analytics", full_page=True)
            snap("07_reports", "/reports")
            snap("08_dataset_repository", "/dataset", full_page=True)
            snap("09_model_management", "/models")
            snap("10_knowledge_center", "/knowledge")
            snap("11_settings", "/settings")
            snap("12_profile", "/profile")
            
            # Dark Mode toggle (assuming there is a theme toggle button or class)
            # QualiVision AI implemented a dark mode class on html or body
            page.evaluate("document.documentElement.classList.add('dark'); document.documentElement.classList.remove('light'); localStorage.setItem('theme', 'dark');")
            time.sleep(1)
            snap("13_dark_mode_dashboard", "/dashboard")
            
            # Responsive Mobile Viewport
            mobile_context = browser.new_context(viewport={"width": 375, "height": 812}, is_mobile=True)
            mobile_page = mobile_context.new_page()
            mobile_page.goto(f"{base_url}/dashboard")
            time.sleep(1)
            filepath = SCREENSHOT_DIR / "14_responsive_mobile.png"
            mobile_page.screenshot(path=str(filepath))
            screenshots_taken.append("14_responsive_mobile.png")
            print("[OK] Captured 14_responsive_mobile.png")
            
            # Error Pages
            snap("15_error_404", "/this-page-does-not-exist")
            
            browser.close()
            
    except Exception as e:
        print(f"Error during playwright automation: {e}")
    finally:
        print("Shutting down Flask server...")
        process.terminate()
        process.wait()
        
    # Generate INDEX
    index_content = "# QualiVision AI — Screenshot Index\n\n"
    for img in sorted(screenshots_taken):
        index_content += f"- `report_assets/screenshots/{img}`\n"
        
    INDEX_PATH.write_text(index_content, encoding='utf-8')
    print(f"\nAll screenshots saved to {SCREENSHOT_DIR.relative_to(ROOT)}")
    print(f"Index saved to {INDEX_PATH.relative_to(ROOT)}")

if __name__ == "__main__":
    capture_screenshots()
