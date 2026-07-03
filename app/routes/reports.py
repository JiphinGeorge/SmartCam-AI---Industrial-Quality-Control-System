from flask import Blueprint, render_template

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
def index():
    return render_template('reports.html')
