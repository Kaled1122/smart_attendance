import os
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from utils.notifier import send_message
from utils.scheduler import schedule_tasks

# -------------------------------------------------
# APP CONFIG
# -------------------------------------------------
app = Flask(__name__)

# Database connection (use Railway env variable)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}

db = SQLAlchemy(app)

# -------------------------------------------------
# DATABASE MODEL
# -------------------------------------------------
class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default="staff")  # staff / senior / contingency
    status = db.Column(db.String(20), default="unconfirmed")
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Staff {self.name} - {self.status}>"

# -------------------------------------------------
# ROUTES
# -------------------------------------------------
@app.route('/')
def index():
    """Staff sign-in page."""
    return render_template('index.html', staff=Staff.query.all())

@app.route('/sign_in', methods=['POST'])
def sign_in():
    """Mark staff as present when they sign in."""
    staff_id = request.form['id']
    s = Staff.query.get(staff_id)
    if not s:
        return jsonify({'error': 'Staff not found'}), 404
    s.status = "present"
    s.timestamp = datetime.now()
    db.session.commit()
    return redirect('/')

@app.route('/update_status', methods=['POST'])
def update_status():
    """Manually update a staff member’s status."""
    s = Staff.query.get(request.form['id'])
    if not s:
        return jsonify({'error': 'Staff not found'}), 404
    s.status = request.form['status']
    db.session.commit()
    return jsonify({'success': True})

@app.route('/dashboard')
def dashboard():
    """Dashboard for senior staff to view live attendance."""
    staff = Staff.query.order_by(Staff.role).all()
    return render_template('dashboard.html', staff=staff)

# -------------------------------------------------
# MAIN ENTRY
# -------------------------------------------------
if __name__ == "__main__":
    # Schedule daily attendance automation (6:00–6:30 AM)
    schedule_tasks(app, db, Staff)
    # Start Flask app
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
