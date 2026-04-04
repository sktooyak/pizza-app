# Backend server for Pizzeria app
# Handles database connection and API routes for menu and orders

from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)


# -------------------------
# Database Setup
# -------------------------
# Create required tables if they do not already exist
def init_db():
    conn = sqlite3.connect("pizzeria.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        price REAL NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# -------------------------
# Seed Sample Data
# -------------------------
# Seed initial menu data if the table is empty
def seed_data():
    conn = sqlite3.connect("pizzeria.db")
    cursor = conn.cursor()

    # Check if menu_items table is empty before inserting sample data
    cursor.execute("SELECT COUNT(*) FROM menu_items")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute("""
        INSERT INTO menu_items (name, description, category, price)
        VALUES (?, ?, ?, ?)
        """, ("Pepperoni Pizza", "Classic pizza", "Pizza", 14.99))

        cursor.execute("""
        INSERT INTO menu_items (name, description, category, price)
        VALUES (?, ?, ?, ?)
        """, ("Cheese Pizza", "Cheesy goodness", "Pizza", 12.99))

    conn.commit()
    conn.close()


# -------------------------
# Database Connection
# -------------------------
# Create and return a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect("pizzeria.db")
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------
# Routes
# -------------------------
# Home route to confirm server is running
@app.route("/")
def home():
    return "Pizzeria Backend Running!"


# API endpoint to get all menu items
@app.route("/menu")
def get_menu():
    conn = get_db_connection()

    # Fetch all menu items from the database
    items = conn.execute("SELECT * FROM menu_items").fetchall()
    conn.close()

    return jsonify([dict(item) for item in items])


# -------------------------
# Run Application
# -------------------------
if __name__ == "__main__":
    init_db()
    seed_data()
    app.run(debug=True)