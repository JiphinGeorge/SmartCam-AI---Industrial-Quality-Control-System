from flask import Blueprint, render_template

inspection_bp = Blueprint('inspection', __name__)

@inspection_bp.route('/inspection')
def index():
    return render_template('inspection.html')
