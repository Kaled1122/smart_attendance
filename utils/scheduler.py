from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from utils.notifier import send_message

def schedule_tasks(app, db, Staff):
    scheduler = BackgroundScheduler()

    # 6:00 — Reset all statuses
    @scheduler.scheduled_job('cron', hour=6, minute=0)
    def reset_attendance():
        with app.app_context():
            for s in Staff.query.all():
                s.status = "unconfirmed"
            db.session.commit()

    # 6:15 — Notify unconfirmed staff
    @scheduler.scheduled_job('cron', hour=6, minute=15)
    def remind_unconfirmed():
        with app.app_context():
            for s in Staff.query.filter_by(status="unconfirmed").all():
                send_message(s.phone, "You haven’t signed in. Reply: [On way] [Sick] [Absent]")

    # 6:25 — Notify contingency staff
    @scheduler.scheduled_job('cron', hour=6, minute=25)
    def activate_contingency():
        with app.app_context():
            missing = Staff.query.filter_by(status="unconfirmed").all()
            if missing:
                contingency = Staff.query.filter_by(role="contingency").all()
                for c in contingency:
                    send_message(c.phone, f"Prepare to cover for: {', '.join([m.name for m in missing])}")

    # 6:30 — Lock attendance
    @scheduler.scheduled_job('cron', hour=6, minute=30)
    def lock_attendance():
        with app.app_context():
            for s in Staff.query.filter_by(status="unconfirmed").all():
                s.status = "absent"
            db.session.commit()

    scheduler.start()