import asyncio
import os
from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:5000"
SCREENSHOT_DIR = "app/static/images/screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def capture_state(page, filename, width, height, theme="light"):
    await page.set_viewport_size({"width": width, "height": height})
    # Small delay to let animations/charts settle
    await asyncio.sleep(1)
    
    # Simple hack to simulate dark mode if supported by CSS body class
    if theme == "dark":
        await page.evaluate("document.body.classList.add('dark-mode')")
        
    await page.screenshot(path=os.path.join(SCREENSHOT_DIR, filename), full_page=True)
    
    if theme == "dark":
        await page.evaluate("document.body.classList.remove('dark-mode')")
        
    print(f"Captured: {filename}")

async def run():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            record_video_dir=None,
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        async def wait_and_clear(p_page):
            await asyncio.sleep(1.5)
            await p_page.evaluate("let el = document.getElementById('splash-screen'); if(el) el.remove();")

        # 1. Login Page
        await page.goto(f"{BASE_URL}/login")
        await wait_and_clear(page)
        await capture_state(page, "1_login_page.png", 1920, 1080)
        await capture_state(page, "1_login_mobile.png", 375, 812)
        
        # 2. Authenticate
        await page.fill('input[name="username"]', 'admin')
        await page.fill('input[name="password"]', 'password')
        await page.click('button[type="submit"]')
        await page.goto(f"{BASE_URL}/dashboard")
        await wait_and_clear(page)
        
        # 3. Dashboard
        await capture_state(page, "2_dashboard_populated.png", 1920, 1080)
        await capture_state(page, "2_dashboard_dark.png", 1920, 1080, theme="dark")
        await capture_state(page, "2_dashboard_tablet.png", 768, 1024)
        
        # 4. Live Monitoring
        await page.goto(f"{BASE_URL}/live")
        await wait_and_clear(page)
        await capture_state(page, "3_live_monitoring.png", 1920, 1080)
        
        # 5. Inspection Module
        await page.goto(f"{BASE_URL}/inspection")
        await wait_and_clear(page)
        await capture_state(page, "4_inspection_module.png", 1920, 1080)
        
        # 6. Analytics
        await page.goto(f"{BASE_URL}/analytics")
        await wait_and_clear(page)
        await capture_state(page, "5_analytics_charts.png", 1920, 1080)
        
        # 7. History
        await page.goto(f"{BASE_URL}/history")
        await wait_and_clear(page)
        await capture_state(page, "6_inspection_history.png", 1920, 1080)
        
        # 8. Reports
        await page.goto(f"{BASE_URL}/reports")
        await wait_and_clear(page)
        await capture_state(page, "7_reports.png", 1920, 1080)
        
        # 9. Dataset Repository
        await page.goto(f"{BASE_URL}/dataset")
        await wait_and_clear(page)
        await capture_state(page, "8_dataset_repository.png", 1920, 1080)
        
        # 10. Model Management
        await page.goto(f"{BASE_URL}/models")
        await wait_and_clear(page)
        await capture_state(page, "9_model_management.png", 1920, 1080)
        
        # 11. Settings
        await page.goto(f"{BASE_URL}/settings")
        await wait_and_clear(page)
        await capture_state(page, "10_settings.png", 1920, 1080)
        
        # 12. Knowledge Center
        await page.goto(f"{BASE_URL}/knowledge")
        await wait_and_clear(page)
        await capture_state(page, "11_knowledge_center.png", 1920, 1080)
        
        await browser.close()
        
    print("[*] All screenshots generated successfully!")

if __name__ == "__main__":
    asyncio.run(run())
