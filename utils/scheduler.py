from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from utils.notifier import send_message

def schedule_tasks(app, db, Staff):
    scheduler = BackgroundScheduler(timezone="Asia/Riyadh")

    # 6:00 AM → Reset all statuses
    @scheduler.scheduled_job('cron', hour=6, minute=0)
    def reset_attendance():
        with app.app_context():
            print("🔄 [6:00 AM] Resetting all staff statuses...")
            for s in Staff.query.all():
                s.status = "unconfirmed"
            db.session.commit()
            print("✅ All statuses set to unconfirmed.")

    # 6:15 AM → Notify unconfirmed staff
    @scheduler.scheduled_job('cron', hour=6, minute=15)
    def remind_unconfirmed():
        with app.app_context():
            print("📱 [6:15 AM] Reminding unconfirmed staff...")
            for s in Staff.query.filter_by(status="unconfirmed").all():
                if s.phone:
                    send_message(
                        s.phone,
                        f"Hi {s.name}, you haven’t signed in yet. Reply: [On way] [Sick] [Absent]"
                    )
            print("✅ Reminder sent to all unconfirmed staff.")

    # 6:25 AM → Notify contingency staff if any absences expected
    @scheduler.scheduled_job('cron', hour=6, minute=25)
    def activate_contingency():
        with app.app_context():
            print("⚠️ [6:25 AM] Checking for absences...")
            unconfirmed = Staff.query.filter_by(status="unconfirmed").count()
            if unconfirmed > 0:
                contingency_staff = Staff.query.filter_by(role="contingency").all()
                for c in contingency_staff:
