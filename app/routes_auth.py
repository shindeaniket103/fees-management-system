from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app as app
from werkzeug.security import check_password_hash
from bson.objectid import ObjectId

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        role = request.form.get('role','student')
        user = app.db.users.find_one({'email': email, 'role': role})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['role'] = user['role']
            session['name'] = user.get('name','')
            flash('Logged in successfully','success')
            if user['role']=='student':
                return redirect(url_for('student.dashboard'))
            if user['role']=='accountant':
                return redirect(url_for('accountant.dashboard'))
            return redirect(url_for('admin.dashboard'))
        flash('Invalid credentials','danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out','info')
    return redirect(url_for('auth.login'))
