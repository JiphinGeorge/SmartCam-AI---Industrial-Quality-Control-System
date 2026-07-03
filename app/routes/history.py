from flask import Blueprint, render_template
from flask_login import login_required

history_bp = Blueprint('history', __name__)

@history_bp.route('/history')
@login_required
def index():
    q = request.args.get('q', '')
    return render_template('history.html', q=q)
