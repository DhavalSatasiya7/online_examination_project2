import uuid
import os
import random
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename, send_from_directory

from db import get_connection
from certificate import generate_certificate

from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas as pdf_canvas
from xml.sax.saxutils import escape

app = Flask(__name__)


# ==========================
# EMAIL CONFIGURATION
# ==========================

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = (
    os.environ.get('MAIL_DEFAULT_SENDER') or app.config['MAIL_USERNAME']
)

mail = Mail(app)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(32)

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
EXCEL_UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXCEL_UPLOAD_FOLDER, exist_ok=True)

ADMIN_NOTIFY_EMAIL = os.environ.get('ADMIN_NOTIFY_EMAIL', '')


def save_profile_photo(file_storage):
    if not file_storage or not getattr(file_storage, "filename", ""):
        return None

    original = secure_filename(file_storage.filename)
    if not original:
        return None

    name, ext = os.path.splitext(original)
    if ext.lower() not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        ext = ".jpg"

    filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
    file_storage.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return filename


def send_email(subject, recipients, body, attachments=None):
    cleaned = []
    for recipient in recipients or []:
        if recipient and str(recipient).strip():
            cleaned.append(str(recipient).strip())

    if not cleaned:
        print("EMAIL SKIPPED: no recipients")
        return False

    try:
        msg = Message(
            subject=subject,
            sender=app.config["MAIL_DEFAULT_SENDER"],
            recipients=cleaned
        )
        msg.body = body

        for attachment in attachments or []:
            path = attachment.get("path")
            if not path or not os.path.exists(path):
                continue
            with open(path, "rb") as handle:
                msg.attach(
                    attachment.get("name") or os.path.basename(path),
                    attachment.get("mime") or "application/octet-stream",
                    handle.read()
                )

        mail.send(msg)
        print("EMAIL SENT:", subject, "->", cleaned)
        return True

    except Exception as e:
        print("EMAIL ERROR:", type(e).__name__, e)
        return False


def get_all_student_emails():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT fullname, email
        FROM users
        WHERE email IS NOT NULL AND email <> ''
    """)
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return students


def notify_students_exam_scheduled(exam_name, subject_name, duration, total_marks):
    students = get_all_student_emails()
    sent = 0

    for student in students:
        ok = send_email(
            subject=f"Exam Scheduled: {exam_name}",
            recipients=[student["email"]],
            body=f"""Hello {student['fullname']},

A new examination has been scheduled in the Online Examination System.

Exam     : {exam_name}
Subject  : {subject_name}
Duration : {duration} minutes
Marks    : {total_marks}

Please login to your dashboard and attempt the exam on time.

Thank you.
Online Examination System
"""
        )
        if ok:
            sent += 1

    send_email(
        subject=f"Exam Conducted / Scheduled: {exam_name}",
        recipients=[ADMIN_NOTIFY_EMAIL],
        body=f"""Hello Admin,

The following exam has been scheduled and students have been notified.

Exam     : {exam_name}
Subject  : {subject_name}
Duration : {duration} minutes
Marks    : {total_marks}
Students notified : {sent}

Online Examination System
"""
    )

    return sent

# ==========================================================
# PROCTORING FILE STORAGE
# ==========================================================

PROCTORING_FOLDER = "static/proctoring"

VIDEO_FOLDER = os.path.join(
    PROCTORING_FOLDER,
    "videos"
)

AUDIO_FOLDER = os.path.join(
    PROCTORING_FOLDER,
    "audio"
)

SCREENSHOT_FOLDER = os.path.join(
    PROCTORING_FOLDER,
    "screenshots"
)

os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)



# ==========================
# HOME PAGE
# ==========================
@app.route('/')
def home():

    student = None

    if 'username' in session:

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT fullname,email,mobile,photo
            FROM users
            WHERE username=%s
        """, (session['username'],))

        student = cursor.fetchone()

        cursor.close()
        conn.close()

    return render_template(
        "index.html",
        student=student
    )

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():

    if "username" not in session:
        return redirect(url_for("login_page"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM users
        WHERE username=%s
    """, (session["username"],))

    student = cursor.fetchone()

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        mobile = request.form["mobile"]

        photo = student["photo"]

        if "photo" in request.files:
            saved_name = save_profile_photo(request.files["photo"])
            if saved_name:
                photo = saved_name

        cursor.execute("""
        UPDATE users
        SET
            fullname=%s,
            email=%s,
            mobile=%s,
            photo=%s
        WHERE username=%s
        """,
        (
            fullname,
            email,
            mobile,
            photo,
            session["username"]
        ))

        conn.commit()

        flash("Profile Updated Successfully")

        return redirect(url_for("dashboard"))

    cursor.close()
    conn.close()

    return render_template(
        "edit_profile.html",
        student=student
    )

# Admin Credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"



# ==========================
# ADMIN LOGIN
# ==========================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session['admin'] = True
            session['admin_name'] = username

            flash("Admin Login Successful!", "success")

            return redirect(url_for('admin_dashboard'))

        flash("Invalid Username or Password!", "danger")

    return render_template('admin_login.html')


# ==========================
# ADMIN DASHBOARD
# ==========================
@app.route('/admin/dashboard')
def admin_dashboard():

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # Total Students
        cursor.execute("SELECT COUNT(*) AS total FROM users")
        total_students = cursor.fetchone()['total']

        # Total Questions
        cursor.execute("SELECT COUNT(*) AS total FROM questions")
        total_questions = cursor.fetchone()['total']

        # Total Subjects
        cursor.execute("SELECT COUNT(*) AS total FROM subjects")
        total_subjects = cursor.fetchone()['total']

        # Total Exams Taken
        cursor.execute("""
        SELECT COUNT(*) AS total_exams
        FROM student_exam
        """)

        total_exams_taken = cursor.fetchone()["total_exams"]

        # PASS Students
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM results
            WHERE status='PASS'
        """)
        total_pass = cursor.fetchone()['total']

        # FAIL Students
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM results
            WHERE status='FAIL'
        """)
        total_fail = cursor.fetchone()['total']

        # Average Score
        cursor.execute("""
            SELECT AVG(score) AS avg_score
            FROM results
        """)
        avg = cursor.fetchone()

        average_score = round(avg["avg_score"],2) if avg["avg_score"] else 0

        total_result = total_pass + total_fail

        if total_result > 0:

            pass_percent = round((total_pass / total_result) * 100,2)
            fail_percent = round((total_fail / total_result) * 100,2)

        else:

            pass_percent = 0
            fail_percent = 0

        cursor.execute("""
        SELECT *
        FROM notifications
        ORDER BY created_at DESC
        LIMIT 10
        """)

        notifications = cursor.fetchall()

        cursor.execute("""
        SELECT COUNT(*)
        AS total
        FROM notifications
        WHERE is_read=0
        """)

        count = cursor.fetchone()["total"]

        cursor.execute("""
        SELECT COUNT(*)
        FROM notifications
        WHERE is_read=0
        """)

        notification_count = cursor.fetchone()['COUNT(*)']


    except Exception as e:

        print("Dashboard Error :", e)

        total_students = 0
        total_questions = 0
        total_subjects = 0
        total_exams_taken = 0
        total_pass = 0
        total_fail = 0
        average_score = 0
        pass_percent = 0
        fail_percent = 0


    finally:

        cursor.close()
        conn.close()

    return render_template(

        "admin_dashboard.html",

        total_students=total_students,

        total_questions=total_questions,

        total_subjects=total_subjects,

        total_exams_taken=total_exams_taken,

        total_pass=total_pass,

        total_fail=total_fail,

        average_score=average_score,

        pass_percent=pass_percent,

        fail_percent=fail_percent,

        notifications = notifications,

        notification_count=count,

        notification_count1=notification_count
     )

@app.route("/notifications")
def view_notifications():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
    SELECT *
    FROM notifications
    ORDER BY created_at DESC
    """)

    notifications = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "notifications.html",
        notifications=notifications
    )

@app.route("/read_notifications")
def read_notifications():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE notifications
    SET is_read=1
    """)

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("admin_dashboard"))

@app.route("/mark_all_read")
def mark_all_read():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE notifications
    SET is_read=1
    WHERE is_read=0
    """)

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("view_notifications"))

# ==========================
# ADMIN LOGOUT
# ==========================
@app.route('/admin/logout')
def admin_logout():

    session.clear()

    flash("Admin Logged Out Successfully", "info")

    return redirect(url_for('admin_login'))

# ==========================
# VIEW STUDENTS
# ==========================
@app.route('/view-students')
def view_students():

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM users
        ORDER BY id DESC
    """)

    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'view_students.html',
        students=students
    )


# ==========================
# VIEW SUBJECTS
# ==========================
@app.route('/view-subjects')
def view_subjects():

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM subjects
        ORDER BY id DESC
    """)

    subjects = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'view_subjects.html',
        subjects=subjects
    )

@app.route('/admin/add-subject', methods=['GET', 'POST'])
def add_subject():

    if request.method == 'POST':

        subject_name = request.form['subject_name']

        conn = get_connection()
        cursor = conn.cursor()

        # Insert Subject
        cursor.execute("""
        INSERT INTO subjects(subject_name)
        VALUES(%s)
        """, (subject_name,))

        conn.commit()

        # Get inserted subject id
        subject_id = cursor.lastrowid

        # Create Exam Automatically
        cursor.execute("""
        INSERT INTO exams
        (
            subject_id,
            exam_name,
            duration,
            total_marks
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            subject_id,
            subject_name + " Exam",
            30,
            20
        ))

        conn.commit()

        cursor.close()
        conn.close()

        notify_students_exam_scheduled(
            exam_name=subject_name + " Exam",
            subject_name=subject_name,
            duration=30,
            total_marks=20
        )

        flash("Subject added and exam emails sent to students.", "success")

        return redirect(url_for('admin_dashboard'))

    return render_template("add_subject.html")

@app.route('/delete-subject/<int:subject_id>')
def delete_subject(subject_id):

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM subjects WHERE id=%s",
        (subject_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash(
        "Subject Deleted Successfully",
        "success"
    )

    return redirect(
        url_for('view_subjects')
    )

@app.route('/add-question', methods=['GET','POST'])
def add_question():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()

    if request.method == 'POST':

        subject_id = request.form['subject_id']
        question_text = request.form['question_text']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_option = request.form['correct_option']

        cursor.execute("""
            INSERT INTO questions
            (
                subject_id,
                question_text,
                option1,
                option2,
                option3,
                option4,
                correct_option
            )
            VALUES(%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            subject_id,
            question_text,
            option1,
            option2,
            option3,
            option4,
            correct_option
        ))

        conn.commit()

        flash("Question Added Successfully")

        return redirect(url_for('admin_dashboard'))

    return render_template(
        'add_question.html',
        subjects=subjects
    )


@app.route('/admin/view-questions')
def view_questions():

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            q.id,
            s.subject_name,
            q.question_text,
            q.correct_option
        FROM questions q
        JOIN subjects s
            ON q.subject_id = s.id
        ORDER BY q.id DESC
    """)

    questions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'view_questions.html',
        questions=questions
    )

@app.route('/delete-question/<int:q_id>')
def delete_question(q_id):

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM questions WHERE id=%s",
        (q_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash("Question Deleted Successfully", "success")

    return redirect(url_for('view_questions'))

@app.route("/edit_question/<int:q_id>", methods=["GET", "POST"])
def edit_question(q_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # ============================
    # Update Question
    # ============================

    if request.method == "POST":

        subject_id = request.form["subject_id"]

        question_text = request.form["question_text"]

        option1 = request.form["option1"]

        option2 = request.form["option2"]

        option3 = request.form["option3"]

        option4 = request.form["option4"]

        correct_option = request.form["correct_option"]

        cursor.execute("""
        UPDATE questions
        SET
            subject_id=%s,
            question_text=%s,
            option1=%s,
            option2=%s,
            option3=%s,
            option4=%s,
            correct_option=%s
        WHERE id=%s
        """,
        (
            subject_id,
            question_text,
            option1,
            option2,
            option3,
            option4,
            correct_option,
            q_id
        ))

        conn.commit()

        flash("Question Updated Successfully", "success")

        cursor.close()
        conn.close()

        return redirect(url_for("view_questions"))

    # ============================
    # Get Question
    # ============================

    cursor.execute("""
    SELECT *
    FROM questions
    WHERE id=%s
    """, (q_id,))

    question = cursor.fetchone()

    # ============================
    # Get Subjects
    # ============================

    cursor.execute("""
    SELECT *
    FROM subjects
    ORDER BY subject_name
    """)

    subjects = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "edit_question.html",
        question=question,
        subjects=subjects
    )

@app.route('/admin/view_results')
def view_results():

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            u.fullname,
            s.subject_name,
            r.score,
            r.total_questions,
            r.status,
            r.exam_date
        FROM results r
        INNER JOIN users u
            ON r.user_id = u.id
        INNER JOIN subjects s
            ON r.subject_id = s.id
        ORDER BY r.exam_date DESC
    """)

    results = cursor.fetchall()

    print(results)   # Debug

    cursor.close()
    conn.close()

    return render_template(
        'view_results.html',
        results=results
    )

# ==========================
# LOGIN PAGE
# ==========================
@app.route('/login', methods=['GET', 'POST'])
def login_page():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
        SELECT * FROM users
        WHERE username=%s AND password=%s 
        """

        cursor.execute(sql, (username, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session['student_id'] = user['id']
            session['username'] = user['username']
            session['fullname'] = user['fullname']

            flash("Login Successful")

            # Redirect back to Home Page
            return redirect(url_for('home'))

        flash("Invalid Username or Password")

    return render_template('login.html')


# ==========================
# REGISTER PAGE
# ==========================
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        fullname = request.form['fullname']
        username = request.form['username']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']

        photo = request.files.get('photo')
        filename = save_profile_photo(photo) or ""

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO users
        (
            fullname,
            username,
            email,
            mobile,
             password,
            photo
           
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            fullname,
            username,
            email,
            mobile,
            password,
            filename

        ))

        conn.commit()

        cursor.close()

        conn.close()

        flash("Registration Successful", "success")

        return redirect(url_for('login_page'))

    return render_template("register.html")
# ==========================
# EXAM BUTTON ROUTE
# ==========================
@app.route('/exam/<int:subject_id>')
def exam(subject_id):

    if 'username' not in session:
        return redirect(url_for('login_page'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
    SELECT *
    FROM questions
    WHERE subject_id=%s
    ORDER BY RAND()
    """, (subject_id,))

    questions = cursor.fetchall()

    # ===========================
    # Randomize Options
    # ===========================

    for q in questions:
        options = [
            {
                "text": q["option1"],
                "value": 1
            },
            {
                "text": q["option2"],
                "value": 2
            },
            {
                "text": q["option3"],
                "value": 3
            },
            {
                "text": q["option4"],
                "value": 4
            }
        ]

        random.shuffle(options)

        q["options"] = options

    cursor.close()
    conn.close()

    return render_template(
        "exam.html",
        questions=questions,
        subject_id=subject_id
    )

#submit exam

@app.route('/submit_exam/<int:subject_id>', methods=['POST'])
def submit_exam(subject_id):

    # =====================================================
    # LOGIN CHECK
    # =====================================================

    if 'student_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login_page'))

    student_id = session['student_id']

    # =====================================================
    # GET CURRENT ATTEMPT
    # =====================================================

    attempt_id = session.get('attempt_id')

    if not attempt_id:
        flash(
            "Exam attempt information is missing.",
            "danger"
        )
        return redirect(url_for('available_exams'))

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # =================================================
        # 1. GET QUESTIONS
        # =================================================

        cursor.execute("""
            SELECT
                id AS question_id,
                question_text,
                option1,
                option2,
                option3,
                option4,
                correct_option
            FROM questions
            WHERE subject_id = %s
        """, (subject_id,))

        questions = cursor.fetchall()

        if not questions:

            flash(
                "No questions found for this examination.",
                "danger"
            )

            return redirect(
                url_for(
                    'exam',
                    subject_id=subject_id
                )
            )

        # =================================================
        # 2. CALCULATE ANSWERS
        # =================================================

        total_questions = len(questions)

        attempted_questions = 0
        correct_answers = 0
        wrong_answers = 0

        for question in questions:

            question_id = str(question['question_id'])

            # exam.html uses:
            # name="answer_<question_id>"

            selected_option = request.form.get(
                f'answer_{question_id}'
            )

            if selected_option is None or selected_option == "":
                continue

            attempted_questions += 1

            if str(selected_option) == str(
                question['correct_option']
            ):

                correct_answers += 1

            else:

                wrong_answers += 1

        # =================================================
        # 3. UNATTEMPTED
        # =================================================

        unattempted_questions = (
            total_questions -
            attempted_questions
        )

        # =================================================
        # 4. NEGATIVE MARKING
        # =================================================

        score = (
            correct_answers -
            (wrong_answers * 0.25)
        )

        if score < 0:
            score = 0

        score = round(score, 1)

        # =================================================
        # 5. PERCENTAGE
        # =================================================

        if total_questions > 0:

            percentage = (
                score /
                total_questions
            ) * 100

        else:

            percentage = 0

        percentage = round(
            percentage,
            2
        )

        # =================================================
        # 6. PASS / FAIL
        # =================================================

        if percentage >= 40:
            status = "PASS"
        else:
            status = "FAIL"

        # =================================================
        # 7. BAND SCORE
        # =================================================

        if total_questions > 0:

            band_score = (
                score /
                total_questions
            ) * 9

        else:

            band_score = 0

        band_score = round(
            band_score,
            1
        )

        # =================================================
        # 8. GET SUBJECT NAME
        # =================================================

        cursor.execute("""
            SELECT subject_name
            FROM subjects
            WHERE id = %s
        """, (subject_id,))

        subject_row = cursor.fetchone()

        if not subject_row:
            raise Exception("Subject not found.")

        subject_name = subject_row['subject_name']

        # =================================================
        # 9. GET STUDENT NAME
        # =================================================

        cursor.execute("""
            SELECT fullname, email
            FROM users
            WHERE id = %s
        """, (student_id,))

        student_row = cursor.fetchone()

        if not student_row:
            raise Exception("Student not found.")

        student_name = student_row['fullname']
        student_email = student_row.get('email')

        # =================================================
        # 10. UPDATE STUDENT_EXAM
        # =================================================

        cursor.execute("""
            UPDATE student_exam
            SET
                status = 'Completed',
                score = %s,
                correct_answers = %s,
                wrong_answers = %s,
                total_questions = %s,
                attempted_questions = %s,
                end_time = NOW(),
                submitted_at = NOW()
            WHERE attempt_id = %s
              AND student_id = %s
        """, (
            score,
            correct_answers,
            wrong_answers,
            total_questions,
            attempted_questions,
            attempt_id,
            student_id
        ))

        if cursor.rowcount == 0:

            raise Exception(
                "Exam attempt was not found or does not belong to this student."
            )

        # =================================================
        # 11. INSERT INTO RESULTS
        # =================================================

        cursor.execute("""
            INSERT INTO results
            (
                user_id,
                subject_id,
                score,
                total_questions,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (
            student_id,
            subject_id,
            score,
            total_questions,
            status
        ))

        # =================================================
        # 12. INSERT INTO TEST HISTORY
        # =================================================

        cursor.execute("""
            INSERT INTO test_history
            (
                student_id,
                attempt_id,
                test_date,
                subject_name,
                band_score,
                status
            )
            VALUES
            (
                %s,
                %s,
                NOW(),
                %s,
                %s,
                'Completed'
            )
        """, (
            student_id,
            attempt_id,
            subject_name,
            band_score
        ))

        # =================================================
        # 13. COMMIT DATABASE
        # =================================================

        conn.commit()

        # =================================================
        # 14. GENERATE RESULT PDF + CERTIFICATE + EMAIL
        # =================================================
        exam_date = datetime.now().strftime("%d-%m-%Y")
        certificate_file = None
        certificate_path = None
        pdf_path = None

        try:
            pdf_path = generate_result_pdf(
                student_name=student_name,
                subject_name=subject_name,
                total_questions=total_questions,
                attempted_questions=attempted_questions,
                correct=correct_answers,
                wrong=wrong_answers,
                unanswered=unattempted_questions,
                score=score,
                band_score=band_score,
                status=status,
                exam_date=exam_date
            )
            session['pdf_file'] = (
                os.path.basename(pdf_path) if pdf_path else None
            )
        except Exception as pdf_error:
            print("RESULT PDF ERROR:", pdf_error)
            session.pop('pdf_file', None)

        try:
            if band_score > 6:
                certificate_path = generate_certificate(
                    student_name=student_name,
                    subject_name=subject_name,
                    band_score=band_score,
                    exam_date=exam_date
                )
                certificate_file = os.path.basename(certificate_path)
                session['certificate_file'] = certificate_file
            else:
                session.pop('certificate_file', None)
        except Exception as cert_error:
            print("CERTIFICATE ERROR:", cert_error)
            session.pop('certificate_file', None)

        try:
            send_result_email(
                student_email=student_email,
                student_name=student_name,
                subject_name=subject_name,
                score=score,
                band_score=band_score,
                status=status,
                pdf_file=pdf_path,
                certificate_file=certificate_path
            )
        except Exception as mail_error:
            print("RESULT EMAIL ERROR:", mail_error)

        # =================================================
        # 15. DEBUG INFORMATION
        # =================================================

        print("======================================")
        print("EXAM SUBMITTED SUCCESSFULLY")
        print("Student ID      :", student_id)
        print("Student Name    :", student_name)
        print("Attempt ID      :", attempt_id)
        print("Subject         :", subject_name)
        print("Total Questions :", total_questions)
        print("Attempted       :", attempted_questions)
        print("Correct         :", correct_answers)
        print("Wrong           :", wrong_answers)
        print("Unattempted     :", unattempted_questions)
        print("Score           :", score)
        print("Percentage      :", percentage)
        print("Band Score      :", band_score)
        print("Status          :", status)
        print("Certificate     :", certificate_file)
        print("======================================")

        # =================================================
        # 16. STORE LAST RESULT IN SESSION
        # =================================================

        session['last_score'] = score
        session['last_percentage'] = percentage
        session['last_correct'] = correct_answers
        session['last_wrong'] = wrong_answers
        session['last_attempted'] = attempted_questions
        session['last_unattempted'] = unattempted_questions
        session['last_band_score'] = band_score
        session['last_status'] = status

        # Used by dashboard success modal
        session['exam_submitted'] = True

        # =================================================
        # 17. CLEAR ACTIVE ATTEMPT
        # =================================================

        session.pop(
            'attempt_id',
            None
        )

        # =================================================
        # 18. SUCCESS MESSAGE
        # =================================================

        flash(
            "Exam submitted successfully!",
            "success"
        )

        # =================================================
        # 19. GO TO DASHBOARD
        # =================================================

        return redirect(
            url_for('dashboard')
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("======================================")
        print("SUBMIT EXAM ERROR:", str(e))
        print("======================================")

        flash(
            "Error while submitting examination: "
            + str(e),
            "danger"
        )

        return redirect(
            url_for(
                'exam',
                subject_id=subject_id
            )
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()



# ==========================
# DASHBOARD PAGE
# ==========================


@app.route('/dashboard')
def dashboard():

    # =====================================================
    # STUDENT LOGIN CHECK
    # =====================================================

    if 'student_id' not in session:
        flash(
            "Please login first.",
            "warning"
        )

        return redirect(
            url_for('login_page')
        )

    student_id = session['student_id']

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # =================================================
        # 1. COUNT COMPLETED TESTS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS tests_completed
            FROM student_exam
            WHERE student_id = %s
              AND status = 'Completed'
        """, (student_id,))

        row = cursor.fetchone()

        tests_completed = (
            row['tests_completed']
            if row else 0
        )

        # =================================================
        # 2. GET TEST HISTORY
        # =================================================

        cursor.execute("""
            SELECT
                se.attempt_id,
                se.submitted_at AS test_date,
                s.subject_name,
                se.score,
                se.total_questions,
                se.attempted_questions,
                se.correct_answers,
                se.wrong_answers,

                (
                    se.total_questions -
                    se.attempted_questions
                ) AS unattempted,

                ROUND(
                    (
                        se.score /
                        NULLIF(se.total_questions, 0)
                    ) * 100,
                    2
                ) AS percentage,

                th.band_score,
                th.status AS history_status

            FROM student_exam se

            INNER JOIN exams e
                ON se.exam_id = e.exam_id

            INNER JOIN subjects s
                ON e.subject_id = s.id

            LEFT JOIN test_history th
                ON th.attempt_id = se.attempt_id

            WHERE se.student_id = %s
              AND se.status = 'Completed'

            ORDER BY se.submitted_at DESC

        """, (student_id,))

        history = cursor.fetchall()

        # =================================================
        # 3. STUDENT PROFILE (PHOTO)
        # =================================================

        cursor.execute("""
            SELECT id, fullname, username, email, mobile, photo
            FROM users
            WHERE id = %s
        """, (student_id,))

        student = cursor.fetchone()

        # =================================================
        # 4. ACCOUNT STATUS
        # =================================================

        # users table does not contain status
        account_status = "Active"

        # =================================================
        # 4. RESULT PDF
        # =================================================

        pdf_file = session.get(
            'pdf_file'
        )

        # =================================================
        # 5. CERTIFICATE FILE
        # =================================================

        certificate_file = session.get(
            'certificate_file'
        )

        # =================================================
        # 6. EXAM SUBMITTED FLAG
        # =================================================

        exam_submitted = session.pop(
            'exam_submitted',
            False
        )

        # =================================================
        # 7. RENDER DASHBOARD
        # =================================================

        return render_template(
            'dashboard.html',

            history=history,

            student=student,

            tests_completed=tests_completed,

            account_status=account_status,

            pdf_file=pdf_file,

            certificate_file=certificate_file,

            exam_submitted=exam_submitted
        )

    except Exception as e:

        print("====================================")
        print("DASHBOARD ERROR:", str(e))
        print("====================================")

        return f"""
        <h2>Dashboard Error</h2>
        <p>{e}</p>
        <p>Please check the Flask terminal for the complete error.</p>
        """, 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ==========================
# LISTENING TEST CONFIRMATION
# ==========================

@app.route('/listening_confirm/<int:subject_id>')
def listening_confirm(subject_id):

    if 'student_id' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            e.exam_id,
            e.subject_id,
            e.exam_name,
            e.duration,
            e.total_marks,
            s.subject_name
        FROM exams e
        INNER JOIN subjects s
            ON e.subject_id = s.id
        WHERE e.subject_id = %s
        LIMIT 1
    """, (subject_id,))

    exam = cursor.fetchone()

    cursor.close()
    conn.close()

    if not exam:
        flash('Exam not found.', 'danger')
        return redirect(url_for('available_exams'))

    return render_template(
        'listening_confirm.html',
        exam=exam
    )
# ==========================================================
# PROCTORING EVENT
# NO DATABASE TABLE
# ==========================================================

@app.route('/log-proctoring-event', methods=['POST'])
def log_proctoring_event():

    if 'student_id' not in session:
        return jsonify({
            'success': False,
            'message': 'Not logged in'
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    event_type = data.get(
        'event_type',
        'UNKNOWN'
    )

    event_message = data.get(
        'event_message',
        ''
    )

    # ------------------------------------------------------
    # VIOLATIONS
    # ------------------------------------------------------

    violation_types = [
        'WINDOW_HIDDEN',
        'WINDOW_BLUR',
        'TAB_SWITCH',
        'FULLSCREEN_EXIT',
        'NO_FACE',
        'MULTIPLE_FACES',
        'PHONE_DETECTED',
        'CAMERA_DISCONNECTED',
        'MICROPHONE_DISCONNECTED'
    ]

    if event_type in violation_types:

        warning_count = session.get(
            'proctoring_warnings',
            0
        )

        warning_count += 1

        session['proctoring_warnings'] = warning_count

    else:

        warning_count = session.get(
            'proctoring_warnings',
            0
        )

    return jsonify({
        'success': True,
        'warning_count': warning_count,
        'event': event_type
    })

# ==========================================================
# VIDEO UPLOAD
# ==========================================================

@app.route(
    '/upload-proctoring-video',
    methods=['POST']
)
def upload_proctoring_video():

    if 'student_id' not in session:
        return jsonify({
            'success': False
        }), 401

    if not session.get(
        'proctoring_consent'
    ):
        return jsonify({
            'success': False,
            'message': 'Recording consent not available.'
        }), 403

    video = request.files.get(
        'video'
    )

    if not video:
        return jsonify({
            'success': False,
            'message': 'Video not received.'
        }), 400

    attempt_id = session.get(
        'attempt_id'
    )

    if not attempt_id:
        return jsonify({
            'success': False,
            'message': 'Attempt not found.'
        }), 400

    filename = (
        f"attempt_{attempt_id}_"
        f"{uuid.uuid4().hex}.webm"
    )

    filepath = os.path.join(
        VIDEO_FOLDER,
        filename
    )

    video.save(filepath)

    return jsonify({
        'success': True,
        'filename': filename
    })

# ==========================================================
# AUDIO UPLOAD
# ==========================================================

@app.route(
    '/upload-proctoring-audio',
    methods=['POST']
)
def upload_proctoring_audio():

    if 'student_id' not in session:
        return jsonify({
            'success': False
        }), 401

    if not session.get(
        'proctoring_consent'
    ):
        return jsonify({
            'success': False
        }), 403

    audio = request.files.get(
        'audio'
    )

    if not audio:
        return jsonify({
            'success': False,
            'message': 'Audio not received.'
        }), 400

    attempt_id = session.get(
        'attempt_id'
    )

    filename = (
        f"attempt_{attempt_id}_"
        f"{uuid.uuid4().hex}.webm"
    )

    filepath = os.path.join(
        AUDIO_FOLDER,
        filename
    )

    audio.save(filepath)

    return jsonify({
        'success': True,
        'filename': filename
    })

# ==========================================================
# SCREENSHOT UPLOAD
# ==========================================================

@app.route(
    '/upload-proctoring-screenshot',
    methods=['POST']
)
def upload_proctoring_screenshot():

    if 'student_id' not in session:
        return jsonify({
            'success': False
        }), 401

    if not session.get(
        'proctoring_consent'
    ):
        return jsonify({
            'success': False
        }), 403

    screenshot = request.files.get(
        'screenshot'
    )

    if not screenshot:
        return jsonify({
            'success': False
        }), 400

    attempt_id = session.get(
        'attempt_id'
    )

    filename = (
        f"attempt_{attempt_id}_"
        f"{uuid.uuid4().hex}.jpg"
    )

    filepath = os.path.join(
        SCREENSHOT_FOLDER,
        filename
    )

    screenshot.save(filepath)

    return jsonify({
        'success': True,
        'filename': filename
    })

# ==========================================================
# SERVE PROCTORING FILES
# ==========================================================

@app.route(
    '/proctoring/video/<filename>'
)
def proctoring_video(filename):

    return send_from_directory(
        VIDEO_FOLDER,
        filename
    )


@app.route(
    '/proctoring/audio/<filename>'
)
def proctoring_audio(filename):

    return send_from_directory(
        AUDIO_FOLDER,
        filename
    )


@app.route(
    '/proctoring/screenshot/<filename>'
)
def proctoring_screenshot(filename):

    return send_from_directory(
        SCREENSHOT_FOLDER,
        filename
    )

@app.route('/admin/add_exam', methods=['GET', 'POST'])
def add_exam():
    if request.method == 'POST':

        subject_id = request.form['subject_id']
        exam_name = request.form['exam_name']
        duration = request.form['duration']
        total_marks = request.form['total_marks']

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO exams
        (subject_id, exam_name, duration, total_marks)
        VALUES (%s,%s,%s,%s)
        """, (
            subject_id,
            exam_name,
            duration,
            total_marks
        ))

        conn.commit()

        cursor.execute(
            "SELECT subject_name FROM subjects WHERE id=%s",
            (subject_id,)
        )
        subject_row = cursor.fetchone()
        subject_name = subject_row[0] if subject_row else "Subject"

        cursor.close()
        conn.close()

        notify_students_exam_scheduled(
            exam_name=exam_name,
            subject_name=subject_name,
            duration=duration,
            total_marks=total_marks
        )

        flash("Exam added and notification emails sent to students.")

        return redirect(url_for("admin_dashboard"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("add_exam.html", subjects=subjects)

@app.route('/view_exam')
def view_exam():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
    SELECT
        se.attempt_id,
        u.fullname,
        u.username,
        e.exam_name,
        s.subject_name,
        se.score,
        se.status,
        se.correct_answers,
        se.wrong_answers,
        se.total_questions,
        se.attempted_questions,
        se.start_time,
        se.end_time,
        se.submitted_at

    FROM student_exam se

    JOIN users u
        ON se.student_id = u.id

    JOIN exams e
        ON se.exam_id = e.exam_id

    JOIN subjects s
        ON e.subject_id = s.id

    ORDER BY se.attempt_id DESC
    """)

    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("view_exam.html", records=records)

@app.route("/edit_exam/<int:exam_id>", methods=["GET", "POST"])
def edit_exam(exam_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        exam_name = request.form["exam_name"]
        duration = request.form["duration"]

        cursor.execute("""
        UPDATE exams
        SET exam_name=%s,
            duration=%s
        WHERE exam_id=%s
        """, (exam_name, duration, exam_id))

        conn.commit()

        cursor.close()
        conn.close()

        flash("Exam Updated Successfully", "success")

        return redirect(url_for("view_exam"))

    cursor.execute("""
    SELECT *
    FROM exams
    WHERE exam_id=%s
    """, (exam_id,))

    exam = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("edit_exam.html", exam=exam)

@app.route("/delete_exam/<int:exam_id>")
def delete_exam(exam_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM exams
        WHERE exam_id = %s
    """, (exam_id,))

    conn.commit()

    cursor.close()
    conn.close()

    flash("Exam Deleted Successfully", "success")

    return redirect(url_for("view_exam"))

@app.route("/history")
def history():

    conn=get_connection()
    cursor=conn.cursor(dictionary=True)

    cursor.execute("""
    SELECT *
    FROM test_history
    ORDER BY id DESC
    """)

    history=cursor.fetchall()

    return render_template("history.html",history=history)

@app.route('/admin/results')
def admin_results():

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            r.*,
            s.subject_name
        FROM results r
        JOIN subjects s
        ON r.subject_id=s.id
        ORDER BY r.exam_date DESC
    """)

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'admin_results.html',
        results=results
    )

@app.route('/available_exams')
def available_exams():

    if 'student_id' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            e.exam_id,
            e.subject_id,
            e.exam_name,
            e.duration,
            e.total_marks,
            s.subject_name
        FROM exams e
        INNER JOIN subjects s
            ON e.subject_id = s.id
        ORDER BY e.exam_id DESC
    """)

    exams = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'available_exams.html',
        exams=exams
    )
# ==========================================================
# START EXAM
# NO PROCTORING TABLE USED
# ==========================================================

@app.route('/start_exam/<int:subject_id>')
def start_exam(subject_id):

    if 'student_id' not in session:
        return redirect(url_for('login'))

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # =====================================================
        # GET EXAM
        # =====================================================

        cursor.execute("""
            SELECT
                e.exam_id,
                e.subject_id,
                e.exam_name,
                e.duration,
                e.total_marks,
                s.subject_name
            FROM exams e
            INNER JOIN subjects s
                ON e.subject_id = s.id
            WHERE e.subject_id = %s
            LIMIT 1
        """, (subject_id,))

        exam = cursor.fetchone()

        if not exam:

            flash(
                'Exam not found.',
                'danger'
            )

            return redirect(
                url_for('available_exams')
            )

        # =====================================================
        # GET RANDOM QUESTIONS
        #
        # IMPORTANT:
        # Your table uses "id", not "question_id".
        # =====================================================

        cursor.execute("""
            SELECT
                id AS question_id,
                question_text,
                option1,
                option2,
                option3,
                option4,
                correct_option
            FROM questions
            WHERE subject_id = %s
            ORDER BY RAND()
        """, (subject_id,))

        questions = cursor.fetchall()

        if not questions:

            flash(
                'No questions available for this exam.',
                'warning'
            )

            return redirect(
                url_for('available_exams')
            )

        # =====================================================
        # CREATE STUDENT EXAM ATTEMPT
        # =====================================================

        cursor.close()
        conn.close()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO student_exam
            (
                student_id,
                exam_id,
                status,
                total_questions,
                start_time
            )
            VALUES
            (
                %s,
                %s,
                'started',
                %s,
                NOW()
            )
        """, (
            session['student_id'],
            exam['exam_id'],
            len(questions)
        ))

        attempt_id = cursor.lastrowid

        conn.commit()

        # =====================================================
        # SAVE ATTEMPT ID IN SESSION
        # =====================================================

        session['attempt_id'] = attempt_id

        return render_template(
            'exam.html',
            exam=exam,
            questions=questions,
            attempt_id=attempt_id
        )

    except Exception as e:

        if conn:

            try:
                conn.rollback()
            except Exception:
                pass

        print(
            "START EXAM ERROR:",
            str(e)
        )

        flash(
            'Unable to start the examination.',
            'danger'
        )

        return redirect(
            url_for('available_exams')
        )

    finally:

        try:

            if cursor:
                cursor.close()

        except Exception:
            pass

        try:

            if conn:
                conn.close()

        except Exception:
            pass
# ==========================
# LOGOUT
# ==========================
@app.route('/logout')
def logout():

    session.clear()

    flash("Logged Out Successfully")

    return redirect(url_for('home'))


from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
import os


def generate_result_pdf(
        student_name,
        subject_name,
        total_questions,
        attempted_questions,
        correct,
        wrong,
        unanswered,
        score,
        band_score,
        status,
        exam_date
):

    # -----------------------------------------------------
    # RESULT PDF FOLDER
    # -----------------------------------------------------

    folder = os.path.join(
        app.root_path,
        "generated_results"
    )

    os.makedirs(
        folder,
        exist_ok=True
    )


    # -----------------------------------------------------
    # SAFE FILE NAME
    # -----------------------------------------------------

    safe_student_name = secure_filename(
        str(student_name)
    )

    safe_subject_name = secure_filename(
        str(subject_name)
    )


    filename = (
        f"{safe_student_name}_"
        f"{safe_subject_name}_"
        f"Result.pdf"
    )


    pdf_path = os.path.join(
        folder,
        filename
    )


    # -----------------------------------------------------
    # PDF DOCUMENT
    # -----------------------------------------------------

    doc = SimpleDocTemplate(

        pdf_path,

        pagesize=(595, 842),

        rightMargin=30,

        leftMargin=30,

        topMargin=30,

        bottomMargin=30
    )


    styles = getSampleStyleSheet()

    story = []


    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "ONLINE EXAMINATION SYSTEM",
            styles["Title"]
        )
    )


    story.append(
        Paragraph(
            "RESULT CARD",
            styles["Heading2"]
        )
    )


    story.append(
        Spacer(1, 20)
    )


    # -----------------------------------------------------
    # STUDENT INFORMATION
    # -----------------------------------------------------

    student_data = [

        ["Student Name", student_name],

        ["Subject", subject_name],

        ["Exam Date", str(exam_date)],

        ["Status", status]

    ]


    student_table = Table(
        student_data,
        colWidths=[150, 350]
    )


    student_table.setStyle(
        TableStyle([

            (
                "GRID",
                (0,0),
                (-1,-1),
                0.5,
                colors.grey
            ),

            (
                "BACKGROUND",
                (0,0),
                (0,-1),
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0,0),
                (0,-1),
                "Helvetica-Bold"
            ),

            (
                "VALIGN",
                (0,0),
                (-1,-1),
                "MIDDLE"
            ),

            (
                "PADDING",
                (0,0),
                (-1,-1),
                8
            )

        ])
    )


    story.append(
        student_table
    )


    story.append(
        Spacer(1, 20)
    )


    # -----------------------------------------------------
    # PERFORMANCE
    # -----------------------------------------------------

    performance_data = [

        ["Performance", "Value"],

        ["Total Questions", str(total_questions)],

        ["Attempted", str(attempted_questions)],

        ["Correct Answers", str(correct)],

        ["Wrong Answers", str(wrong)],

        ["Unattempted", str(unanswered)],

        ["Score", f"{score:.1f}"],

        ["Percentage", f"{(score / total_questions * 100):.2f}%"
         if total_questions > 0 else "0.00%"],

        ["Band Score", f"{band_score:.1f}"],

        ["Result", status]

    ]


    performance_table = Table(
        performance_data,
        colWidths=[250, 250]
    )


    performance_table.setStyle(
        TableStyle([

            (
                "GRID",
                (0,0),
                (-1,-1),
                0.5,
                colors.grey
            ),

            (
                "BACKGROUND",
                (0,0),
                (-1,0),
                colors.HexColor("#0d6efd")
            ),

            (
                "TEXTCOLOR",
                (0,0),
                (-1,0),
                colors.white
            ),

            (
                "FONTNAME",
                (0,0),
                (-1,0),
                "Helvetica-Bold"
            ),

            (
                "FONTNAME",
                (0,1),
                (0,-1),
                "Helvetica-Bold"
            ),

            (
                "ALIGN",
                (1,0),
                (1,-1),
                "CENTER"
            ),

            (
                "PADDING",
                (0,0),
                (-1,-1),
                8
            )

        ])
    )


    story.append(
        performance_table
    )


    story.append(
        Spacer(1, 25)
    )


    story.append(
        Paragraph(
            "This result has been generated by the Online Examination System.",
            styles["Normal"]
        )
    )


    # -----------------------------------------------------
    # BUILD PDF
    # -----------------------------------------------------

    doc.build(story)


    print("====================================")
    print("RESULT PDF GENERATED")
    print("PATH:", pdf_path)
    print("EXISTS:", os.path.isfile(pdf_path))
    print("====================================")


    return pdf_path
# ==========================
# STUDENT RANKING
# ==========================
@app.route('/student_rank')
def student_rank():

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            u.username,
            s.subject_name,
            r.score
        FROM results r
        INNER JOIN users u
            ON r.user_id = u.id
        INNER JOIN subjects s
            ON r.subject_id = s.id
        ORDER BY r.score DESC
    """)

    rankings = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "student_rank.html",
        rankings=rankings
    )

# ==========================
# TOP 10 LEADERBOARD
# ==========================
@app.route('/leaderboard')
def leaderboard():

    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                u.username,
                MAX(r.score) AS best_score
            FROM users u
            INNER JOIN results r
                ON u.id = r.user_id
            GROUP BY u.id, u.username
            ORDER BY best_score DESC
            LIMIT 10
        """)

        leaderboard = cursor.fetchall()

    except Exception as e:

        print("Leaderboard Error:", e)
        leaderboard = []

    finally:

        cursor.close()
        conn.close()

    return render_template(
        "leaderboard.html",
        leaderboard=leaderboard
    )
def generate_certificate(
        student_name,
        subject_name,
        band_score,
        exam_date
):
    folder = "generated_certificates"
    os.makedirs(folder, exist_ok=True)

    certificate_path = os.path.join(
        folder,
        f"{student_name}_Certificate.pdf"
    )

    certificate_id = "CERT-" + str(random.randint(100000, 999999))
    page_width, page_height = 842, 595
    pdf = pdf_canvas.Canvas(
        certificate_path,
        pagesize=(page_width, page_height)
    )

    pdf.setStrokeColor(HexColor("#D4AF37"))
    pdf.setLineWidth(6)
    pdf.rect(25, 25, page_width - 50, page_height - 50)
    pdf.setStrokeColor(HexColor("#F2D675"))
    pdf.setLineWidth(1)
    pdf.rect(34, 34, page_width - 68, page_height - 68)

    pdf.setFillColor(HexColor("#0D47A1"))
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(page_width / 2, 510, "CERTIFICATE OF ACHIEVEMENT")

    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 17)
    pdf.drawCentredString(
        page_width / 2,
        465,
        "This Certificate is Proudly Presented To"
    )

    safe_student_name = escape(str(student_name))
    safe_subject_name = escape(str(subject_name))
    name_font_size = 34
    while (
        name_font_size > 18
        and pdf.stringWidth(str(student_name), "Helvetica-Bold", name_font_size) > 730
    ):
        name_font_size -= 1
    pdf.setFillColor(HexColor("#1B5E20"))
    pdf.setFont("Helvetica-Bold", name_font_size)
    pdf.drawCentredString(page_width / 2, 418, str(student_name))

    description_style = getSampleStyleSheet()["BodyText"]
    description_style.alignment = TA_CENTER
    description_style.fontSize = 16
    description_style.leading = 22
    description = Paragraph(
        "This certificate is awarded to <b>{}</b> for successfully "
        "completing the <b>{}</b> examination with outstanding "
        "performance and dedication.".format(
            safe_student_name,
            safe_subject_name
        ),
        description_style
    )
    description_width, description_height = description.wrap(720, 58)
    description.drawOn(
        pdf,
        (page_width - description_width) / 2,
        365 - description_height
    )

    pdf.setFillColor(HexColor("#1565C0"))
    pdf.roundRect(291, 285, 260, 44, 8, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 19)
    pdf.drawCentredString(
        page_width / 2,
        300,
        f"Band Score: {band_score}"
    )

    pdf.setFillColor(HexColor("#FFD700"))
    pdf.setStrokeColor(HexColor("#B8860B"))
    pdf.setLineWidth(2)
    pdf.circle(page_width / 2, 215, 34, fill=1, stroke=1)
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawCentredString(page_width / 2, 220, "TOP")
    pdf.setFont("Helvetica-Bold", 7)
    pdf.drawCentredString(page_width / 2, 205, "PERFORMER")

    info_y = 130
    pdf.setFillColor(HexColor("#E3F2FD"))
    pdf.setStrokeColor(HexColor("#90A4AE"))
    pdf.roundRect(91, info_y, 660, 42, 4, fill=1, stroke=1)
    info = (
        ("CERTIFICATE ID", certificate_id),
        ("ISSUE DATE", str(exam_date)),
        ("SUBJECT", str(subject_name))
    )
    for index, (label, value) in enumerate(info):
        center_x = 201 + index * 220
        pdf.setFillColor(HexColor("#455A64"))
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawCentredString(center_x, info_y + 27, label)
        pdf.setFillColor(colors.black)
        pdf.setFont("Helvetica", 10)
        display_value = value
        while (
            len(display_value) > 26
            and pdf.stringWidth(display_value, "Helvetica", 10) > 200
        ):
            display_value = display_value[:-1]
        if display_value != value:
            display_value = display_value.rstrip() + "..."
        pdf.drawCentredString(center_x, info_y + 11, display_value)

    pdf.setFillColor(HexColor("#0D47A1"))
    pdf.roundRect(41, 48, page_width - 82, 44, 4, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawCentredString(
        page_width / 2,
        73,
        "ONLINE EXAMINATION SYSTEM"
    )
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(
        page_width / 2,
        59,
        "This certificate is digitally generated and does not require a physical signature."
    )

    pdf.save()

    return certificate_path

@app.route('/download_result_pdf/<int:attempt_id>')
def download_result_pdf(attempt_id):

    # -----------------------------------------------------
    # CHECK LOGIN
    # -----------------------------------------------------

    if 'student_id' not in session:

        flash("Please login first.", "warning")

        return redirect(url_for('login_page'))


    student_id = session['student_id']

    conn = None
    cursor = None

    try:

        # -------------------------------------------------
        # DATABASE CONNECTION
        # -------------------------------------------------

        conn = get_connection()

        cursor = conn.cursor(dictionary=True)


        # -------------------------------------------------
        # GET EXAM ATTEMPT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                se.attempt_id,
                se.student_id,
                se.submitted_at AS exam_date,
                se.score,
                se.total_questions,
                se.attempted_questions,
                se.correct_answers,
                se.wrong_answers,

                s.subject_name,

                u.fullname

            FROM student_exam se

            INNER JOIN exams e
                ON se.exam_id = e.exam_id

            INNER JOIN subjects s
                ON e.subject_id = s.id

            INNER JOIN users u
                ON se.student_id = u.id

            WHERE se.attempt_id = %s
              AND se.student_id = %s
              AND se.status = 'Completed'

            LIMIT 1
        """, (attempt_id, student_id))


        result = cursor.fetchone()


        # -------------------------------------------------
        # CHECK RESULT
        # -------------------------------------------------

        if not result:

            flash(
                "Result not found for this examination.",
                "danger"
            )

            return redirect(url_for('dashboard'))


        # -------------------------------------------------
        # CALCULATE VALUES
        # -------------------------------------------------

        total_questions = int(
            result['total_questions'] or 0
        )

        attempted_questions = int(
            result['attempted_questions'] or 0
        )

        correct = int(
            result['correct_answers'] or 0
        )

        wrong = int(
            result['wrong_answers'] or 0
        )


        unanswered = max(
            total_questions - attempted_questions,
            0
        )


        score = float(
            result['score'] or 0
        )


        # -------------------------------------------------
        # PERCENTAGE
        # -------------------------------------------------

        if total_questions > 0:

            percentage = round(
                (score / total_questions) * 100,
                2
            )

        else:

            percentage = 0


        # -------------------------------------------------
        # BAND SCORE
        # -------------------------------------------------

        band_score = round(
            (score / total_questions) * 9,
            1
        ) if total_questions > 0 else 0


        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        status = (
            "PASS"
            if percentage >= 40
            else "FAIL"
        )


        # -------------------------------------------------
        # EXAM DATE
        # -------------------------------------------------

        exam_date = result['exam_date']


        # -------------------------------------------------
        # GENERATE PDF
        # -------------------------------------------------

        pdf_path = generate_result_pdf(

            student_name=result['fullname'],

            subject_name=result['subject_name'],

            total_questions=total_questions,

            attempted_questions=attempted_questions,

            correct=correct,

            wrong=wrong,

            unanswered=unanswered,

            score=score,

            band_score=band_score,

            status=status,

            exam_date=exam_date
        )


        # -------------------------------------------------
        # CHECK FILE
        # -------------------------------------------------

        if not pdf_path or not os.path.isfile(pdf_path):

            print("RESULT PDF ERROR")
            print("PDF PATH:", pdf_path)

            flash(
                "Result PDF could not be generated.",
                "danger"
            )

            return redirect(url_for('dashboard'))


        # -------------------------------------------------
        # DOWNLOAD PDF
        # -------------------------------------------------

        filename = os.path.basename(pdf_path)


        return send_file(

            pdf_path,

            as_attachment=True,

            download_name=filename,

            mimetype='application/pdf'
        )


    except Exception as e:

        print("====================================")
        print("DOWNLOAD RESULT PDF ERROR:", e)
        print("====================================")

        flash(
            "Unable to generate result PDF.",
            "danger"
        )

        return redirect(url_for('dashboard'))


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()

@app.route('/download_certificate/<int:attempt_id>')
def download_certificate(attempt_id):

    # -----------------------------------------------------
    # CHECK LOGIN
    # -----------------------------------------------------

    if 'student_id' not in session:

        flash("Please login first.", "warning")

        return redirect(url_for('login_page'))


    student_id = session['student_id']

    conn = None
    cursor = None

    try:

        # -------------------------------------------------
        # DATABASE CONNECTION
        # -------------------------------------------------

        conn = get_connection()

        cursor = conn.cursor(dictionary=True)


        # -------------------------------------------------
        # GET ATTEMPT INFORMATION
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                se.attempt_id,
                se.student_id,
                se.score,
                se.total_questions,
                se.submitted_at AS exam_date,

                s.subject_name,

                u.fullname

            FROM student_exam se

            INNER JOIN exams e
                ON se.exam_id = e.exam_id

            INNER JOIN subjects s
                ON e.subject_id = s.id

            INNER JOIN users u
                ON se.student_id = u.id

            WHERE se.attempt_id = %s
              AND se.student_id = %s
              AND se.status = 'Completed'

            LIMIT 1
        """, (attempt_id, student_id))


        result = cursor.fetchone()


        # -------------------------------------------------
        # CHECK ATTEMPT
        # -------------------------------------------------

        if not result:

            flash(
                "Examination attempt not found.",
                "danger"
            )

            return redirect(url_for('dashboard'))


        # -------------------------------------------------
        # CALCULATE BAND SCORE
        # -------------------------------------------------

        total_questions = int(
            result['total_questions'] or 0
        )

        score = float(
            result['score'] or 0
        )


        if total_questions > 0:

            band_score = round(
                (score / total_questions) * 9,
                1
            )

        else:

            band_score = 0


        # -------------------------------------------------
        # CERTIFICATE CONDITION
        # -------------------------------------------------

        if band_score <= 6:

            flash(
                "Certificate is available only when Band Score is greater than 6.",
                "warning"
            )

            return redirect(url_for('dashboard'))


        # -------------------------------------------------
        # GENERATE CERTIFICATE
        # -------------------------------------------------

        certificate_path = generate_certificate(

            student_name=result['fullname'],

            subject_name=result['subject_name'],

            band_score=band_score,

            exam_date=result['exam_date']

        )


        # -------------------------------------------------
        # CHECK FILE
        # -------------------------------------------------

        if not certificate_path or not os.path.isfile(
            certificate_path
        ):

            print("====================================")
            print("CERTIFICATE FILE ERROR")
            print("PATH:", certificate_path)
            print("EXISTS:", os.path.isfile(certificate_path))
            print("====================================")

            flash(
                "Certificate could not be generated.",
                "danger"
            )

            return redirect(url_for('dashboard'))


        # -------------------------------------------------
        # DOWNLOAD CERTIFICATE
        # -------------------------------------------------

        filename = os.path.basename(
            certificate_path
        )


        return send_file(

            certificate_path,

            as_attachment=True,

            download_name=filename,

            mimetype='application/pdf'

        )


    except Exception as e:

        print("====================================")
        print("DOWNLOAD CERTIFICATE ERROR:", e)
        print("====================================")

        flash(
            "Unable to generate certificate.",
            "danger"
        )

        return redirect(url_for('dashboard'))


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


EXCEL_UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
os.makedirs(EXCEL_UPLOAD_FOLDER, exist_ok=True)

import pandas as pd

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/upload_questions", methods=["GET", "POST"])
def upload_questions():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":

        file = request.files["excel"]

        if file.filename == "":
            flash("Please select an Excel file.", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)

        filepath = os.path.join(
            EXCEL_UPLOAD_FOLDER,
            filename
        )

        file.save(filepath)

        df = pd.read_excel(filepath)
        df = df.fillna("")

        conn = get_connection()
        cursor = conn.cursor()

        count = 0

        try:

            for _, row in df.iterrows():

                # Skip empty rows
                if pd.isna(row["question_text"]):
                    continue

                # Find subject_id using subject_name
                cursor.execute("""
                    SELECT id
                    FROM subjects
                    WHERE subject_name=%s
                """, (str(row["subject_name"]).strip(),))

                subject = cursor.fetchone()

                if not subject:
                    print(f"Subject not found: {row['subject_name']}")
                    continue

                subject_id = subject[0]

                cursor.execute("""
                    INSERT INTO questions
                    (
                        subject_id,
                        question_text,
                        option1,
                        option2,
                        option3,
                        option4,
                        correct_option
                        
                    )
                    VALUES
                    (
                        %s,%s,%s,%s,%s,%s,%s
                    )
                """,
                               (
                                   subject_id,
                                   str(row["question_text"]),
                                   str(row["option1"]),
                                   str(row["option2"]),
                                   str(row["option3"]),
                                   str(row["option4"]),
                                   int(row["correct_option"])
                               ))

                count += 1

            conn.commit()

            flash(f"{count} Questions Uploaded Successfully!", "success")

        except Exception as e:

            conn.rollback()

            flash(str(e), "danger")

        finally:

            cursor.close()
            conn.close()

        return redirect(url_for("view_questions"))

    return render_template("upload_questions.html")


from flask import send_file
from openpyxl import Workbook
import tempfile

@app.route("/download_question_template")
def download_question_template():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            s.subject_name,
            q.question_text,
            q.option1,
            q.option2,
            q.option3,
            q.option4,
            q.correct_option
            
        FROM questions q
        JOIN subjects s
        ON q.subject_id = s.id
        ORDER BY s.subject_name, q.id
    """)

    questions = cursor.fetchall()

    cursor.close()
    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Questions"

    # Header
    ws.append([
        "subject_name",
        "question_text",
        "option1",
        "option2",
        "option3",
        "option4",
        "correct_option"

    ])

    # Existing records
    for q in questions:

        ws.append([
            q["subject_name"],
            q["question_text"],
            q["option1"],
            q["option2"],
            q["option3"],
            q["option4"],
            q["correct_option"]

        ])

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(temp.name)
    temp.close()

    return send_file(
        temp.name,
        as_attachment=True,
        download_name="questions.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==========================================
# Export Excel
# ==========================================
@app.route('/export_excel')
def export_excel():
    return "Export Excel"

# ==========================================
# Export CSV
# ==========================================
@app.route('/export_csv')
def export_csv():
    return "Export CSV"

# ==========================================
# Export PDF
# ==========================================
@app.route('/export_pdf')
def export_pdf():
    return "Export PDF"


def send_result_email(
    student_email,
    student_name,
    subject_name,
    score,
    band_score,
    status,
    pdf_file,
    certificate_file=None
):
    print("=" * 50)
    print("EMAIL FUNCTION STARTED")
    print("Student Email :", student_email)
    print("PDF File :", pdf_file)

    attachments = []
    if pdf_file and os.path.exists(str(pdf_file)):
        attachments.append({
            "path": pdf_file,
            "name": "Result.pdf",
            "mime": "application/pdf"
        })

    if certificate_file and os.path.exists(certificate_file):
        attachments.append({
            "path": certificate_file,
            "name": "Certificate.pdf",
            "mime": "application/pdf"
        })

    body = f"""Hello {student_name},

Your examination has been completed successfully.

Subject    : {subject_name}
Score      : {score}
Band Score : {band_score}
Status     : {status}

The result PDF is attached with this email.

Thank you.
Online Examination System
"""

    send_email(
        subject=f"Exam Result: {subject_name}",
        recipients=[student_email],
        body=body,
        attachments=attachments
    )

    send_email(
        subject=f"Student Result: {student_name} - {subject_name}",
        recipients=[ADMIN_NOTIFY_EMAIL],
        body=f"""Hello Admin,

A student has completed an examination.

Student    : {student_name}
Email      : {student_email}
Subject    : {subject_name}
Score      : {score}
Band Score : {band_score}
Status     : {status}

Online Examination System
""",
        attachments=attachments
    )

    print("EMAIL FUNCTION COMPLETED")
    print("=" * 50)


# ==========================================
# Run Application
# ==========================================
if __name__ == '__main__':
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
