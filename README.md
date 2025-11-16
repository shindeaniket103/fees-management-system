# Fees Management (Demo)

This is a compact demo of the Fees Management System (Flask + MongoDB).

## Quick start
1. Copy `.env.example` to `.env` and edit if needed.
2. Ensure local MongoDB is running and accessible (`mongodb://localhost:27017/feesdb`).
3. Create and activate a virtualenv and install:
   ```
   pip install -r requirements.txt
   python run.py
   ```
4. Open `http://127.0.0.1:5000/login` and use demo credentials:
   - student@example.com / student123
   - accountant@example.com / acct123
   - admin@example.com / admin123

## Notes
- Payments are mock (no real gateway).
- Receipts are simple DB records; HTML view available in student dashboard flow.
