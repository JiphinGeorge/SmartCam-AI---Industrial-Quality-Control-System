from flask import Blueprint, render_template
from flask_login import login_required

live_bp = Blueprint('live', __name__)

@live_bp.route('/live')
@login_required
def index():
    return render_template('live_monitor.html')
