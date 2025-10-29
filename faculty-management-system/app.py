from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, date, timedelta
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'faculty-management-enhanced-system'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///faculty.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database
db = SQLAlchemy(app)

# Database Models


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(10), nullable=False)


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)


class Syllabus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(300), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.String(20))


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(300))
    notified = db.Column(db.Boolean, default=False)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(20), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    marks = db.Column(db.Text)


# Sample data
SE_STUDENTS = [
    {"name": "Alice Johnson", "roll": "SE001",
        "email": "alice@college.edu", "phone": "1234567890"},
    {"name": "Bob Smith", "roll": "SE002",
        "email": "bob@college.edu", "phone": "1234567891"},
    {"name": "Carol Davis", "roll": "SE003",
        "email": "carol@college.edu", "phone": "1234567892"},
    {"name": "David Wilson", "roll": "SE004",
        "email": "david@college.edu", "phone": "1234567893"},
    {"name": "Eva Brown", "roll": "SE005",
        "email": "eva@college.edu", "phone": "1234567894"}
]

TE_STUDENTS = [
    {"name": "Ivy Chen", "roll": "TE001",
        "email": "ivy@college.edu", "phone": "1234567895"},
    {"name": "Jack Anderson", "roll": "TE002",
        "email": "jack@college.edu", "phone": "1234567896"},
    {"name": "Karen White", "roll": "TE003",
        "email": "karen@college.edu", "phone": "1234567897"},
    {"name": "Leo Martin", "roll": "TE004",
        "email": "leo@college.edu", "phone": "1234567898"},
    {"name": "Mia Garcia", "roll": "TE005",
        "email": "mia@college.edu", "phone": "1234567899"}
]

SAMPLE_SYLLABUS = {
    'SE': {
        'Software Engineering': ['Introduction to SE', 'SDLC', 'Requirements'],
        'Data Structures': ['Arrays', 'Linked Lists', 'Stacks']
    },
    'TE': {
        'Database Systems': ['DB Concepts', 'SQL', 'Normalization'],
        'Computer Networks': ['Network Basics', 'TCP/IP', 'Security']
    }
}

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ========== ROUTES ==========


@app.route('/')
def dashboard():
    today = date.today().strftime('%Y-%m-%d')

    today_lectures = Event.query.filter_by(
        date=today, type='lecture').count() or 2
    total_attendance = Attendance.query.count() or 1
    present_count = Attendance.query.filter_by(status='Present').count()
    attendance_percentage = round((present_count / total_attendance * 100), 1)
    assignments_count = Assignment.query.count()
    total_syllabus = Syllabus.query.count() or 1
    completed_syllabus = Syllabus.query.filter_by(completed=True).count()
    syllabus_percentage = round((completed_syllabus / total_syllabus * 100), 1)
    total_students = Student.query.count()
    upcoming_events = Event.query.filter(Event.date >= today).order_by(
        Event.date, Event.time).limit(5).all()

    return render_template('dashboard.html',
                           today_lectures=today_lectures,
                           attendance_percentage=attendance_percentage,
                           assignments_count=assignments_count,
                           syllabus_percentage=syllabus_percentage,
                           total_students=total_students,
                           upcoming_events=upcoming_events)


@app.route('/get_attendance_chart_data')
def get_attendance_chart_data():
    present_count = Attendance.query.filter_by(status='Present').count() or 8
    absent_count = Attendance.query.filter_by(status='Absent').count() or 2
    return jsonify({'present': present_count, 'absent': absent_count})


@app.route('/syllabus_progress')
def syllabus_progress():
    total = Syllabus.query.count() or 1
    completed = Syllabus.query.filter_by(completed=True).count()
    return jsonify({
        'completed': completed,
        'total': total,
        'percentage': round((completed / total * 100), 1)
    })

# ========== CALENDAR ROUTES ==========


@app.route('/calendar')
def calendar():
    events = Event.query.order_by(Event.date, Event.time).all()
    return render_template('calendar.html', events=events)


@app.route('/add_event', methods=['POST'])
def add_event():
    title = request.form['title']
    event_date = request.form['date']
    time = request.form['time']
    event_type = request.form['type']
    description = request.form['description']

    new_event = Event(title=title, date=event_date, time=time,
                      type=event_type, description=description)
    db.session.add(new_event)
    db.session.commit()
    flash('Event added successfully!', 'success')
    return redirect(url_for('calendar'))


@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        event.title = request.form['title']
        event.date = request.form['date']
        event.time = request.form['time']
        event.type = request.form['type']
        event.description = request.form['description']
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('calendar'))
    return render_template('edit_event.html', event=event)


@app.route('/delete_event/<int:event_id>')
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('calendar'))

# ========== ATTENDANCE ROUTES ==========


@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        year = request.form['year']
        subject = request.form['subject']
        attendance_date = request.form['date']

        students = SE_STUDENTS if year == 'SE' else TE_STUDENTS
        for student_data in students:
            status = request.form.get(
                f"status_{student_data['name']}", 'Absent')
            attendance_record = Attendance(
                date=attendance_date,
                year=year,
                subject=subject,
                student_name=student_data['name'],
                status=status
            )
            db.session.add(attendance_record)

        db.session.commit()
        flash('Attendance saved successfully!', 'success')
        return redirect(url_for('attendance'))

    return render_template('attendance.html')


@app.route('/attendance_records')
def attendance_records():
    records = Attendance.query.order_by(Attendance.date.desc()).all()
    return render_template('attendance_records.html', records=records)


@app.route('/attendance_stats')
def attendance_stats():
    return render_template('attendance_stats.html')

# ========== ASSIGNMENT ROUTES ==========


@app.route('/assignments', methods=['GET', 'POST'])
def assignments():
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        subject = request.form['subject']
        description = request.form['description']
        file = request.files['file']

        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_assignment = Assignment(
                title=title, year=year, subject=subject,
                filename=filename, upload_date=date.today().strftime('%Y-%m-%d'),
                description=description
            )
            db.session.add(new_assignment)
            db.session.commit()
            flash('Assignment uploaded successfully!', 'success')
        else:
            flash('Please select a file to upload', 'error')

    assignments = Assignment.query.order_by(
        Assignment.upload_date.desc()).all()
    return render_template('assignments.html', assignments=assignments)


@app.route('/delete_assignment/<int:assignment_id>')
def delete_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    try:
        os.remove(os.path.join(
            app.config['UPLOAD_FOLDER'], assignment.filename))
    except:
        pass
    db.session.delete(assignment)
    db.session.commit()
    flash('Assignment deleted successfully!', 'success')
    return redirect(url_for('assignments'))

# ========== NOTES ROUTES ==========


@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        subject = request.form['subject']
        description = request.form['description']
        file = request.files['file']

        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_note = Note(
                title=title, year=year, subject=subject,
                filename=filename, upload_date=date.today().strftime('%Y-%m-%d'),
                description=description
            )
            db.session.add(new_note)
            db.session.commit()
            flash('Notes uploaded successfully!', 'success')
        else:
            flash('Please select a file to upload', 'error')

    notes = Note.query.order_by(Note.upload_date.desc()).all()
    return render_template('notes.html', notes=notes)


@app.route('/delete_note/<int:note_id>')
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], note.filename))
    except:
        pass
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully!', 'success')
    return redirect(url_for('notes'))

# ========== SYLLABUS ROUTES ==========


@app.route('/syllabus_tracker')
def syllabus_tracker():
    syllabus_data = Syllabus.query.all()
    progress_data = {}
    for topic in syllabus_data:
        key = f"{topic.year} - {topic.subject}"
        if key not in progress_data:
            progress_data[key] = {'total': 0, 'completed': 0}
        progress_data[key]['total'] += 1
        if topic.completed:
            progress_data[key]['completed'] += 1

    return render_template('syllabus_tracker.html', syllabus_data=syllabus_data, progress_data=progress_data)


@app.route('/update_syllabus', methods=['POST'])
def update_syllabus():
    topic_id = request.form['topic_id']
    completed = request.form.get('completed') == 'true'
    topic = Syllabus.query.get(topic_id)
    if topic:
        topic.completed = completed
        topic.completion_date = date.today().strftime('%Y-%m-%d') if completed else None
        db.session.commit()
    return jsonify({'status': 'success'})


@app.route('/init_syllabus')
def init_syllabus():
    Syllabus.query.delete()
    for year, subjects in SAMPLE_SYLLABUS.items():
        for subject, topics in subjects.items():
            for topic in topics:
                new_topic = Syllabus(
                    year=year, subject=subject, topic=topic, completed=False)
                db.session.add(new_topic)
    db.session.commit()
    flash('Syllabus initialized with sample data!', 'success')
    return redirect(url_for('syllabus_tracker'))

# ========== STUDENT ROUTES ==========


@app.route('/students')
def students():
    students = Student.query.all()
    return render_template('students.html', students=students)


@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    roll_number = request.form['roll_number']
    year = request.form['year']
    email = request.form['email']
    phone = request.form['phone']

    existing = Student.query.filter_by(roll_number=roll_number).first()
    if existing:
        flash('Student with this roll number already exists!', 'error')
        return redirect(url_for('students'))

    new_student = Student(name=name, roll_number=roll_number,
                          year=year, email=email, phone=phone, marks='{}')
    db.session.add(new_student)
    db.session.commit()
    flash('Student added successfully!', 'success')
    return redirect(url_for('students'))


@app.route('/edit_student/<int:student_id>', methods=['POST'])
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.name = request.form['name']
    student.roll_number = request.form['roll_number']
    student.year = request.form['year']
    student.email = request.form['email']
    student.phone = request.form['phone']
    db.session.commit()
    flash('Student updated successfully!', 'success')
    return redirect(url_for('students'))


@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('students'))


@app.route('/student_marks/<int:student_id>')
def student_marks(student_id):
    student = Student.query.get_or_404(student_id)
    marks = json.loads(student.marks) if student.marks else {}
    return render_template('student_marks.html', student=student, marks=marks)


@app.route('/update_marks/<int:student_id>', methods=['POST'])
def update_marks(student_id):
    student = Student.query.get_or_404(student_id)
    subject = request.form['subject']
    marks = request.form['marks']
    current_marks = json.loads(student.marks) if student.marks else {}
    current_marks[subject] = marks
    student.marks = json.dumps(current_marks)
    db.session.commit()
    flash('Marks updated successfully!', 'success')
    return redirect(url_for('student_marks', student_id=student_id))

# ========== FILE DOWNLOAD ==========


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ========== DATABASE INITIALIZATION ==========


def init_db():
    with app.app_context():
        db.create_all()

        # Add sample events
        if Event.query.count() == 0:
            sample_events = [
                Event(title='SE Lecture - Software Engineering',
                      date=date.today().strftime('%Y-%m-%d'), time='09:00', type='lecture'),
                Event(title='TE Lecture - Database Systems',
                      date=date.today().strftime('%Y-%m-%d'), time='11:00', type='lecture'),
                Event(title='Department Meeting', date=date.today().strftime(
                    '%Y-%m-%d'), time='14:00', type='meeting')
            ]
            for event in sample_events:
                db.session.add(event)

        # Add sample students
        if Student.query.count() == 0:
            for student_data in SE_STUDENTS:
                student = Student(
                    name=student_data['name'],
                    roll_number=student_data['roll'],
                    year='SE',
                    email=student_data['email'],
                    phone=student_data['phone'],
                    marks='{}'
                )
                db.session.add(student)

            for student_data in TE_STUDENTS:
                student = Student(
                    name=student_data['name'],
                    roll_number=student_data['roll'],
                    year='TE',
                    email=student_data['email'],
                    phone=student_data['phone'],
                    marks='{}'
                )
                db.session.add(student)

        db.session.commit()


# Create necessary folders
if not os.path.exists('templates'):
    os.makedirs('templates')
if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

if __name__ == '__main__':
    init_db()
    print("✅ Enhanced Faculty Management System starting...")
    print("🌐 Open: http://localhost:5000")
    app.run(debug=True)
