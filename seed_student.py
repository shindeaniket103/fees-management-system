from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client["feesdb"]

user = db.users.find_one({"email": "student@example.com"})
if user:
    if not db.students.find_one({"user_id": user["_id"]}):
        db.students.insert_one({
            "name": "Demo Student",
            "email": user["email"],
            "user_id": user["_id"],
            "course": "B.Tech",
            "year": "2025",
            "category": "General"
        })
        print("✅ Student document created.")
    else:
        print("ℹ️ Student document already exists.")
else:
    print("❌ User not found.")
