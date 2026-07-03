from flask import Blueprint, render_template

knowledge_bp = Blueprint('knowledge', __name__)

@knowledge_bp.route('/knowledge')
def index():
    return render_template('knowledge_center.html')
