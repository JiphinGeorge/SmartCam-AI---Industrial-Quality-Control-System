import urllib.request
import re
import os

urls = [
    # Knowledge Center (already extracted, but add for completeness)
    "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzAwMDY1NWIzYmE4YTg4NWQwNmRjMDA0YTRjMTc0MTk5EgsSBxD0zoT5hAEYAZIBJAoKcHJvamVjdF9pZBIWQhQxMjEzMTAxNzMzOTUzNzE0NjYwMQ&filename=&opi=89354086",
    # Dataset
    "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzAwMDY1NWIzYmEwMjYwYjkwMWE2MmVjYTM1MDE3MjA1EgsSBxD0zoT5hAEYAZIBJAoKcHJvamVjdF9pZBIWQhQxMjEzMTAxNzMzOTUzNzE0NjYwMQ&filename=&opi=89354086",
    # Config
    "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzAwMDY1NWIzYjk0ZDM4ZjMwMWE2MmVjYTM1MDE3MjA1EgsSBxD0zoT5hAEYAZIBJAoKcHJvamVjdF9pZBIWQhQxMjEzMTAxNzMzOTUzNzE0NjYwMQ&filename=&opi=89354086",
    # Model Mgmt
    "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzAwMDY1NWIzYmE2YWEwOTAwNmRjMDA0YTRjMTc0MTk5EgsSBxD0zoT5hAEYAZIBJAoKcHJvamVjdF9pZBIWQhQxMjEzMTAxNzMzOTUzNzE0NjYwMQ&filename=&opi=89354086",
    # Reporting
    "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzAwMDY1NWIzYjQxNjMzNGUwNDMxMDNiY2NlMGI1OTE1EgsSBxD0zoT5hAEYAZIBJAoKcHJvamVjdF9pZBIWQhQxMjEzMTAxNzMzOTUzNzE0NjYwMQ&filename=&opi=89354086",
    # History
    "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzAwMDY1NWIzYjVjZTQ5MjIwOTI1YzdkNTcyMjIzNDMyEgsSBxD0zoT5hAEYAZIBJAoKcHJvamVjdF9pZBIWQhQxMjEzMTAxNzMzOTUzNzE0NjYwMQ&filename=&opi=89354086",
    # Analytics
    "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzAwMDY1NWIzYjQ4ZWZiM2MwODg0YzdmZTllMmE5OWRmEgsSBxD0zoT5hAEYAZIBJAoKcHJvamVjdF9pZBIWQhQxMjEzMTAxNzMzOTUzNzE0NjYwMQ&filename=&opi=89354086",
    # Live Monitor
    "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzAwMDY1NWIzYjBmMjBlYzMwOTI1Yzc5ODMwMWNlYWVlEgsSBxD0zoT5hAEYAZIBJAoKcHJvamVjdF9pZBIWQhQxMjEzMTAxNzMzOTUzNzE0NjYwMQ&filename=&opi=89354086",
    # Dashboard
    "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzAwMDY1NWIzYjBmYzZlZjYwNDczNTZjMjM1MzU4Yjg1EgsSBxD0zoT5hAEYAZIBJAoKcHJvamVjdF9pZBIWQhQxMjEzMTAxNzMzOTUzNzE0NjYwMQ&filename=&opi=89354086",
    # Inspection
    "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzAwMDY1NWIzYjA2MDFmNGEwNDMxMDNiY2NlMGI1OTE1EgsSBxD0zoT5hAEYAZIBJAoKcHJvamVjdF9pZBIWQhQxMjEzMTAxNzMzOTUzNzE0NjYwMQ&filename=&opi=89354086",
    # Animated Inspection
    "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzAwMDY1NWIzYzdlY2Q0MmIwMDMwM2UxMmIzMDIxNjJkEgsSBxD0zoT5hAEYAZIBJAoKcHJvamVjdF9pZBIWQhQxMjEzMTAxNzMzOTUzNzE0NjYwMQ&filename=&opi=89354086"
]

all_css = set()

for i, url in enumerate(urls):
    print(f"Downloading {i+1}/{len(urls)}...")
    try:
        html = urllib.request.urlopen(url).read().decode('utf-8')
        style_blocks = re.findall(r'<style(?![^>]*id="tailwind-config")[^>]*>(.*?)</style>', html, re.DOTALL)
        for block in style_blocks:
            block = block.strip()
            if block:
                all_css.add(block)
    except Exception as e:
        print(f"Error fetching URL {i+1}: {e}")

# Also add the classes we know were used in Inspection Studio since we replaced them manually,
# just to make sure if we ever use them again they work!
# Wait, actually we manually fixed the inspection studio donut chart, so those custom classes are no longer needed there.
# But it's good to have them if the user explicitly wants "all the missing css".
# Let's just output what Stitch gave us.

final_css = "\n\n/* STITCH CUSTOM CSS AGGREGATED FROM ALL 11 SCREENS */\n\n" + "\n\n".join(all_css)

os.makedirs(r"d:\Antigravity Projects\Smart-Cam Live\app\static\css", exist_ok=True)
css_path = r"d:\Antigravity Projects\Smart-Cam Live\app\static\css\stitch_custom.css"

with open(css_path, "w", encoding="utf-8") as f:
    f.write(final_css)
    
print("Saved aggregated Stitch CSS to stitch_custom.css!")
