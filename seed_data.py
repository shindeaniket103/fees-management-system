from pymongo import MongoClient
from werkzeug.security import generate_password_hash

client = MongoClient("mongodb://localhost:27017/")
db = client["feesdb"]

users = db.users

# Clear existing data to avoid duplicates
users.delete_many({})

# Insert demo users with hashed passwords
users.insert_many([
    {
        "email": "student@example.com",
        "password": generate_password_hash("student123"),
        "role": "student",
        "name": "Demo Student"
    },
    {
        "email": "accountant@example.com",
        "password": generate_password_hash("acct123"),
        "role": "accountant",
        "name": "Demo Accountant"
    },
    {
        "email": "admin@example.com",
        "password": generate_password_hash("admin123"),
        "role": "dept_head",
        "name": "Demo DeptHead"
    }
])

print("✅ Database 'feesdb' seeded successfully with demo users!")
