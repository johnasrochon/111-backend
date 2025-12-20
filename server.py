from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DB_NAME = "budget.manage.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # Expenses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        amount REAL NOT NULL,
        date_str TEXT NOT NULL,
        category TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # Seed users
    users = [
        ("alice", "password123"),
        ("bob", "bobpass"),
        ("charlie", "charliepass"),
        ("diana", "dianapass")
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO users (username, password)
        VALUES (?, ?)
    """, users)

    # Seed expenses (only once)
    expenses = [
        ("2025-01-05", "Groceries", "Weekly grocery shopping", 85.40, "Jan 5, 2025", "Food", 1),
        ("2025-01-07", "Gas", "Car fuel", 42.00, "Jan 7, 2025", "Transportation", 2),
        ("2025-01-10", "Internet Bill", "Monthly internet payment", 65.99, "Jan 10, 2025", "Utilities", 1),
        ("2025-01-12", "Coffee", "Morning coffee", 4.75, "Jan 12, 2025", "Food", 3),
        ("2025-01-15", "Gym Membership", "Monthly gym fee", 30.00, "Jan 15, 2025", "Health", 4),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO expenses
        (date, title, description, amount, date_str, category, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, expenses)

    conn.commit()
    conn.close()

# Initialize DB on app start
init_db()

@app.get("/api/health")
def health_check():
    return jsonify({"status": "OK"}), 200

@app.post("/api/register")
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "user registered successfully"}), 201
