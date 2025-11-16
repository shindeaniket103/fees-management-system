from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from bson.objectid import ObjectId
import random

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["feesdb"]

# Clear old data (optional but recommended for fresh seeding)
db.users.delete_many({})
db.students.delete_many({})
db.fee_structures.delete_many({})
db.payments.delete_many({})
db.receipts.delete_many({})

# --- Create Fee Structures ---
fee_structures = [
    {
        "category": "General",
        "version": 1,
        "components": [
            {"name": "Tuition Fee", "amount": 35000},
            {"name": "Library Fee", "amount": 2000},
            {"name": "Lab Fee", "amount": 3000},
            {"name": "Exam Fee", "amount": 1500},
        ],
    },
    {
        "category": "OBC",
        "version": 1,
        "components": [
            {"name": "Tuition Fee", "amount": 28000},
            {"name": "Library Fee", "amount": 2000},
            {"name": "Lab Fee", "amount": 2500},
            {"name": "Exam Fee", "amount": 1000},
        ],
    },
    {
        "category": "SC",
        "version": 1,
        "components": [
            {"name": "Tuition Fee", "amount": 22000},
            {"name": "Library Fee", "amount": 1500},
            {"name": "Lab Fee", "amount": 2000},
            {"name": "Exam Fee", "amount": 1000},
        ],
    },
]
db.fee_structures.insert_many(fee_structures)
print("✅ Fee structures added.")

# --- Create Admin & Accountant ---
users = [
    {
        "email": "admin@example.com",
        "password": generate_password_hash("admin123"),
        "role": "dept_head",
        "name": "Admin User",
    },
    {
        "email": "accountant@example.com",
        "password": generate_password_hash("acct123"),
        "role": "accountant",
        "name": "Accountant User",
    },
]
db.users.insert_many(users)
print("✅ Admin and accountant users created.")

# --- Generate 30 Students ---
categories = ["General", "OBC", "SC"]
courses = ["B.Tech", "B.Sc", "B.Com"]
years = ["2023", "2024", "2025"]

student_users = []
student_profiles = []

for i in range(1, 31):
    name = f"Student {i}"
    email = f"student{i}@example.com"
    category = random.choice(categories)
    course = random.choice(courses)
    year = random.choice(years)

    user_doc = {
        "email": email,
        "password": generate_password_hash("student123"),
        "role": "student",
        "name": name,
    }
    user_id = db.users.insert_one(user_doc).inserted_id

    student_doc = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "course": course,
        "year": year,
        "category": category,
    }
    db.students.insert_one(student_doc)

print("✅ 30 student users and profiles created.")

# --- Generate Random Payments ---
students = list(db.students.find())
for s in students:
    total_fee_doc = db.fee_structures.find_one({"category": s["category"]})
    total_fee = sum(c["amount"] for c in total_fee_doc["components"])
    paid_amount = random.choice([0, total_fee * 0.25, total_fee * 0.5, total_fee])
    if paid_amount > 0:
        payment = {
            "student_id": s["_id"],
            "amount": paid_amount,
            "method": "MockGateway",
            "status": "success",
        }
        pid = db.payments.insert_one(payment).inserted_id
        db.receipts.insert_one({"payment_id": pid, "receipt_no": f"R-{str(pid)[:8]}"})

print("✅ Random payments and receipts seeded.")
print("🎉 Seeding complete. You can now log in with:")
print("   Admin: admin@example.com / admin123")
print("   Accountant: accountant@example.com / acct123")
print("   Student: student1@example.com / student123 (and up to student30)")
