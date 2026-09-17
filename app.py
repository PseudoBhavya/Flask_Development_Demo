from flask import Flask, render_template_string, request, redirect, url_for, flash
from datetime import date, timedelta

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

# Demo data (resets whenever the server restarts)
books = [
    {"id": 1, "title": "Atomic Habits", "author": "James Clear", "category": "Self-Help", "copies": 4},
    {"id": 2, "title": "The Alchemist", "author": "Paulo Coelho", "category": "Fiction", "copies": 3},
    {"id": 3, "title": "Clean Code", "author": "Robert C. Martin", "category": "Technology", "copies": 2},
    {"id": 4, "title": "Wings of Fire", "author": "A. P. J. Abdul Kalam", "category": "Biography", "copies": 5},
]
members = [
    {"id": 1, "name": "Aarav Sharma", "email": "aarav@example.com"},
    {"id": 2, "name": "Diya Patel", "email": "diya@example.com"},
]
loans = [
    {"id": 1, "book_id": 3, "member_id": 1, "issued": date.today().isoformat(),
     "due": (date.today() + timedelta(days=14)).isoformat(), "returned": False}
]
next_book_id = 5
next_member_id = 3
next_loan_id = 2

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title }} | PageTurn Library</title>
<style>
:root { --navy:#172554; --blue:#3b82f6; --ink:#172033; --muted:#64748b; --bg:#f4f7fb; --line:#e5eaf2; }
* { box-sizing:border-box; margin:0; padding:0; }
body { font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:var(--bg); color:var(--ink); }
header { background:var(--navy); color:white; padding:18px clamp(18px,5vw,72px); display:flex; align-items:center; justify-content:space-between; gap:18px; flex-wrap:wrap; }
.brand { font-size:21px; font-weight:800; letter-spacing:-.4px; }
.brand span { color:#93c5fd; }
nav { display:flex; gap:8px; flex-wrap:wrap; }
nav a { color:#dbeafe; text-decoration:none; padding:10px 13px; border-radius:9px; font-size:14px; font-weight:600; }
nav a:hover, nav a.active { background:#ffffff20; color:white; }
main { max-width:1160px; margin:0 auto; padding:34px 20px 60px; }
.hero { background:linear-gradient(120deg,#1d4ed8,#7c3aed); color:white; border-radius:22px; padding:clamp(28px,5vw,54px); display:flex; justify-content:space-between; align-items:center; gap:24px; flex-wrap:wrap; box-shadow:0 14px 35px #1d4ed81c; }
.hero h1 { font-size:clamp(30px,4vw,44px); letter-spacing:-1.3px; margin:10px 0 12px; }
.hero p { color:#e0e7ff; max-width:570px; line-height:1.7; }
.eyebrow { text-transform:uppercase; font-size:12px; font-weight:800; letter-spacing:1.5px; color:#bfdbfe; }
.hero-icon { font-size:86px; opacity:.95; }
.btn { display:inline-block; border:0; cursor:pointer; text-decoration:none; background:var(--blue); color:white; font-weight:700; padding:11px 16px; border-radius:10px; font-size:14px; }
.btn:hover { filter:brightness(.94); }
.btn.light { background:white; color:#1d4ed8; margin-top:22px; }
.btn.secondary { background:#eaf1ff; color:#1d4ed8; }
.btn.danger { background:#fee2e2; color:#b91c1c; }
.stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:16px; margin:24px 0 34px; }
.stat,.panel,.book-card { background:white; border:1px solid var(--line); border-radius:16px; padding:22px; box-shadow:0 5px 18px #17255408; }
.stat-label { color:var(--muted); font-size:13px; font-weight:600; }
.stat-value { font-size:30px; font-weight:800; margin-top:8px; }
.section-head { display:flex; justify-content:space-between; align-items:center; gap:15px; flex-wrap:wrap; margin:30px 0 17px; }
.section-head h2 { font-size:23px; letter-spacing:-.5px; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:17px; }
.book-card { display:flex; flex-direction:column; gap:12px; }
.book-cover { height:112px; border-radius:12px; background:linear-gradient(135deg,#dbeafe,#ede9fe); display:grid; place-items:center; font-size:42px; }
.book-card h3 { font-size:18px; }
.book-card p { color:var(--muted); font-size:14px; line-height:1.5; }
.tag { display:inline-block; width:max-content; background:#eff6ff; color:#1d4ed8; border-radius:30px; padding:5px 10px; font-size:12px; font-weight:700; }
.panel { margin-top:18px; }
.form-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px; }
label { display:block; color:#475569; font-size:13px; font-weight:700; margin-bottom:7px; }
input,select { width:100%; padding:12px 13px; border:1px solid #d7dfeb; border-radius:10px; font:inherit; background:white; color:var(--ink); }
input:focus,select:focus { outline:2px solid #bfdbfe; border-color:#60a5fa; }
.form-actions { margin-top:16px; }
table { width:100%; border-collapse:collapse; min-width:650px; }
th,td { text-align:left; padding:14px 12px; border-bottom:1px solid var(--line); font-size:14px; }
th { color:#64748b; text-transform:uppercase; letter-spacing:.6px; font-size:11px; }
.table-wrap { overflow-x:auto; }
.status { padding:5px 9px; border-radius:30px; font-size:12px; font-weight:800; background:#dcfce7; color:#166534; }
.status.out { background:#ffedd5; color:#9a3412; }
.flash { padding:13px 16px; background:#dcfce7; color:#166534; border-radius:10px; margin-bottom:18px; font-weight:600; }
.empty { color:var(--muted); padding:25px 0; }
footer { background:#111c3b; color:#cbd5e1; text-align:center; padding:24px; font-size:13px; }
@media(max-width:600px) { header { align-items:flex-start; } nav a { padding:8px; } .hero-icon { display:none; } main { padding-top:22px; } }
</style>
</head>
<body>
<header>
  <div class="brand">📚 PageTurn <span>Library</span></div>
  <nav>
    <a href="{{ url_for('home') }}" class="{{ 'active' if page=='home' else '' }}">Dashboard</a>
    <a href="{{ url_for('books_page') }}" class="{{ 'active' if page=='books' else '' }}">Books</a>
    <a href="{{ url_for('members_page') }}" class="{{ 'active' if page=='members' else '' }}">Members</a>
    <a href="{{ url_for('loans_page') }}" class="{{ 'active' if page=='loans' else '' }}">Issue / Return</a>
  </nav>
</header>
<main>
{% with messages = get_flashed_messages() %}
  {% if messages %}{% for message in messages %}<div class="flash">✓ {{ message }}</div>{% endfor %}{% endif %}
{% endwith %}
{% if page == 'home' %}
<section class="hero">
  <div><div class="eyebrow">Your campus reading space</div><h1>Every great journey<br>starts with a book.</h1>
  <p>Discover your next read, keep track of library books, and manage borrowing from one simple dashboard.</p>
  <a class="btn light" href="{{ url_for('books_page') }}">Browse collection →</a></div>
  <div class="hero-icon">📖</div>
</section>
<section class="stats">
  <div class="stat"><div class="stat-label">Total book titles</div><div class="stat-value">{{ books|length }}</div></div>
  <div class="stat"><div class="stat-label">Registered members</div><div class="stat-value">{{ members|length }}</div></div>
  <div class="stat"><div class="stat-label">Books currently issued</div><div class="stat-value">{{ active_count }}</div></div>
  <div class="stat"><div class="stat-label">Copies available</div><div class="stat-value">{{ available_total }}</div></div>
</section>
<div class="section-head"><h2>Recently added to your shelf</h2><a class="btn secondary" href="{{ url_for('books_page') }}">View all books</a></div>
<div class="grid">
{% for book in books[:3] %}
  <article class="book-card"><div class="book-cover">📘</div><span class="tag">{{ book.category }}</span><h3>{{ book.title }}</h3><p>by {{ book.author }}</p><p>{{ book.copies }} copies available</p></article>
{% endfor %}
</div>
{% elif page == 'books' %}
<div class="section-head"><div><div class="eyebrow" style="color:#3b82f6">Collection</div><h2>Book catalogue</h2></div></div>
<div class="panel">
  <h3 style="margin-bottom:18px">Add a new book</h3>
  <form method="post" action="{{ url_for('add_book') }}">
    <div class="form-grid">
      <div><label for="title">Book title</label><input id="title" name="title" placeholder="e.g. The Pragmatic Programmer" required></div>
      <div><label for="author">Author</label><input id="author" name="author" placeholder="Author name" required></div>
      <div><label for="category">Category</label><input id="category" name="category" placeholder="e.g. Technology" required></div>
      <div><label for="copies">Copies</label><input id="copies" name="copies" type="number" min="1" value="1" required></div>
    </div><div class="form-actions"><button class="btn" type="submit">＋ Add book</button></div>
  </form>
</div>
<div class="grid" style="margin-top:20px">
{% for book in books %}
  <article class="book-card"><div class="book-cover">📚</div><span class="tag">{{ book.category }}</span><h3>{{ book.title }}</h3><p>by {{ book.author }}</p><p><strong>{{ book.copies }}</strong> copies available</p>
  <form method="post" action="{{ url_for('delete_book', book_id=book.id) }}" onsubmit="return confirm('Delete this book?')"><button class="btn danger" type="submit">Remove book</button></form></article>
{% else %}<p class="empty">No books in the catalogue yet.</p>{% endfor %}
</div>
{% elif page == 'members' %}
<div class="section-head"><div><div class="eyebrow" style="color:#3b82f6">Community</div><h2>Library members</h2></div></div>
<div class="panel"><h3 style="margin-bottom:18px">Register a member</h3>
<form method="post" action="{{ url_for('add_member') }}"><div class="form-grid">
<div><label for="name">Full name</label><input id="name" name="name" placeholder="Member name" required></div>
<div><label for="email">Email address</label><input id="email" name="email" type="email" placeholder="name@example.com" required></div>
</div><div class="form-actions"><button class="btn" type="submit">＋ Register member</button></div></form></div>
<div class="panel"><div class="table-wrap"><table><thead><tr><th>Member</th><th>Email</th><th>Books on loan</th></tr></thead><tbody>
{% for member in members %}<tr><td><strong>{{ member.name }}</strong></td><td>{{ member.email }}</td><td>{{ loans|selectattr('member_id','equalto',member.id)|selectattr('returned','equalto',false)|list|length }}</td></tr>
{% else %}<tr><td colspan="3">No members registered.</td></tr>{% endfor %}
</tbody></table></div></div>
{% elif page == 'loans' %}
<div class="section-head"><div><div class="eyebrow" style="color:#3b82f6">Circulation desk</div><h2>Issue & return books</h2></div></div>
<div class="panel"><h3 style="margin-bottom:18px">Issue a book</h3>
<form method="post" action="{{ url_for('issue_book') }}"><div class="form-grid">
<div><label for="book_id">Available book</label><select id="book_id" name="book_id" required><option value="">Choose a book</option>{% for book in books if book.copies > 0 %}<option value="{{ book.id }}">{{ book.title }} ({{ book.copies }} available)</option>{% endfor %}</select></div>
<div><label for="member_id">Member</label><select id="member_id" name="member_id" required><option value="">Choose a member</option>{% for member in members %}<option value="{{ member.id }}">{{ member.name }}</option>{% endfor %}</select></div>
</div><div class="form-actions"><button class="btn" type="submit">Issue for 14 days</button></div></form></div>
<div class="panel"><h3 style="margin-bottom:15px">Loan register</h3><div class="table-wrap"><table><thead><tr><th>Book</th><th>Member</th><th>Issued</th><th>Due date</th><th>Status / action</th></tr></thead><tbody>
{% for loan in loans %}<tr><td><strong>{{ book_name(loan.book_id) }}</strong></td><td>{{ member_name(loan.member_id) }}</td><td>{{ loan.issued }}</td><td>{{ loan.due }}</td><td>{% if loan.returned %}<span class="status">Returned</span>{% else %}<span class="status out">On loan</span> <form style="display:inline" method="post" action="{{ url_for('return_book', loan_id=loan.id) }}"><button class="btn secondary" type="submit">Return</button></form>{% endif %}</td></tr>
{% else %}<tr><td colspan="5">No loans recorded yet.</td></tr>{% endfor %}
</tbody></table></div></div>
{% endif %}
</main>
<footer>© 2026 PageTurn Library · Read more, discover more.</footer>
</body>
</html>
"""

def book_name(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    return book["title"] if book else "Book removed"

def member_name(member_id):
    member = next((m for m in members if m["id"] == member_id), None)
    return member["name"] if member else "Member removed"

@app.route("/")
def home():
    active_count = sum(not loan["returned"] for loan in loans)
    available_total = sum(book["copies"] for book in books)
    return render_template_string(TEMPLATE, title="Dashboard", page="home", books=books,
        members=members, active_count=active_count, available_total=available_total)

@app.route("/books")
def books_page():
    return render_template_string(TEMPLATE, title="Books", page="books", books=books, members=members, loans=loans)

@app.route("/books/add", methods=["POST"])
def add_book():
    global next_book_id
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    category = request.form.get("category", "").strip()
    try:
        copies = int(request.form.get("copies", "1"))
    except ValueError:
        copies = 0
    if not title or not author or not category or copies < 1:
        flash("Please enter valid book details and at least one copy.")
    else:
        books.append({"id": next_book_id, "title": title, "author": author, "category": category, "copies": copies})
        next_book_id += 1
        flash("Book added to the catalogue.")
    return redirect(url_for("books_page"))

@app.route("/books/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if book and any(l["book_id"] == book_id and not l["returned"] for l in loans):
        flash("This book is currently issued and cannot be removed.")
    elif book:
        books.remove(book)
        flash("Book removed.")
    else:
        flash("Book not found.")
    return redirect(url_for("books_page"))

@app.route("/members")
def members_page():
    return render_template_string(TEMPLATE, title="Members", page="members", books=books, members=members, loans=loans)

@app.route("/members/add", methods=["POST"])
def add_member():
    global next_member_id
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    if not name or not email:
        flash("Please enter both a name and email.")
    elif any(m["email"].lower() == email.lower() for m in members):
        flash("A member with this email is already registered.")
    else:
        members.append({"id": next_member_id, "name": name, "email": email})
        next_member_id += 1
        flash("Member registered successfully.")
    return redirect(url_for("members_page"))

@app.route("/loans")
def loans_page():
    return render_template_string(TEMPLATE, title="Issue / Return", page="loans", books=books, members=members,
        loans=loans, book_name=book_name, member_name=member_name)

@app.route("/loans/issue", methods=["POST"])
def issue_book():
    global next_loan_id
    try:
        book_id = int(request.form.get("book_id", ""))
        member_id = int(request.form.get("member_id", ""))
    except ValueError:
        flash("Choose a valid book and member.")
        return redirect(url_for("loans_page"))
    book = next((b for b in books if b["id"] == book_id), None)
    member = next((m for m in members if m["id"] == member_id), None)
    if not book or not member:
        flash("The selected book or member was not found.")
    elif book["copies"] < 1:
        flash("No copies of this book are currently available.")
    else:
        book["copies"] -= 1
        loans.append({"id": next_loan_id, "book_id": book_id, "member_id": member_id,
            "issued": date.today().isoformat(), "due": (date.today() + timedelta(days=14)).isoformat(),
            "returned": False})
        next_loan_id += 1
        flash("Book issued successfully. Due in 14 days.")
    return redirect(url_for("loans_page"))

@app.route("/loans/return/<int:loan_id>", methods=["POST"])
def return_book(loan_id):
    loan = next((l for l in loans if l["id"] == loan_id), None)
    if not loan or loan["returned"]:
        flash("This loan is already returned or does not exist.")
    else:
        loan["returned"] = True
        book = next((b for b in books if b["id"] == loan["book_id"]), None)
        if book:
            book["copies"] += 1
        flash("Book returned successfully.")
    return redirect(url_for("loans_page"))

if __name__ == "__main__":
    app.run(debug=True, port=5001, use_reloader=False)
