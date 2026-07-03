import re

html = open('app/templates/knowledge_center.html', encoding='utf-8').read()
depth = 0
for match in re.finditer(r'<(div|/div)\b', html):
    tag = match.group(1)
    if tag == 'div':
        depth += 1
    else:
        depth -= 1

print(f"Final depth: {depth}")
