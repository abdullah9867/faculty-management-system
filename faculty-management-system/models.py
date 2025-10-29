from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(10), nullable=False)  # Present/Absent

    def __repr__(self):
        return f'<Attendance {self.student_name} - {self.status}>'


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Assignment {self.title}>'


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Note {self.title}>'


class Syllabus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(300), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Syllabus {self.topic}>'


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # lecture/meeting
    description = db.Column(db.String(300))

    def __repr__(self):
        return f'<Event {self.title}>'
