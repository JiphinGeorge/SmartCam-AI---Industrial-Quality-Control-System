import os
import glob

template_dir = r"d:\Antigravity Projects\Smart-Cam Live\app\templates"
files = glob.glob(os.path.join(template_dir, "**", "*.html"), recursive=True)

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "SmartCam AI" in content:
        content = content.replace("SmartCam AI", "QualiVision")
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)

print("Updated text branding from SmartCam AI to QualiVision across all templates!")
