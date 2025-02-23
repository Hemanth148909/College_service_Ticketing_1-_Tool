import sqlite3
from flask import Flask, request, jsonify, redirect, url_for
import bcrypt
from flask_cors import CORS
from utils.db_config import get_db_connection

app = Flask(__name__)
CORS(app)  # Allow frontend requests

# -------------------------------
# 🚀 User Routes
# -------------------------------

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the College Service Support API!"}), 200
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not all([username, email, password, role]):
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 🔹 Check if email or username already exists
        existing_user = cursor.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if existing_user:
            return jsonify({"error": "Email already registered"}), 409
        
        existing_username = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if existing_username:
            return jsonify({"error": "Username already taken"}), 409
        
        # 🔹 Check if there is already an admin user
        if role == "admin":
            admin_count = cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'").fetchone()[0]
            if admin_count >= 1:
                return jsonify({"error": "An admin already exists. Only one admin is allowed."}), 409

        # 🔹 Hash password and insert user
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                       (username, email, hashed_password, role))
        conn.commit()  # Commit changes
        return jsonify({"message": "Registration successful"}), 201

    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()  # Always close the connection

# 🔹 User Login
@app.route('/user/login', methods=['POST'])
def login_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[3]):  # user[3] is password column
        return jsonify({"message": "Login successful", "role": user[4]}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# -------------------------------
# 🎫 Ticket Routes
# -------------------------------

# 🔹 Create a Ticket
@app.route('/ticket/create', methods=['POST'])
def create_ticket():
    data = request.json
    student_id = data.get('student_id')
    service = data.get('service')
    priority = data.get('priority')
    assigned_department = data.get('assigned_department')
    status = "Pending"
    
    if not all([student_id, service, priority, assigned_department]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tickets (student_id, service, priority, assigned_department, status) VALUES (?, ?, ?, ?, ?)",
                   (student_id, service, priority, assigned_department, status))
    conn.commit()
    conn.close()

    return jsonify({"message": "Ticket created successfully"}), 201

# 🔹 Get All Tickets
@app.route('/ticket/all', methods=['GET'])
def get_all_tickets():
    conn = get_db_connection()
    cursor = conn.cursor()
    tickets = cursor.execute("SELECT * FROM tickets").fetchall()
    conn.close()
    return jsonify([dict(ticket) for ticket in tickets]), 200

# 🔹 Update Ticket Status
@app.route('/ticket/status/<int:ticket_id>', methods=['PUT'])
def update_ticket_status(ticket_id):
    data = request.json
    new_status = data.get('status')
    
    if new_status not in ["Pending", "In Progress", "Completed"]:
        return jsonify({"error": "Invalid status"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tickets SET status = ? WHERE id = ?", (new_status, ticket_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Ticket status updated"}), 200

# -------------------------------
# 🎯 Run the Flask App
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
