from flask import Blueprint, render_template, request, session, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('dashboard.index'))
        else:
            return render_template('login.html', error="Invalid password")
    
    if session.get('admin_logged_in'):
        return redirect(url_for('dashboard.index'))
        
    return render_template('login.html', error=None)

@auth_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
def profile():
    return render_template('profile.html')
