import uvicorn, os
import datetime
from fastapi import FastAPI, HTTPException
from models import SessionLocal, User, Habit, CheckIn, ReportLog
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()


# FastAPI app instance
app = FastAPI()


@app.get("/")
def index():
    return {"Hello, FastAPI Habit Tracker"}


#POST /users – Register a user
@app.post("/users")
async def create_user(name: str, email: str):
    db = SessionLocal()
    db_user = User(name=name, email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



#POST /habits – Create a habit for a user
#user_id, title, description, frequency (daily/weekly), created_at
@app.post("/habits")
async def create_habit(user_id : int, title: str, description: str, frequency: str ):
    db = SessionLocal()
    db_habit = Habit(user_id=user_id,title=title, description=description, frequency=frequency)
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit


#POST /habits/{id}/check-in – Mark habit as completed for the day
@app.post("/habits")
async def create_habit(user_id : int, title: str, description: str, frequency: str ):
    db = SessionLocal()
    db_habit = Habit(user_id=user_id,title=title, description=description, frequency=frequency)
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit



@app.post("/habits/{habit_id}/check-in")
def check_in(habit_id: int):
    db = SessionLocal()
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    today = datetime.date.today()

    existing = db.query(CheckIn).filter_by(habit_id=habit_id, date=today).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in today")

    db_check = CheckIn(habit_id=habit_id, date=today)
    db.add(db_check)
    db.commit()
    db.refresh(db_check)
    return db_check


@app.get("/habits/{id}/stats")
def habit_stats(id: int):
    db= SessionLocal()
    habit = db.query(Habit).filter(Habit.id == id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    checkins = db.query(CheckIn).filter_by(habit_id=id).order_by(CheckIn.date).all()
    total_checkins = len(checkins)
    first_date = checkins[0].date if checkins else None
    last_date = checkins[-1].date if checkins else None

    return {
        "habit_id": habit.id,
        "title": habit.title,
        "frequency": habit.frequency,
        "total_checkins": total_checkins,
        "first_checkin": first_date,
        "last_checkin": last_date,
    }


def send_weekly_reports():
    db = SessionLocal()
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())  # Monday

    users = db.query(User).all()

    for user in users:
        existing_log = db.query(ReportLog).filter(
            ReportLog.user_id == user.id,
            ReportLog.week_start == week_start
        ).first()

        if existing_log:
            continue

        habits = db.query(Habit).filter(Habit.user_id == user.id).all()
        report = f"Weekly Report for {user.name}\n\n"

        for habit in habits:
            habit_start = habit.created_at.date()
            report_end_date = week_start + datetime.timedelta(days=6)  # Sunday
            report_end = min(today, report_end_date)

            total_days = (report_end - habit_start).days + 1
            if total_days < 1:
                continue  # Habit started after report period, skip

            checkins = db.query(CheckIn).filter(
                CheckIn.habit_id == habit.id,
                CheckIn.date >= habit_start,
                CheckIn.date <= report_end
            ).all()

            if habit.frequency == "daily":
                expected = total_days
            else:
                expected = total_days // 7

            completed = len(checkins)
            missed = expected - completed
            percent = int((completed / expected) * 100) if expected > 0 else 0

            if percent >= 80:
                suggestion = "Great job, keep it up!"
            else:
                suggestion = "Try to be more consistent next week."

            report += f"Habit: {habit.title}\n"
            report += f"Started on: {habit_start.strftime('%d-%b-%Y')}\n"
            report += f"Progress from {habit_start.strftime('%d-%b-%Y')} to {report_end.strftime('%d-%b-%Y')}:\n"
            report += f"Completed: {completed}/{expected} ({percent}%)\n"
            report += f"Missed Days: {missed}\n"
            report += f"Suggestion: {suggestion}\n\n"

        try:
            send_email(user.email, report)
            status = "sent"
        except Exception as e:
            print(f"Failed to send report to {user.email}: {e}")
            status = "failed"

        report_log = ReportLog(
            user_id=user.id,
            week_start=week_start,
            generated_at=datetime.datetime.utcnow(),
            status=status
        )
        db.add(report_log)
        db.commit()

    db.close()




def send_email(to_email: str, content: str):
    message = Mail(
        from_email=os.getenv('From_Email'),
        to_emails=to_email,
        subject='Your Weekly Habit Tracker Report',
        plain_text_content=content
    )

    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(f"Email sent to {to_email} - Status Code: {response.status_code}")
    except Exception as e:
        print(f"Failed to send email to {to_email}")
        print(str(e))



def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_weekly_reports, 'cron', day_of_week='sun', hour=12, minute=0)
    scheduler.start()

@app.on_event("startup")
def startup_event():
    start_scheduler()


@app.post("/reports/test")
def test_weekly_report():
    try:
        send_weekly_reports()
        return {"message": "Weekly reports sent successfully."}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app)
