from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='staff')  # staff, senior, contingency
    status = db.Column(db.String(20), default='unconfirmed')  # present, late, sick, absent, on_way, unconfirmed
    timestamp = db.Column(db.DateTime, default=None)

    def __repr__(self):
        return f"<Staff {self.name} - {self.status}>"

class AttendanceLog(db.Model):
    __tablename__ = 'attendance_log'
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    action = db.Column(db.String(50))  # sign_in, auto_message, reminder_sent, contingency_alert
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    staff = db.relationship('Staff', backref=db.backref('logs', lazy=True))

    def __repr__(self):
        return f"<Log {self.staff.name} - {self.action}>"