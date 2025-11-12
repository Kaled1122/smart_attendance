import os
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from datetime import datetime
from utils.notifier import send_message
from utils.scheduler import schedule_tasks

# -------------------------------------------------
# APP CONFIG
# -------------------------------------------------
app = Flask(__name__)

# --- SECRET & JWT CONFIG ---
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key")
jwt = JWTManager(app)

# --- DATABASE CONFIG ---
db_url = os.getenv("DATABASE_URL")

# 🧠 Railway fix (replace old format postgres:// with postgresql://)
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///data/attendance.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

db = SQLAlchemy(app)

# -------------------------------------------------
# DATABASE MODEL
# -------------------------------------------------
class Staff(db.Model):
    __tablename__ = "staff"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default="staff")  # staff / senior / contingency
    status = db.Column(db.String(20), default="unconfirmed")
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Staff {self.name} - {self.status}>"

# -------------------------------------------------
# INITIALIZATION
# -------------------------------------------------
with app.app_context():
    db.create_all()
    if not Staff.query.first():
        db.session.add_all([
            Staff(name="Ahmed", phone="0501234567", role="staff"),
            Staff(name="Fahad", phone="0509876543", role="senior"),
            Staff(name="Contingency 1", phone="0505555555", role="contingency")
        ])
        db.session.commit()
        print("✅ Staff table created and sample data added.")

# -------------------------------------------------
# ROUTES
# -------------------------------------------------
@app.route("/")
def index():
    """Main staff page."""
    staff = Staff.query.all()
    return render_template("index.html", staff=staff)

@app.route("/sign_in", methods=["POST"])
def sign_in():
    """Mark staff as present."""
    staff_id = request.form.get("id")
    s = Staff.query.get(staff_id)
    if not s:
        return jsonify({"error": "Staff not found"}), 404
    s.status = "present"
    s.timestamp = datetime.now()
    db.session.commit()
    return redirect("/")

@app.route("/update_status", methods=["POST"])
@jwt_required(optional=True)
def update_status():
    """Update a staff member’s status (used by senior staff)."""
    s = Staff.query.get(request.form.get("id"))
    if not s:
        return jsonify({"error": "Staff not found"}), 404
    s.status = request.form.get("status", "unconfirmed")
    db.session.commit()
    return jsonify({"success": True})

@app.route("/dashboard")
def dashboard():
    """Dashboard for senior staff to view all statuses."""
    staff = Staff.query.order_by(Staff.role).all()
    return render_template("dashboard.html", staff=staff)

@app.route("/login", methods=["POST"])
def login():
    """Simple login route returning a JWT for senior staff."""
    name = request.form.get("name")
    role = request.form.get("role")
    staff = Staff.query.filter_by(name=name, role=role).first()
    if not staff:
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_access_token(identity=staff.name)
    return jsonify(access_token=token)
    
@app.route("/run_schedule")
def run_schedule():
    schedule_tasks(app, db, Staff)
    return "Scheduler triggered", 200

# -------------------------------------------------
# MAIN ENTRY
# -------------------------------------------------
if __name__ == "__main__":
    print("🚀 Starting Attendance App...")
    schedule_tasks(app, db, Staff)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
