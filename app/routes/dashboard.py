from flask import Blueprint, render_template
from flask_login import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    return render_template('dashboard.html')

@dashboard_bp.route('/notifications')
@login_required
def notifications():
    return render_template('notifications.html')

@dashboard_bp.route('/logs')
@login_required
def logs():
    return render_template('logs.html')
