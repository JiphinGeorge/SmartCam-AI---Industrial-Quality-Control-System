import os

routes_dir = 'app/routes'
for filename in os.listdir(routes_dir):
    if filename.endswith('.py'):
        filepath = os.path.join(routes_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
        if "url_for('auth.login')" in content:
            new_content = content.replace("url_for('auth.login')", "url_for('auth_bp.login')")
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"Fixed {filename}")
