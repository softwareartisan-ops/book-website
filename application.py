import os

from flask import Flask, session, render_template, redirect, request, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if session.get("username"):
        return render_template("search.html", username=session["username"])
    else:
        return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    """User Login process"""
    # Get form information.
    username = request.form.get("username")
    password = request.form.get("password")

    user = db.execute("SELECT * FROM users WHERE (username = '" + username + "') AND (password = '" + password + "')").first()

    if user:
        session["username"] = user.username
        return redirect(url_for("index"))

    return render_template("login.html", invalid=True)


@app.route("/sign_up")
def sign_up():
    """Register form a new user account"""
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    """User registration process"""
    # Get form information.
    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")


    # Check if user email  exists.
    if db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).rowcount == 0:

        db.execute("INSERT INTO users (name, username, password, email) VALUES (:name, :username, :password, :email )",
            {"name": name, "username": username, "password" : password, "email" : email})
        db.commit()
        return redirect(url_for("index"))

    else:
        return render_template("error.html", message="Existing email address. Please insert another email address")


@app.route("/logout")
def logout():
    """User logout process"""
    session.clear()
    return redirect(url_for("index"))


@app.route("/search", methods=["POST"])
def search():
    """Search a book."""
    username = request.form.get("username")
    return render_template("search.html", name=username)


@app.route("/books", methods=["POST"])
def books():
    """List  books result."""
    # Get form information.
    try:
        isbn = request.form.get("isbn")
        title =  request.form.get("title")
        author = request.form.get("author")
        year = request.form.get("year")
    except ValueError:
        return render_template("error.html", message="Error.")

    books = None
    if isbn:
        books = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    if title:
        books = db.execute("SELECT * FROM books WHERE  title = :title", {"title": title}).fetchall()
    if author:
        books = db.execute("SELECT * FROM books WHERE author = :author", {"author": author}).fetchall()
    if year:
        books = db.execute("SELECT * FROM books WHERE year = :year", {"year": year}).fetchall()

    #Search with any criteria returns maximun 20 results in order to not affect performance
    if books is None:
        books = db.execute("SELECT * FROM books LIMIT 20").fetchall()

    count = len(books)
    if count == 0:
        return render_template("error.html", message="No such book")


    return render_template("books.html" , books=books, count=count)




@app.route("/books/<int:book_id>")
def book(book_id):
    """List details about a single book"""

    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="No such book.")
    else:
        return render_template("book.html", book=book)
