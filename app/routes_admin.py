from flask import Blueprint, render_template, session, redirect, url_for, request, flash, current_app as app
from bson.objectid import ObjectId
import json

# IMPORTANT — Blueprint must be defined BEFORE any routes
admin_bp = Blueprint('admin', __name__)

# ---------------------------
# Authentication decorator
# ---------------------------
def login_required(fn):
    def wrapper(*a, **k):
        if session.get('role') != 'dept_head':
            flash('Please login as department head', 'warning')
            return redirect(url_for('auth.login'))
        return fn(*a, **k)
    wrapper.__name__ = fn.__name__
    return wrapper


# ---------------------------
# Admin Dashboard
# ---------------------------
@admin_bp.route('/dashboard')
@login_required
def dashboard():

    # Fetch all fee structure documents
    fee_structs = list(
        app.db.fee_structures.find()
        .sort([('category', 1), ('version', -1)])
    )

    # Calculate totals safely
    total_categories = len(fee_structs)
    total_components = sum(
        len(fs.get('components', [])) for fs in fee_structs
    )

    versions = [
        fs.get('version') for fs in fee_structs
        if fs.get('version') is not None
    ]
    latest_version = max(versions) if versions else None

    return render_template(
        'admin/dashboard.html',
        fee_structs=fee_structs,
        total_categories=total_categories,
        total_components=total_components,
        latest_version=latest_version
    )


# ---------------------------
# Fee Structure Management
# ---------------------------
@admin_bp.route('/fee-structures', methods=['GET', 'POST'])
@login_required
def fee_structures():

    # Save fee structure
    if request.method == 'POST':
        category = request.form['category'].strip()
        components_raw = request.form['components']

        try:
            components = json.loads(components_raw)
        except Exception:
            components = []

        # Determine next version number
        version = (
            app.db.fee_structures.count_documents({'category': category}) or 0
        ) + 1

        app.db.fee_structures.insert_one({
            'category': category,
            'components': components,
            'version': version
        })

        flash('Fee structure saved successfully!', 'success')
        return redirect(url_for('admin.fee_structures'))

    # Show all fee structures
    structs = list(app.db.fee_structures.find())

    return render_template(
        'admin/fee_structures.html',
        fee_structs=structs
    )
