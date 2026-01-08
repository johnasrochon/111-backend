from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DB_NAME = "budget.manage.db"

ALLOWED_CATEGORIES = ["Food", "Education", "Entertainment"]

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

    # Seed expenses
    expenses = [
        ("2025-01-05", "Groceries", "Weekly grocery shopping", 85.40, "Jan 5, 2025", "Food", 1),
        ("2025-01-07", "Books", "College textbooks", 120.00, "Jan 7, 2025", "Education", 2),
        ("2025-01-10", "Movie Night", "Cinema tickets", 30.00, "Jan 10, 2025", "Entertainment", 3),
        ("2025-01-12", "Lunch", "Cafe lunch", 12.50, "Jan 12, 2025", "Food", 1),
        ("2025-01-15", "Online Course", "Python course", 55.00, "Jan 15, 2025", "Education", 4),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO expenses
        (date, title, description, amount, date_str, category, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, expenses)

    conn.commit()
    conn.close()

init_db()

def row_to_dict(row):
    return {
        "id": row[0],
        "date": row[1],
        "title": row[2],
        "description": row[3],
        "amount": row[4],
        "date_str": row[5],
        "category": row[6],
        "user_id": row[7]
    }

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

# 1. GET all expenses
@app.get("/api/expenses")
def get_expenses():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    conn.close()

    return jsonify([row_to_dict(row) for row in rows]), 200

# 2. GET single expense
@app.get("/api/expenses/<int:expense_id>")
def get_expense(expense_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Expense not found"}), 404

    return jsonify(row_to_dict(row)), 200

# 3. UPDATE expense
@app.put("/api/expenses/<int:expense_id>")
def update_expense(expense_id):
    data = request.get_json()

    if "category" in data and data["category"] not in ALLOWED_CATEGORIES:
        return jsonify({
            "error": "Invalid category. Allowed values: Food, Education, Entertainment"
        }), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Expense not found"}), 404

    fields = []
    values = []

    for field in ["title", "description", "amount", "category", "user_id"]:
        if field in data:
            fields.append(f"{field} = ?")
            values.append(data[field])

    if fields:
        values.append(expense_id)
        cursor.execute(
            f"UPDATE expenses SET {', '.join(fields)} WHERE id = ?",
            values
        )
        conn.commit()

    conn.close()
    return jsonify({"message": "Expense updated successfully"}), 200

# 4. DELETE expense
@app.delete("/api/expenses/<int:expense_id>")
def delete_expense(expense_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Expense not found"}), 404

    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Expense deleted successfully"}), 200



# Frontend
@app.get("/")
def home ():
    return render_template("home.html")

