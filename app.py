from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "library_secret"

# --- Database connection ---
def get_db():
    conn = sqlite3.connect("library.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- Role selection page ---
@app.route("/")
def index():
    return render_template("role.html")

# --- Student login ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        roll = request.form["roll_number"]
        password = request.form["password"]
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM students WHERE roll=? AND password=?", (roll, password))
        student = cur.fetchone()
        conn.close()
        if student:
            session["student_id"] = student["id"]
            session["student_name"] = student["name"]
            flash("Login successful!", "success")
            return redirect(url_for("chat"))
        else:
            flash("Invalid credentials", "error")
    return render_template("student_login.html")

# --- Student chatbot ---
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "student_id" not in session:
        return redirect(url_for("login"))

    response = ""
    if request.method == "POST":
        user_input = request.form["user_input"].strip().lower()
        conn = get_db()
        cur = conn.cursor()

        # --- Borrow/Return/Clear commands ---
        if user_input == "__borrow__":
            session["mode"] = "borrow"
            response = "Which book would you like to borrow? Please enter the title or author."
        elif user_input == "__return__":
            session["mode"] = "return"
            response = "Which book would you like to return? Please enter the title or author."
        elif user_input == "__clear__":
            session.pop("mode", None)
            session.pop("last_book_id", None)
            response = "Chat cleared. You can start a new search."
        else:
            # --- Search for book ---
            cur.execute("SELECT * FROM books WHERE LOWER(title) LIKE ? OR LOWER(author) LIKE ?",
                        (f"%{user_input}%", f"%{user_input}%"))
            book = cur.fetchone()

            if book:
                session["last_book_id"] = book["id"]

                # --- Borrow mode ---
                if session.get("mode") == "borrow":
                    if book["quantity"] > 0:
                        cur.execute("UPDATE books SET quantity=quantity-1 WHERE id=?", (book["id"],))
                        cur.execute("INSERT INTO transactions (student_id, book_id, action) VALUES (?, ?, ?)",
                                    (session["student_id"], book["id"], "Borrow"))
                        conn.commit()
                        response = f"You borrowed {book['title']} successfully."
                    else:
                        response = f"Sorry, {book['title']} is not available right now."
                    session.pop("mode", None)

                # --- Return mode ---
                elif session.get("mode") == "return":
                    cur.execute("UPDATE books SET quantity=quantity+1 WHERE id=?", (book["id"],))
                    cur.execute("INSERT INTO transactions (student_id, book_id, action) VALUES (?, ?, ?)",
                                (session["student_id"], book["id"], "Return"))
                    conn.commit()
                    response = f"You returned {book['title']} successfully."
                    session.pop("mode", None)

                # --- Normal search ---
                else:
                    response = f"Book found: {book['title']} by {book['author']} (Available: {book['quantity']})"
            else:
                response = "Sorry, I couldn't find that book."

        conn.close()

    return render_template("index.html", response=response)

# --- Student history ---
@app.route("/history")
def history():
    if "student_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT b.title, t.action, t.timestamp
                   FROM transactions t
                   JOIN books b ON t.book_id = b.id
                   WHERE t.student_id=? ORDER BY t.timestamp DESC""",
                (session["student_id"],))
    records = cur.fetchall()
    conn.close()
    return render_template("student_history.html", history=records)

# --- Admin login ---
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "admin":
            session["admin"] = True
            flash("Admin login successful!", "success")
            return redirect(url_for("admin_panel"))
        else:
            flash("Invalid admin credentials", "error")
    return render_template("admin_login.html")

# --- Admin panel ---
@app.route("/admin_panel")
def admin_panel():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM books")
    books = cur.fetchall()

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    cur.execute("SELECT * FROM rules")
    rules = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM books")
    total_books = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM books WHERE available='Yes'")
    available_books = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM books WHERE available='No'")
    not_available_books = cur.fetchone()[0]

    cur.execute("SELECT subject, COUNT(*) FROM books GROUP BY subject")
    subject_counts = dict(cur.fetchall())

    conn.close()
    return render_template("admin.html",
                           books=books,
                           students=students,
                           rules=rules,
                           total_books=total_books,
                           available_books=available_books,
                           not_available_books=not_available_books,
                           subject_counts=subject_counts)

# --- Add Book ---
@app.route("/add_book", methods=["POST"])
def add_book():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    title = request.form["title"]
    author = request.form["author"]
    available = request.form["available"]
    location = request.form["location"]
    subject = request.form["subject"]
    quantity = request.form["quantity"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO books (title, author, subject, available, location, quantity) VALUES (?, ?, ?, ?, ?, ?)",
                (title, author, subject, available, location, quantity))
    conn.commit()
    conn.close()

    flash(f"Book '{title}' added successfully!", "success")
    return redirect(url_for("admin_panel"))

# --- Edit Book ---
@app.route("/edit/<int:book_id>")
def edit_book(book_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books WHERE id=?", (book_id,))
    book = cur.fetchone()
    conn.close()
    return render_template("edit.html", book=book)

@app.route("/update_book/<int:book_id>", methods=["POST"])
def update_book(book_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    title = request.form["title"]
    author = request.form["author"]
    available = request.form["available"]
    location = request.form["location"]
    subject = request.form["subject"]
    quantity = request.form["quantity"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""UPDATE books SET title=?, author=?, available=?, location=?, subject=?, quantity=? WHERE id=?""",
                (title, author, available, location, subject, quantity, book_id))
    conn.commit()
    conn.close()

    flash(f"Book '{title}' updated successfully!", "success")
    return redirect(url_for("admin_panel"))

# --- Remove Copies ---
@app.route("/remove_copies/<int:book_id>", methods=["POST"])
def remove_copies(book_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    copies = int(request.form["copies"])
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT quantity FROM books WHERE id=?", (book_id,))
    current_quantity = cur.fetchone()["quantity"]

    if copies <= current_quantity:
        cur.execute("UPDATE books SET quantity=quantity-? WHERE id=?", (copies, book_id))
        conn.commit()
        flash(f"Removed {copies} copies successfully!", "success")
    else:
        flash("Cannot remove more copies than available.", "error")

    conn.close()
    return redirect(url_for("admin_panel"))

# --- Delete Book ---
@app.route("/delete_book/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()

    flash("Book deleted successfully!", "success")
    return redirect(url_for("admin_panel"))

# --- Admin history ---
@app.route("/admin/history")
def admin_history():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT s.name AS student_name, s.roll, b.title, t.action, t.timestamp
                   FROM transactions t
                   JOIN students s ON t.student_id = s.id
                   JOIN books b ON t.book_id = b.id
                   ORDER BY t.timestamp DESC""")
    records = cur.fetchall()
    conn.close()
    return render_template("admin_history.html", history=records)

# --- Logout ---
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("index"))

# --- Run the app ---
if __name__ == "__main__":
    app.run(debug=True)
