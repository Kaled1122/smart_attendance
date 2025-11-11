from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token
from datetime import datetime
from utils.scheduler import schedule_tasks

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")
db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    role = db.Column(db.String(20))
    department = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(120))
    uuid = db.Column(db.String(36), unique=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    date = db.Column(db.Date)
    status = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime)

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(phone=data["phone"]).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "role": user.role})

@app.route("/api/mark", methods=["POST"])
@jwt_required()
def mark_attendance():
    user_id = get_jwt_identity()
    att = Attendance(user_id=user_id, date=datetime.now().date(),
                     status="present", timestamp=datetime.now())
    db.session.add(att)
    db.session.commit()
    return jsonify({"message": "Marked present"})

from utils.scheduler import schedule_tasks

if __name__ == "__main__":
    schedule_tasks(app, db, Staff)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
