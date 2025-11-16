from flask import Flask
from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    # -----------------------------
    # SECRET KEY
    # -----------------------------
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')

    # -----------------------------
    # DATABASE SETUP
    # -----------------------------
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/feesdb')
    client = MongoClient(mongo_uri)

    # If URI does NOT specify a DB name, fallback to 'feesdb'
    db_name = mongo_uri.rsplit('/', 1)[-1] or 'feesdb'
    app.db = client[db_name]

    # -----------------------------
    # CREATE DEFAULT USERS (ONCE)
    # -----------------------------
    with app.app_context():
        users = app.db.users
        if users.count_documents({}) == 0:
            users.insert_many([
                {
                    'email': 'student@example.com',
                    'password': generate_password_hash('student123'),
                    'role': 'student',
                    'name': 'Demo Student'
                },
                {
                    'email': 'accountant@example.com',
                    'password': generate_password_hash('acct123'),
                    'role': 'accountant',
                    'name': 'Demo Accountant'
                },
                {
                    'email': 'admin@example.com',
                    'password': generate_password_hash('admin123'),
                    'role': 'dept_head',
                    'name': 'Demo DeptHead'
                }
            ])
            print("✔ Default demo users created.")

    # -----------------------------
    # BLUEPRINTS IMPORT
    # -----------------------------
    from .routes_auth import auth_bp
    from .routes_student import student_bp
    from .routes_accountant import accountant_bp
    from .routes_admin import admin_bp  # MUST be after Blueprint is defined

    # -----------------------------
    # BLUEPRINT REGISTRATION
    # -----------------------------
    app.register_blueprint(auth_bp)                         # /login, /logout
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(accountant_bp, url_prefix='/accountant')
    app.register_blueprint(admin_bp, url_prefix='/admin')   # /admin/dashboard

    return app
