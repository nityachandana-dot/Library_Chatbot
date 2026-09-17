import sqlite3

# Connect to database
conn = sqlite3.connect("library.db")
cur = conn.cursor()

# --- Create tables ---
cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll TEXT UNIQUE,
    name TEXT,
    department TEXT,
    year TEXT,
    email TEXT,
    password TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    subject TEXT,
    available TEXT,
    location TEXT,
    quantity INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    book_id INTEGER,
    action TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(book_id) REFERENCES books(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule TEXT
)
""")

# --- Insert sample students ---
students = [
    ("24E51A6693", "Nitya", "CSM", "2nd Year", "24E51A6693@hitam.org", "pass123"),
    ("24E51A6682", "Sathwika", "CSM", "2nd Year", "24E51A6682@hitam.org", "pass123"),
    ("24E51A66B8", "Vyshnavi", "CSM", "2nd Year", "24E51A66B8@hitam.org", "pass123"),
    ("24E51A6688", "Niveditha", "CSM", "2nd Year", "24E51A6688@hitam.org", "pass123"),
    ("24E51A6676", "Joshitha", "CSM", "2nd Year", "24E51A6676@hitam.org", "pass123"),
]
cur.executemany(
    "INSERT OR IGNORE INTO students (roll, name, department, year, email, password) VALUES (?, ?, ?, ?, ?, ?)",
    students
)

# --- Insert sample books ---
books = [
    ("Python Programming", "Guido van Rossum", "CS", "Yes", "Shelf A", 5),
    ("Operating Systems", "Silberschatz", "CS", "Yes", "Shelf B", 3),
    ("Database Systems", "Elmasri", "CS", "Yes", "Shelf C", 4),
    ("Computer Networks", "Tanenbaum", "CS", "Yes", "Shelf D", 2),
    ("Engineering Chemistry", "Dr. Sharma", "Chemistry", "Yes", "Shelf E", 6)
]
cur.executemany(
    "INSERT OR IGNORE INTO books (title, author, subject, available, location, quantity) VALUES (?, ?, ?, ?, ?, ?)",
    books
)

# --- Insert library rules ---
rules = [
    ("Return books within 14 days."),
    ("Maintain silence in the library."),
    ("Handle books with care.")
]
cur.executemany("INSERT OR IGNORE INTO rules (rule) VALUES (?)", [(r,) for r in rules])

# Commit and close
conn.commit()
conn.close()

print("✅ Database setup complete with sample students, books, and rules.")
