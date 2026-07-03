from flask import Blueprint, render_template
from flask_login import login_required

knowledge_bp = Blueprint('knowledge', __name__)

@knowledge_bp.route('/knowledge')
@login_required
def index():
    return render_template('knowledge_center.html')
