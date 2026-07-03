import urllib.request
import re
import os

url = "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzAwMDY1NWIzYmE4YTg4NWQwNmRjMDA0YTRjMTc0MTk5EgsSBxD0zoT5hAEYAZIBJAoKcHJvamVjdF9pZBIWQhQxMjEzMTAxNzMzOTUzNzE0NjYwMQ&filename=&opi=89354086"

print("Downloading HTML...")
html = urllib.request.urlopen(url).read().decode('utf-8')

style_blocks = re.findall(r'<style(?![^>]*id="tailwind-config")[^>]*>(.*?)</style>', html, re.DOTALL)
all_css = set()

for block in style_blocks:
    block = block.strip()
    if block:
        all_css.add(block)

final_css = "\n\n/* STITCH CUSTOM CSS */\n\n" + "\n\n".join(all_css)

os.makedirs(r"d:\Antigravity Projects\Smart-Cam Live\app\static\css", exist_ok=True)
css_path = r"d:\Antigravity Projects\Smart-Cam Live\app\static\css\stitch_custom.css"

with open(css_path, "w", encoding="utf-8") as f:
    f.write(final_css)
    
print("Saved Stitch CSS to stitch_custom.css!")
