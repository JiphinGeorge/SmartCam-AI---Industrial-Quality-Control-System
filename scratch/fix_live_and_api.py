with open('app/templates/live_monitor.html', 'a') as f:
    f.write("{% endblock %}\n")

with open('app/routes/api.py', 'r') as f:
    content = f.read()

api_additions = """
@api_bp.route('/analytics')
def analytics_data():
    return jsonify({"status": "success", "data": []})

@api_bp.route('/history')
def history_data():
    return jsonify({"status": "success", "data": []})
"""

if "def analytics_data()" not in content:
    content = content.replace("api_bp = Blueprint('api', __name__)", "api_bp = Blueprint('api', __name__)\n" + api_additions)
    with open('app/routes/api.py', 'w') as f:
        f.write(content)
