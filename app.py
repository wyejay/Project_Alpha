from flask import Flask, request, redirect, render_template_string, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Use Render Postgres if available, else SQLite locally
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///local.db")
if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres://"):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["SQLALCHEMY_DATABASE_URI"].replace("postgres://", "postgresql://")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ----------------- MODELS -----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

# ----------------- ROUTES -----------------
@app.route("/")
def index():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        return render_template_string("""
            <h1>Welcome, {{ user.username }}!</h1>
            <a href="{{ url_for('logout') }}">Logout</a>
        """, user=user)
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        if User.query.filter_by(username=username).first():
            return "Username already exists!"
        db.session.add(User(username=username, password=password))
        db.session.commit()
        return redirect(url_for("login"))
    return render_template_string("""
        <h2>Signup</h2>
        <form method="post">
            <input name="username" placeholder="Username"><br>
            <input type="password" name="password" placeholder="Password"><br>
            <button type="submit">Signup</button>
        </form>
        <a href="{{ url_for('login') }}">Login</a>
    """)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect(url_for("index"))
        return "Invalid credentials!"
    return render_template_string("""
        <h2>Login</h2>
        <form method="post">
            <input name="username" placeholder="Username"><br>
            <input type="password" name="password" placeholder="Password"><br>
            <button type="submit">Login</button>
        </form>
        <a href="{{ url_for('signup') }}">Signup</a>
    """)

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

# ----------------- RUN -----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
