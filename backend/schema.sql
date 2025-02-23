-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('student', 'admin', 'department')) NOT NULL
);

-- Departments Table (To manage departments separately)
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- Tickets Table
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    service TEXT NOT NULL,
    priority TEXT CHECK(priority IN ('Low', 'Medium', 'High')) NOT NULL,
    assigned_department_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('Pending', 'In Progress', 'Completed')) NOT NULL,
    image_path TEXT,  -- Store image file path instead of BLOB
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (assigned_department_id) REFERENCES departments(id)
);

-- Ticket Updates Table (To track changes in ticket status)
CREATE TABLE IF NOT EXISTS ticket_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    updated_status TEXT CHECK(updated_status IN ('Pending', 'In Progress', 'Completed')) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id)
);
