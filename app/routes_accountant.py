from flask import Blueprint, render_template, session, redirect, url_for, request, flash, current_app as app
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash
from datetime import datetime

accountant_bp = Blueprint('accountant', __name__, template_folder='templates')

# ------------------- Helper -------------------
def login_required(fn):
    def wrapper(*a, **k):
        if session.get('role') != 'accountant':
            flash('Please login as accountant', 'warning')
            return redirect(url_for('auth.login'))
        return fn(*a, **k)
    wrapper.__name__ = fn.__name__
    return wrapper

# ------------------- Accountant Dashboard -------------------
@accountant_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # Handle new student creation
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        category = request.form.get('category', 'General')
        password = request.form.get('password', 'student123')

        # Prevent duplicate user
        if app.db.users.find_one({'email': email}):
            flash('Email already exists. Try another.', 'danger')
        else:
            # Create user login
            user_id = app.db.users.insert_one({
                'email': email,
                'password': generate_password_hash(password),
                'role': 'student',
                'name': name
            }).inserted_id

            # Create student profile
            app.db.students.insert_one({
                'user_id': user_id,
                'name': name,
                'email': email,
                'category': category,
                'created_at': datetime.utcnow()
            })

            flash('✅ Student added successfully!', 'success')
            return redirect(url_for('accountant.dashboard'))

    # Summary section
    total_students = app.db.students.count_documents({})
    total_paid = sum(p.get('amount', 0) for p in app.db.payments.find({}))

    total_fees = 0
    for s in app.db.students.find():
        fee_doc = app.db.fee_structures.find_one(
            {'category': s.get('category', 'General')},
            sort=[('version', -1)]
        )
        if fee_doc:
            total_fees += sum(c['amount'] for c in fee_doc.get('components', []))

    total_pending = max(total_fees - total_paid, 0)

    # Recent payments (join with student name)
    payments = list(app.db.payments.find().sort('_id', -1).limit(20))
    for p in payments:
        student = app.db.students.find_one({'_id': p.get('student_id')})
        p['student_name'] = student['name'] if student else 'Unknown'

    return render_template(
        'accountant/dashboard.html',
        total_students=total_students,
        total_paid=total_paid,
        total_pending=total_pending,
        payments=payments
    )
# ------------------- Manage Students -------------------
@accountant_bp.route('/students', methods=['GET', 'POST'])
@login_required
def students():
    # Search/filter
    query = request.args.get('q', '').strip().lower()
    category_filter = request.args.get('category', '')

    students = list(app.db.students.find())

    # Apply filters
    if query:
        students = [s for s in students if query in s.get('name', '').lower() or query in s.get('email', '').lower()]
    if category_filter:
        students = [s for s in students if s.get('category', '') == category_filter]

    # Sort by newest first
    students.sort(key=lambda s: s.get('created_at', datetime.utcnow()), reverse=True)

    return render_template('accountant/students.html', students=students, query=query, category_filter=category_filter)


# ------------------- Edit Student -------------------
@accountant_bp.route('/students/edit/<student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    student = app.db.students.find_one({'_id': ObjectId(student_id)})
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('accountant.students'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        category = request.form.get('category', 'General')

        app.db.students.update_one({'_id': ObjectId(student_id)}, {'$set': {
            'name': name,
            'email': email,
            'category': category
        }})

        app.db.users.update_one({'_id': student['user_id']}, {'$set': {
            'name': name,
            'email': email
        }})

        flash('✅ Student details updated successfully!', 'success')
        return redirect(url_for('accountant.students'))

    return render_template('accountant/edit_student.html', student=student)


# ------------------- Delete Student -------------------
@accountant_bp.route('/students/delete/<student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    student = app.db.students.find_one({'_id': ObjectId(student_id)})
    if not student:
        flash('Student not found.', 'danger')
    else:
        app.db.users.delete_one({'_id': student['user_id']})
        app.db.students.delete_one({'_id': ObjectId(student_id)})
        app.db.payments.delete_many({'student_id': ObjectId(student_id)})
        flash('🗑️ Student deleted successfully.', 'info')

    return redirect(url_for('accountant.students'))
