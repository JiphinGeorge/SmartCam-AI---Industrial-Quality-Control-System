import os

def fix_analytics():
    with open('app/templates/analytics.html', 'r') as f:
        content = f.read()
    content = content.replace(
        "{% set active_page = 'analytics' %}\n{% endblock %}\n{% endblock %}",
        "{% set active_page = 'analytics' %}\n{% block title %}Analytics - SmartCam AI{% endblock %}\n{% block body_class %}bg-background text-on-background font-body-md min-h-screen flex overflow-hidden selection:bg-primary selection:text-on-primary{% endblock %}"
    )
    with open('app/templates/analytics.html', 'w') as f:
        f.write(content)

def fix_history():
    with open('app/templates/history.html', 'r') as f:
        content = f.read()
    if "{% block content %}" in content and not content.endswith("{% endblock %}"):
        content += "\n{% endblock %}\n"
    with open('app/templates/history.html', 'w') as f:
        f.write(content)

def fix_live_monitor():
    with open('app/templates/live_monitor.html', 'r') as f:
        content = f.read()
    if "{% block content %}" in content and not content.endswith("{% endblock %}\n"):
        content += "\n{% endblock %}\n"
    with open('app/templates/live_monitor.html', 'w') as f:
        f.write(content)

def fix_inspection():
    with open('app/templates/inspection.html', 'r') as f:
        content = f.read()
    # Replace empty blocks at the top
    top_bad = "{% block title %}Inspection Module - SmartCam AI\n\n{% endblock %}\n{% block body_class %}bg-background text-on-background font-body-md min-h-screen selection:bg-primary selection:text-on-primary\n\n{% endblock %}"
    top_good = "{% block title %}Inspection Module - SmartCam AI{% endblock %}\n{% block body_class %}bg-background text-on-background font-body-md min-h-screen selection:bg-primary selection:text-on-primary{% endblock %}"
    content = content.replace(top_bad, top_good)
    with open('app/templates/inspection.html', 'w') as f:
        f.write(content)

if __name__ == "__main__":
    fix_analytics()
    fix_history()
    fix_live_monitor()
    fix_inspection()
    print("Fixed template blocks")
