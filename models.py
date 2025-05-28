from sqlalchemy import Column, Integer, String, DateTime, create_engine, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=False)
    name = Column(String, index=True, nullable=False)
    email = Column(String, index=True, nullable=False)
    created = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated = Column(DateTime, default=datetime.utcnow,onupdate=datetime.utcnow, nullable=False)


class Habit(Base):
    __tablename__ = 'habits'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    frequency = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class CheckIn(Base):
    __tablename__ = 'check_ins'

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey('habits.id'), nullable=False, index=True)
    date = Column(Date, nullable=False)


class ReportLog(Base):
    __tablename__ = 'report_logs'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    week_start = Column(Date, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)