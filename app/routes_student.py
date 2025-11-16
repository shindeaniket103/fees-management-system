from flask import Blueprint, render_template, session, redirect, url_for, request, flash, current_app as app
from bson.objectid import ObjectId
from datetime import datetime

student_bp = Blueprint('student', __name__, template_folder='templates')

def login_required(fn):
    def wrapper(*a, **k):
        if session.get('role') != 'student':
            flash('Please login as student', 'warning')
            return redirect(url_for('auth.login'))
        return fn(*a, **k)
    wrapper.__name__ = fn.__name__
    return wrapper

@student_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = ObjectId(session['user_id'])
    student = app.db.students.find_one({'user_id': user_id})

    # ✅ Prevent crash if student record is missing
    if not student:
        flash("Student profile not found in database. Please contact admin.", "danger")
        return redirect(url_for("auth.logout"))

    payments = list(app.db.payments.find({'student_id': student['_id']}).sort('created_at', -1))
    paid = sum(p.get('amount', 0) for p in payments)

    fee_doc = app.db.fee_structures.find_one(
        {'category': student.get('category', 'General')},
        sort=[('version', -1)]
    ) or {'components': []}

    total_fee = sum(c['amount'] for c in fee_doc.get('components', []))
    pending = max(total_fee - paid, 0)

    return render_template(
        'student/dashboard.html',
        student=student,
        payments=payments,
        total_fee=total_fee,
        paid=paid,
        pending=pending
    )

@student_bp.route('/pay', methods=['GET', 'POST'])
@login_required
def pay():
    user_id = ObjectId(session['user_id'])
    student = app.db.students.find_one({'user_id': user_id})

    # ✅ Prevent crash if student record is missing
    if not student:
        flash("Student profile not found in database. Please contact admin.", "danger")
        return redirect(url_for("auth.logout"))

    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
        except ValueError:
            flash('Invalid amount entered', 'danger')
            return redirect(url_for('student.pay'))

        if amount <= 0:
            flash('Amount must be greater than zero', 'danger')
            return redirect(url_for('student.pay'))

        payment = {
            'student_id': student['_id'],
            'student_name': student.get('name', 'Unknown'),
            'category': student.get('category', 'General'),
            'amount': amount,
            'method': 'MockGateway',
            'status': 'success',
            'created_at': datetime.utcnow()
        }

        pid = app.db.payments.insert_one(payment).inserted_id

        app.db.receipts.insert_one({
            'payment_id': pid,
            'student_id': student['_id'],
            'receipt_no': f'R-{str(pid)[:8]}',
            'issued_at': datetime.utcnow()
        })

        flash('✅ Payment recorded (mock)', 'success')
        return redirect(url_for('student.dashboard'))

    return render_template('student/pay.html', student=student)
