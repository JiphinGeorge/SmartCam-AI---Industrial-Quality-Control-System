import urllib.request
import re
import json

url = "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzAwMDY1NWJhZDM0NTdmYWYwOTI1Yzc1MGI3MjdjMjVjEgsSBxD0zoT5hAEYAZIBJAoKcHJvamVjdF9pZBIWQhQxMjEzMTAxNzMzOTUzNzE0NjYwMQ&filename=&opi=89354086"
print("Downloading Light Theme HTML...")
html = urllib.request.urlopen(url).read().decode('utf-8')

# Extract colors dict from the tailwind config in the HTML
color_match = re.search(r'"colors":\s*(\{.*?\})', html, re.DOTALL)
if not color_match:
    print("Could not find colors in light theme HTML")
    exit(1)

colors_json_str = color_match.group(1)
# Clean up JSON if necessary
colors_json_str = re.sub(r',\s*\}', '}', colors_json_str)

try:
    colors_dict = json.loads(colors_json_str)
except Exception as e:
    # Try eval as fallback
    try:
        colors_dict = eval(colors_json_str)
    except Exception as e2:
        print("Failed to parse colors dict", e2)
        exit(1)

# Read base.html
with open('app/templates/base.html', 'r', encoding='utf-8') as f:
    base_html = f.read()

# Find the :root block
root_match = re.search(r':root\s*\{([^}]*)\}', base_html, re.DOTALL)
if not root_match:
    print("Could not find :root block in base.html")
    exit(1)

# Generate new :root css
new_root_css = ""
for name, hex_code in colors_dict.items():
    new_root_css += f"            --color-{name}: {hex_code};\n"

new_base_html = base_html[:root_match.start(1)] + "\n" + new_root_css + "        " + base_html[root_match.end(1):]

with open('app/templates/base.html', 'w', encoding='utf-8') as f:
    f.write(new_base_html)

print("Successfully injected accurate Light Theme colors from Stitch into :root!")
