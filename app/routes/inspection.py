from flask import Blueprint, render_template
from flask_login import login_required

inspection_bp = Blueprint('inspection', __name__)

@inspection_bp.route('/inspection')
@login_required
def index():
    return render_template('inspection.html')
