# Habit Tracker API (FastAPI + SendGrid)

A backend API that allows users to create habits, check in on them daily or weekly, and receive weekly progress reports via email. Built using FastAPI, SQLAlchemy, SendGrid, and APScheduler.

---

## Features

- Register users and their habits
- Daily/weekly habit tracking
- Check-in endpoint
- Weekly email reports with:
  - Percentage of completion
  - Missed days
  - Suggestions
- Automated weekly reports every Sunday
- SendGrid integration for sending email

---

## Tech Stack

- FastAPI
- SQLAlchemy
- SendGrid
- APScheduler
- SQLite

---

## Installation Instructions

### 1. Clone the Repository

```bash

git clone https://github.com/fardansheikh01/HabitTracker.git
cd HabitTracker

```

### 2. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Rename and edit 
```
.env.example
```
to 
```
.env
```
and fill in the values before running the app

### 5. Run the Application
```bash
uvicorn main:app --reload
```

### 6. Visit the API docs: 
(http://127.0.0.1:8000/docs)

and test the endpoints