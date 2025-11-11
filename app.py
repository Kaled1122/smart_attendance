import os
import uuid
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# -------------------------------------------------
# APP CONFIG
# -------------------------------------------------
app = Flask(__name__)

db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///data/attendance.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# -------------------------------------------------
# DATABASE MODELS
# -------------------------------------------------
class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default="staff")  # staff / senior / contingency
    department = db.Column(db.String(80))
    status = db.Column(db.String(20), default="unconfirmed")
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Staff {self.name} ({self.role}) - {self.status}>"

# -------------------------------------------------
# INITIALIZE DATABASE
# -------------------------------------------------
with app.app_context():
    db.create_all()

# -------------------------------------------------
# ROUTES
# -------------------------------------------------
@app.route("/")
def home():
    return render_template("admin.html", staff=Staff.query.all())

@app.route("/login/<uuid_code>")
def login(uuid_code):
    """Personalized login page per staff UUID"""
    staff = Staff.query.filter_by(uuid=uuid_code).first()
    if not staff:
        return "Invalid or expired link", 404
    return render_template("index.html", staff=staff)

@app.route("/sign_in/<uuid_code>", methods=["POST"])
def sign_in(uuid_code):
    staff = Staff.query.filter_by(uuid=uuid_code).first()
    if not staff:
        return jsonify({"error": "Invalid ID"}), 404
    staff.status = "present"
    staff.timestamp = datetime.now()
    db.session.commit()
    return render_template("index.html", staff=staff, message="✅ You are signed in successfully!")

@app.route("/dashboard")
def dashboard():
    staff = Staff.query.order_by(Staff.role, Staff.name).all()
    return render_template("dashboard.html", staff=staff)

@app.route("/generate_links")
def generate_links():
    """Generate personal sign-in links for all staff"""
    base_url = request.host_url.rstrip("/")
    links = []
    for s in Staff.query.all():
        links.append({
            "name": s.name,
            "role": s.role,
            "url": f"{base_url}/login/{s.uuid}"
        })
    return render_template("admin.html", staff=Staff.query.all(), links=links)

# -------------------------------------------------
# RUN APP
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
