import os
import re

template_dir = 'app/templates'

for filename in os.listdir(template_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(template_dir, filename)
        with open(filepath, 'r') as f:
            lines = f.readlines()

        new_lines = []
        i = 0
        changed = False
        while i < len(lines):
            # If we are in the first 20 lines and see {% block scripts %}
            if i < 20 and "{% block scripts %}" in lines[i]:
                # Skip this line and the next two lines (the script and endblock)
                # But wait, what if there's a blank line? 
                # Let's just skip until {% endblock %}
                changed = True
                i += 1
                while i < len(lines) and "{% endblock %}" not in lines[i]:
                    i += 1
                if i < len(lines):
                    # We found the endblock for the scripts, skip it too
                    i += 1
                continue
            
            new_lines.append(lines[i])
            i += 1

        if changed:
            with open(filepath, 'w') as f:
                f.writelines(new_lines)
            print(f"Fixed {filename}")
