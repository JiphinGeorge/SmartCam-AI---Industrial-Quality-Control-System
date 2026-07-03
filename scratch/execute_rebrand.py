import os
import glob
import re

# We operate in the workspace root
base_dir = r"d:\Antigravity Projects\Smart-Cam Live"

# Replacements mapped longest-to-shortest
replacements = {
    "SmartCam AI Industrial Dashboard": "QualiVision Industrial Dashboard",
    "SmartCam Industrial Dashboard": "QualiVision Industrial Dashboard",
    "SmartCam Industrial Quality Control System": "QualiVision Industrial Quality Control System",
    "SmartCam AI Dashboard": "QualiVision AI Dashboard",
    "SmartCam Dashboard": "QualiVision AI Dashboard",
    "SmartCam AI": "QualiVision AI",
    "SmartCam Live": "QualiVision",
    "SmartCam QC": "QualiVision",
    "SmartCam Project": "QualiVision Project",
    "Smart Cam": "QualiVision",
    "SmartCam": "QualiVision"
}

# Add some specific about page texts just in case
replacements["SmartCam AI Industrial Systems"] = "QualiVision AI Industrial Systems"

excluded_dirs = ["venv310", "venv", ".git", "__pycache__", "node_modules", "dataset", "dataset_old", "dataset_original", "logs", "models", "scratch"]
excluded_extensions = [".pyc", ".db", ".sqlite3", ".jpg", ".jpeg", ".png", ".mp4", ".avi", ".h5", ".keras", ".pb", ".ico"]

def should_process(file_path):
    for ed in excluded_dirs:
        if f"\\{ed}\\" in file_path or file_path.endswith(f"\\{ed}"):
            return False
    for ext in excluded_extensions:
        if file_path.endswith(ext):
            return False
    return True

all_files = []
for root, dirs, files in os.walk(base_dir):
    # filter dirs
    dirs[:] = [d for d in dirs if d not in excluded_dirs]
    for file in files:
        full_path = os.path.join(root, file)
        if should_process(full_path):
            all_files.append(full_path)

total_replacements = 0
files_modified = 0

for file_path in all_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        # Might be a binary file not caught by extension filter
        continue
    
    original_content = content
    local_replacements = 0
    
    # Apply replacements in order
    for old, new in replacements.items():
        if old in content:
            count = content.count(old)
            local_replacements += count
            total_replacements += count
            content = content.replace(old, new)
            
    if local_replacements > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        files_modified += 1

print(f"Rebranding Complete!")
print(f"Files Modified: {files_modified}")
print(f"Total Replacements: {total_replacements}")
