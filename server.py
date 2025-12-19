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

    # Seed users (only if they don't already exist)
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

    conn.commit()
    conn.close()

# Call this once when the app starts
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
