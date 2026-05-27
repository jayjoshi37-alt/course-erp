from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from flask import send_file

from dotenv import load_dotenv

import os
import uuid
import qrcode

from datetime import datetime

from reportlab.lib.colors import HexColor, black, grey
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

# =========================
# LOAD ENV FILE
# =========================
load_dotenv()

app = Flask(__name__)

# =========================
# SECRET KEY
# =========================
app.secret_key = os.getenv("SECRET_KEY")

# =========================
# MYSQL CONFIG
# =========================
app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST")
app.config['MYSQL_PORT'] = int(os.getenv("MYSQL_PORT"))
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")

mysql = MySQL(app)

# =========================
# MAIL CONFIG
# =========================
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT"))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS") == "True"

app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")

mail = Mail(app)

# =========================
# FILE UPLOAD CONFIG
# =========================
app.config['UPLOAD_FOLDER'] = os.getenv("UPLOAD_FOLDER")
app.config['VIDEO_UPLOAD_FOLDER'] = os.getenv("VIDEO_UPLOAD_FOLDER")

# =========================
# ALLOWED FILES
# =========================
ALLOWED_VIDEO_EXTENSIONS = {'mp4'}
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_video(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS
    )

def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# =========================
# TEMP DATA
# =========================
courses = []

# =========================
# ADMIN LOGIN
# =========================
admins = {
    "admin": "super",
}

@app.route('/')
def index():
    return render_template('index.html')


# ---------- ADMIN ----------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in admins and admins[username] == password:
            session['admin'] = username
        return redirect(url_for('admin_dashboard'))
        flash("Invalid Credentials", "danger")
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()

    # Total Users
    cur.execute("SELECT COUNT(*) FROM registration")
    total_users = cur.fetchone()[0]

    # Total Courses
    cur.execute("SELECT COUNT(*) FROM courses")
    total_courses = cur.fetchone()[0]

    # Revenue (temporary / optional)
    total_revenue = 0

    cur.close()

    return render_template('admin/dashboard.html', total_users=total_users, total_courses=total_courses,
                           total_revenue=total_revenue)

@app.route('/admin/reviews')
def admin_reviews():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT cr.id, c.title, r.name, cr.rating, cr.review
        FROM course_reviews cr
        JOIN courses c ON cr.course_id=c.id
        JOIN registration r ON cr.user_id=r.id
        ORDER BY cr.created_at DESC
    """)
    reviews = cur.fetchall()
    cur.close()

    return render_template('admin/reviews.html', reviews=reviews)

@app.route('/admin/delete_review/<int:review_id>')
def delete_review(review_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM course_reviews WHERE id=%s", (review_id,))
    mysql.connection.commit()
    cur.close()

    flash("Review deleted successfully ❌", "danger")
    return redirect(url_for('admin_reviews'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/history')
def history():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, username FROM registration")
    users = cur.fetchall()
    cur.close()

    return render_template("admin/history.html", users=users)

# ---------- USER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM registration WHERE email=%s OR username=%s", (email, username))
        if cur.fetchone():
            flash("User already exists", "danger")
            return redirect(url_for('register'))

        cur.execute("INSERT INTO registration(name,email,username,password) VALUES(%s,%s,%s,%s)",
                    (name, email, username, password))
        mysql.connection.commit()
        cur.close()
        flash("Registration Successful", "success")
        return redirect(url_for('login'))

    return render_template('user_register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM registration WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['user'] = username
            return redirect(url_for('user_dashboard'))
        flash("Invalid Credentials", "danger")

    return render_template('user_login.html')

@app.route('/user/dashboard')
def user_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, description, price, image FROM courses")
    courses = cur.fetchall()
    cur.close()

    return render_template('user/dashboard.html', user=session['user'], courses=courses)

# -----------Forget Password-------------#
@app.route('/user/forgot-password', methods=['GET', 'POST'])
def user_forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        cur = mysql.connection.cursor()
        cur.execute("SELECT name, password FROM registration WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            name, password = user

            msg = Message(
                subject="Your Account Password",
                recipients=[email]
            )
            msg.body = f"""Hello {name},

Your user login password is: {password}

Please keep it secure.

Regards,
User Portal
"""
            mail.send(msg)

            flash("Password sent to your email successfully!", "success")
            return redirect(url_for('login'))
        else:
            flash("Email not registered!", "danger")

    return render_template('user/forgot_password.html')

# -------- USER CHANGE PASSWORD -------- #
@app.route('/user/change-password', methods=['GET', 'POST'])
def user_change_password():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash("New passwords do not match!", "danger")
            return redirect(request.url)

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT password FROM registration WHERE username=%s",
            (session['user'],)
        )
        user = cur.fetchone()

        if user and user[0] == old_password:
            cur.execute(
                "UPDATE registration SET password=%s WHERE username=%s",
                (new_password, session['user'])
            )
            mysql.connection.commit()
            flash("Password changed successfully!", "success")
        else:
            flash("Old password is incorrect!", "danger")

        cur.close()
        return redirect(request.url)

    return render_template('user/change_password.html')

# ===================== CERTIFICATE LOGIC =====================
@app.route('/video/complete/<int:video_id>', methods=['POST'])
def complete_video(video_id):
    if 'user' not in session:
        return jsonify({'status': 'unauthorized'}), 401

    cur = mysql.connection.cursor()
    # Get user id
    cur.execute("SELECT id FROM registration WHERE username=%s", (session['user'],))
    user_id = cur.fetchone()[0]

    # Get course id
    cur.execute("SELECT course_id FROM course_videos WHERE id=%s", (video_id,))
    course_id = cur.fetchone()[0]

    # Mark video complete
    cur.execute("""
        INSERT INTO video_progress (user_id, course_id, video_id, completed, completed_at)
        VALUES (%s,%s,%s,1,NOW())
        ON DUPLICATE KEY UPDATE completed=1, completed_at=NOW()
    """, (user_id, course_id, video_id))
    mysql.connection.commit()

    # Check course completion
    if is_course_completed(user_id, course_id):
        generate_certificate(user_id, course_id)

    cur.close()
    return jsonify({'status': 'success'})

# ----------------- Certificates -----------------
def is_course_completed(user_id, course_id):
    cur=mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM course_videos WHERE course_id=%s",(course_id,))
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM video_progress WHERE user_id=%s AND course_id=%s AND completed=1",(user_id,course_id))
    completed = cur.fetchone()[0]
    cur.execute("""SELECT qa.passed FROM quiz_attempts qa JOIN quizzes q ON qa.quiz_id=q.id WHERE qa.user_id=%s AND q.course_id=%s""",(user_id,course_id))
    quiz = cur.fetchone(); cur.close()
    return total>0 and total==completed and quiz and quiz[0]==1

def update_course_progress(user_id, course_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM course_videos WHERE course_id=%s",(course_id,))
    total_videos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM video_progress WHERE user_id=%s AND course_id=%s AND completed=1",(user_id,course_id))
    completed_videos = cur.fetchone()[0]
    progress_percent = int((completed_videos/total_videos)*100) if total_videos else 0
    completed = 1 if progress_percent==100 else 0
    cur.execute("""INSERT INTO user_course_progress(user_id,course_id,completed_videos,total_videos,progress_percent,completed)
                VALUES(%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE completed_videos=%s,total_videos=%s,progress_percent=%s,completed=%s""",
                (user_id,course_id,completed_videos,total_videos,progress_percent,completed,completed_videos,total_videos,progress_percent,completed))
    mysql.connection.commit(); cur.close()

def generate_certificate(user_id, course_id):
    cur=mysql.connection.cursor()
    cur.execute("SELECT certificate_no,issued_at FROM certificates WHERE user_id=%s AND course_id=%s",(user_id,course_id))
    existing = cur.fetchone()
    cur.execute("""SELECT r.name, c.title, c.instructor_name FROM registration r JOIN courses c ON c.id=%s WHERE r.id=%s""",(course_id,user_id))
    row = cur.fetchone()
    if not row: cur.close(); return
    user_name, course_title, instructor_name = row
    if existing:
        certificate_no, issued_at = existing
    else:
        certificate_no = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        cur.execute("INSERT INTO certificates(user_id,course_id,certificate_no,issued_at) VALUES(%s,%s,%s,NOW())",(user_id,course_id,certificate_no))
        mysql.connection.commit()
        cur.execute("SELECT issued_at FROM certificates WHERE certificate_no=%s",(certificate_no,))
        issued_at = cur.fetchone()[0]
    cur.close()
    pdf_path = f"certificates/{certificate_no}.pdf"
    os.makedirs("certificates", exist_ok=True)
    if not os.path.exists(pdf_path):
        generate_certificate_pdf(pdf_path, certificate_no, user_name, course_title, instructor_name, issued_at)

from weasyprint import HTML
from flask import render_template
import os

def generate_certificate_pdf(pdf_path, certificate_no, user_name, course_title, instructor_name, issued_at):
    issued_date = issued_at.strftime("%d %B %Y")

    html = render_template(
        "user/certificate_template.html",
        user_name=user_name,
        course_title=course_title,
        instructor_name=instructor_name,
        certificate_no=certificate_no,
        issued_date=issued_date,
        signature_path=os.path.abspath("static/images/signature.png")
    )

    HTML(
        string=html,
        base_url=os.getcwd()
    ).write_pdf(pdf_path)

@app.route('/user/my_certificates')
def my_certificates():
    if 'user' not in session: return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("""SELECT c.title, cert.certificate_no, DATE_FORMAT(cert.issued_at,'%%d %%b %%Y')
                   FROM certificates cert JOIN courses c ON cert.course_id=c.id
                   WHERE cert.user_id=(SELECT id FROM registration WHERE username=%s)""",(session['user'],))
    certificates = cur.fetchall(); cur.close()
    return render_template('user/my_certificates.html', certificates=certificates)

@app.route('/certificate/download/<certificate_no>')
def download_certificate(certificate_no):
    if 'user' not in session: return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("""SELECT r.name, c.title FROM certificates cert
                   JOIN registration r ON cert.user_id=r.id
                   JOIN courses c ON cert.course_id=c.id
                   WHERE cert.certificate_no=%s AND r.username=%s""",(certificate_no,session['user']))
    row = cur.fetchone(); cur.close()
    if not row: flash("Unauthorized access", "danger"); return redirect(url_for('my_certificates'))
    user_name, course_title = row
    os.makedirs("certificates", exist_ok=True); pdf_path=f"certificates/{certificate_no}.pdf"
    if not os.path.exists(pdf_path):
        generate_certificate_pdf(pdf_path, certificate_no, user_name, course_title, "Instructor Name", datetime.now())
    return send_file(pdf_path, as_attachment=True, download_name=f"{course_title}_Certificate.pdf")

# ---------------- CREATE RESUME ----------------
@app.route('/user/resume/input', methods=['GET', 'POST'])
def resume_input():
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM registration WHERE username=%s", (session['user'],))
    user_id = cur.fetchone()[0]

    if request.method == 'POST':

        # ---------- PHOTO ----------
        photo_name = None
        photo = request.files.get('photo')
        if photo and photo.filename and allowed_file(photo.filename):
            photo_name = secure_filename(photo.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_name))

        # ---------- FILTER CERTIFICATES ----------
        certificates = ", ".join([
            f"{n} ({i})"
            for n, i in zip(
                request.form.getlist('certificate_name[]'),
                request.form.getlist('certificate_institute[]')
            ) if n.strip() and i.strip()
        ])

        # ---------- FILTER PROJECTS ----------
        projects = ", ".join([
            f"{t} - {d}"
            for t, d in zip(
                request.form.getlist('project_title[]'),
                request.form.getlist('project_desc[]')
            ) if t.strip() and d.strip()
        ])

        # ---------- FILTER EXPERIENCES ----------
        experiences = ", ".join([
            f"{t} - {d}"
            for t, d in zip(
                request.form.getlist('experience_title[]'),
                request.form.getlist('experience_desc[]')
            ) if t.strip() and d.strip()
        ])

        # ---------- INSERT ----------
        cur.execute("""
            INSERT INTO resume_data (
                user_id, name, mobile, email, address, photo,
                summary, skills,
                education_10, education_12, education_degree, education_pg,
                certificates, projects, experiences,
                linkedin, github, template_id
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1)
        """, (
            user_id,
            request.form['name'],
            request.form['mobile'],
            request.form['email'],
            request.form['address'],
            photo_name,
            request.form['summary'],
            request.form['skills'],
            request.form['education_10'],
            request.form['education_12'],
            request.form['education_degree'],
            request.form.get('education_pg'),  # ✅ PG added
            certificates,
            projects,
            experiences,
            request.form['linkedin'],
            request.form['github']
        ))

        mysql.connection.commit()
        cur.close()

        flash("Resume Created Successfully", "success")
        return redirect(url_for('edit_resume'))

    return render_template('user/resume_input.html')

@app.route('/user/resume/edit', methods=['GET', 'POST'])
def edit_resume():
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM registration WHERE username=%s", (session['user'],))
    user_id = cur.fetchone()[0]

    cur.execute("SELECT * FROM resume_data WHERE user_id=%s", (user_id,))
    resume = cur.fetchone()

    if not resume:
        flash("No resume found. Please create one first.", "warning")
        return redirect(url_for('resume_input'))

    columns = [desc[0] for desc in cur.description]
    resume_data = dict(zip(columns, resume))

    if request.method == 'POST':

        photo_name = resume_data['photo']
        photo = request.files.get('photo')
        if photo and photo.filename and allowed_file(photo.filename):
            photo_name = secure_filename(photo.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_name))

        certificates = ", ".join([
            f"{n} ({i})"
            for n, i in zip(
                request.form.getlist('certificate_name[]'),
                request.form.getlist('certificate_institute[]')
            ) if n.strip() and i.strip()
        ])

        projects = ", ".join([
            f"{t} - {d}"
            for t, d in zip(
                request.form.getlist('project_title[]'),
                request.form.getlist('project_desc[]')
            ) if t.strip() and d.strip()
        ])

        experiences = ", ".join([
            f"{t} - {d}"
            for t, d in zip(
                request.form.getlist('experience_title[]'),
                request.form.getlist('experience_desc[]')
            ) if t.strip() and d.strip()
        ])

        cur.execute("""
            UPDATE resume_data SET
                name=%s, mobile=%s, email=%s, address=%s, photo=%s,
                summary=%s, skills=%s,
                education_10=%s, education_12=%s,
                education_degree=%s, education_pg=%s,
                certificates=%s, projects=%s, experiences=%s,
                linkedin=%s, github=%s
            WHERE user_id=%s
        """, (
            request.form['name'],
            request.form['mobile'],
            request.form['email'],
            request.form['address'],
            photo_name,
            request.form['summary'],
            request.form['skills'],
            request.form['education_10'],
            request.form['education_12'],
            request.form['education_degree'],
            request.form.get('education_pg'),  # ✅ PG
            certificates,
            projects,
            experiences,
            request.form['linkedin'],
            request.form['github'],
            user_id
        ))

        mysql.connection.commit()
        cur.close()

        flash("Resume Updated Successfully", "success")
        return redirect(url_for('edit_resume'))

    cur.close()
    return render_template('user/edit_resume.html', resume=resume_data)

@app.route('/user/resume/template', methods=['GET', 'POST'])
def select_template():
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    # Get user id
    cur.execute("SELECT id FROM registration WHERE username=%s", (session['user'],))
    user_id = cur.fetchone()[0]

    # Fetch existing resume data
    cur.execute("SELECT * FROM resume_data WHERE user_id=%s", (user_id,))
    resume = cur.fetchone()

    if not resume:
        flash("Please create your resume first.", "warning")
        return redirect(url_for('resume_input'))

    if request.method == 'POST':
        selected_template = request.form['template_id']

        # Update template choice in database
        cur.execute("""
            UPDATE resume_data
            SET template_id=%s
            WHERE user_id=%s
        """, (selected_template, user_id))
        mysql.connection.commit()
        cur.close()

        flash("Template selected successfully!", "success")
        return redirect(url_for('generate_resume'))

    cur.close()
    return render_template('user/select_template.html', resume=resume)

# ---------------- GENERATE RESUME ----------------
@app.route('/user/resume/generate')
def generate_resume():
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM registration WHERE username=%s", (session['user'],))
    user_id = cur.fetchone()[0]

    cur.execute("""
        SELECT
            name, mobile, email, address, photo,
            certificates,
            education_10, education_12, education_degree, education_pg,
            summary, skills, projects, experiences,
            linkedin, github, template_id
        FROM resume_data
        WHERE user_id=%s
    """, (user_id,))
    resume = cur.fetchone()
    cur.close()

    if not resume:
        return redirect(url_for('resume_input'))

    template_id = resume[-1]

    if template_id == 1:
        return render_template('user/resume_templates/template1.html', resume=resume)
    elif template_id == 2:
        return render_template('user/resume_templates/template2.html', resume=resume)
    elif template_id == 3:
        return render_template('user/resume_templates/template3.html', resume=resume)
    elif template_id == 4:
        return render_template('user/resume_templates/template4.html', resume=resume)
    else:
        return render_template('user/resume_templates/template1.html', resume=resume)

# ----------------------------#
@app.route('/course/<int:course_id>')
def course_detail(course_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    # Course info
    cur.execute("SELECT * FROM courses WHERE id=%s", (course_id,))
    course = cur.fetchone()

    # Check enrollment
    cur.execute(""" SELECT * FROM enrollments
        WHERE user_id=(SELECT id FROM registration WHERE username=%s) AND course_id=%s
    """, (session['user'], course_id))
    enrolled = cur.fetchone()

    # Fetch videos (only number + title)
    cur.execute(""" SELECT video_number, title FROM course_videos
        WHERE course_id=%s ORDER BY video_number ASC
    """, (course_id,))
    videos = cur.fetchall()

    cur.execute("""
            SELECT r.name, cr.rating, cr.review, cr.created_at
            FROM course_reviews cr
            JOIN registration r ON cr.user_id = r.id
            WHERE cr.course_id = %s
            ORDER BY cr.created_at DESC
        """, (course_id,))
    reviews = cur.fetchall()

    cur.close()

    return render_template('user/course_detail.html', course=course, enrolled=enrolled, videos=videos, reviews=reviews)

@app.route('/course/<int:course_id>/review', methods=['GET', 'POST'])
def add_review(course_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    # Get user id
    cur.execute("SELECT id FROM registration WHERE username=%s", (session['user'],))
    user_id = cur.fetchone()[0]

    # Prevent duplicate review
    cur.execute("""
        SELECT id FROM course_reviews
        WHERE course_id=%s AND user_id=%s
    """, (course_id, user_id))

    if cur.fetchone():
        flash("You already reviewed this course", "warning")
        return redirect(url_for('course_detail', course_id=course_id))

    if request.method == 'POST':
        rating = request.form['rating']
        review = request.form['review']

        cur.execute("""
            INSERT INTO course_reviews (course_id, user_id, rating, review)
            VALUES (%s,%s,%s,%s)
        """, (course_id, user_id, rating, review))

        mysql.connection.commit()
        cur.close()

        flash("Review submitted successfully ⭐", "success")
        return redirect(url_for('course_detail', course_id=course_id))

    cur.close()
    return render_template('user/add_review.html', course_id=course_id)

# COURSE VIDEOS PAGE
@app.route('/course/<int:course_id>/videos')
def course_videos(course_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    # Get logged-in user ID
    cur.execute("SELECT id FROM registration WHERE username=%s", (session['user'],))
    user_id = cur.fetchone()[0]

    # Get videos with completion status
    cur.execute("""
        SELECT 
            v.id,
            v.video_number,
            v.title,
            v.description,
            IF(vp.completed = 1, 'Completed', 'Pending') AS status
        FROM course_videos v
        LEFT JOIN video_progress vp
            ON v.id = vp.video_id AND vp.user_id = %s
        WHERE v.course_id = %s
        ORDER BY v.video_number
    """, (user_id, course_id))

    videos = cur.fetchall()

    # Calculate progress
    cur.execute("""
        SELECT 
            ROUND(
                (COUNT(vp.video_id) / COUNT(v.id)) * 100
            )
        FROM course_videos v
        LEFT JOIN video_progress vp
            ON v.id = vp.video_id
            AND vp.completed = 1
            AND vp.user_id = %s
        WHERE v.course_id = %s
    """, (user_id, course_id))

    progress = cur.fetchone()[0] or 0

    cur.close()

    return render_template(
        'user/course_videos.html',
        videos=videos,
        progress=progress,
        course_id=course_id
    )

@app.route('/enroll/<int:course_id>')
def enroll_course(course_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    cur.execute(""" INSERT INTO enrollments (user_id, course_id)VALUES (
            (SELECT id FROM registration WHERE username=%s),%s)
    """, (session['user'], course_id))

    mysql.connection.commit()
    cur.close()

    flash("Course enrolled successfully 🎉", "success")
    return redirect(url_for('course_detail', course_id=course_id))

@app.route('/dummy_payment/<int:course_id>', methods=['GET', 'POST'])
def dummy_payment(course_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, price FROM courses WHERE id=%s", (course_id,))
    course = cur.fetchone()

    if request.method == 'POST':
        # Enroll user
        cur.execute("""
            INSERT INTO enrollments (user_id, course_id)
            VALUES ((SELECT id FROM registration WHERE username=%s), %s)
        """, (session['user'], course_id))
        mysql.connection.commit()

        # 🔹 Create receipt data
        session['receipt'] = {
            "transaction_id": str(uuid.uuid4()).split('-')[0].upper(),
            "course_name": course[1],
            "amount": course[2],
            "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "course_id": course_id
        }

        cur.close()
        return redirect(url_for('payment_receipt'))

    cur.close()
    return render_template('user/dummy_payment.html', course=course)

@app.route('/payment_receipt')
def payment_receipt():
    if 'receipt' not in session:
        return redirect(url_for('user_dashboard'))

    receipt = session['receipt']
    return render_template('user/payment_receipt.html', receipt=receipt)

@app.route('/user/my_courses')
def my_registered_courses():
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT 
            c.id,
            c.title,
            c.image,
            COALESCE(p.progress_percent, 0) AS progress
        FROM courses c
        JOIN enrollments e 
            ON c.id = e.course_id
        LEFT JOIN user_course_progress p
            ON p.course_id = c.id
            AND p.user_id = (
                SELECT id FROM registration WHERE username=%s
            )
        WHERE e.user_id = (
            SELECT id FROM registration WHERE username=%s
        )
    """, (session['user'], session['user']))

    courses = cur.fetchall()
    cur.close()

    return render_template(
        'user/my_courses.html',
        courses=courses
    )

@app.route('/video/<int:video_id>', methods=['GET', 'POST'])
def play_video(video_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, title, description, video_filename, youtube_url, course_id
        FROM course_videos WHERE id=%s
    """, (video_id,))
    video = cur.fetchone()

    if not video:
        cur.close()
        flash("Video not found!", "danger")
        return redirect(url_for('user_dashboard'))

    if request.method == 'POST':
        cur.execute("SELECT id FROM registration WHERE username=%s", (session['user'],))
        user_id = cur.fetchone()[0]
        course_id = video[5]

        cur.execute("""
            INSERT INTO video_progress (user_id, course_id, video_id, completed, completed_at)
            VALUES (%s,%s,%s,1,NOW())
            ON DUPLICATE KEY UPDATE completed=1, completed_at=NOW()
        """, (user_id, course_id, video_id))
        mysql.connection.commit()

        # 🔥 UPDATE COURSE PROGRESS
        update_course_progress(user_id, course_id)

        # 🎓 CERTIFICATE
        if is_course_completed(user_id, course_id):
            generate_certificate(user_id, course_id)

        cur.close()
        flash("Video marked as completed ✅", "success")
        return redirect(url_for('course_videos', course_id=course_id))

    cur.close()
    return render_template('user/play_video.html', video=video)

# -------------------#
@app.route('/user/logout')
def user_logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ---------- INSTRUCTOR ----------
@app.route('/instructor_register', methods=['GET', 'POST'])
def instructor_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO instructors (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password))
        mysql.connection.commit()
        cur.close()

        flash("Instructor Registered Successfully", "success")
        return redirect(url_for('instructor_login'))

    return render_template('instructor_register.html')

@app.route('/instructor_login', methods=['GET', 'POST'])
def instructor_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM instructors WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['instructor'] = email
            return redirect(url_for('instructor_dashboard'))
        flash("Invalid Login", "danger")

    return render_template('instructor_login.html')

@app.route('/instructor/dashboard')
def instructor_dashboard():
    if 'instructor' not in session:
        return redirect(url_for('instructor_login'))

    cur = mysql.connection.cursor()

    # Total Courses (automatic)
    cur.execute("SELECT COUNT(*) FROM courses")
    total_courses = cur.fetchone()[0]

    # Temporary values (until you implement these features)
    total_students = 0
    total_earnings = 0
    avg_rating = 0

    cur.close()

    return render_template('instructor/dashboard.html', total_courses=total_courses,
                           total_students=total_students, total_earnings=total_earnings, avg_rating=avg_rating)

# --------Forget Password-------------#
@app.route('/instructor/forgot-password', methods=['GET', 'POST'])
def instructor_forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        cur = mysql.connection.cursor()
        cur.execute("SELECT name, password FROM instructors WHERE email=%s", (email,))
        row = cur.fetchone()
        cur.close()

        if row:
            name, password = row

            msg = Message()
            msg.subject = "Your Instructor Account Password"
            msg.recipients = [email]
            msg.body = f"""Hello {name},

Your instructor login password is: {password}

Regards,
Institute ERP System
"""

            mail.send(msg)

            flash("Password sent to your email successfully!", "success")
            return redirect(url_for('instructor_login'))
        else:
            flash("Email not found!", "danger")

    return render_template('instructor/forgot_password.html')

# -------- INSTRUCTOR CHANGE PASSWORD -------- #
@app.route('/instructor/change-password', methods=['GET', 'POST'])
def instructor_change_password():
    if 'instructor' not in session:
        return redirect(url_for('instructor_login'))

    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(request.url)

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT password FROM instructors WHERE email=%s",
            (session['instructor'],)
        )
        instructor = cur.fetchone()

        if instructor and instructor[0] == old_password:
            cur.execute(
                "UPDATE instructors SET password=%s WHERE email=%s",
                (new_password, session['instructor'])
            )
            mysql.connection.commit()
            flash("Password updated successfully!", "success")
        else:
            flash("Old password incorrect!", "danger")

        cur.close()
        return redirect(request.url)

    return render_template('instructor/change_password.html')

@app.route('/instructor/logout')
def instructor_logout():
    session.pop('instructor', None)
    return redirect(url_for('instructor_login'))

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO contact_details (name, email, phone, message) VALUES (%s, %s, %s, %s)",
            (name, email, phone, message), )
        mysql.connection.commit()
        cur.close()

        flash("Message Sent Successfully!", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")

@app.route("/pricing")
def pricing():
    return render_template("pricing.html")  # Pricing page route

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    item = request.form.to_dict()

    cart = session.get('cart', [])

    # check if item already exists
    for c in cart:
        if c['title'] == item['title']:
            c['qty'] += 1
            break
    else:
        item['qty'] = 1
        cart.append(item)

    session['cart'] = cart
    flash("Course added to cart successfully!", "success")
    return redirect(url_for('index'))

@app.route('/checkout')
def checkout():
    cart = session.get('cart', [])

    for item in cart:
        item['price'] = float(item['price'])
        item['qty'] = int(item['qty'])

    total = sum(item['price'] * item['qty'] for item in cart)

    session['cart'] = cart  # update session with numeric values
    return render_template('checkout.html', cart=cart, total=total)

@app.route('/remove/<int:index>')
def remove(index):
    cart = session.get('cart', [])
    cart.pop(index)
    session['cart'] = cart
    return redirect(url_for('checkout'))

@app.route('/update/<int:index>/<action>')
def update_qty(index, action):
    cart = session.get('cart', [])
    if action == 'plus':
        cart[index]['qty'] += 1
    elif action == 'minus' and cart[index]['qty'] > 1:
        cart[index]['qty'] -= 1
    session['cart'] = cart
    return redirect(url_for('checkout'))

# Instructor #
@app.route('/instructor')
def instructor():
    cur = mysql.connection.cursor()

    # Total courses
    cur.execute("SELECT COUNT(*) FROM courses")
    total = cur.fetchone()[0]

    # All courses
    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()

    cur.close()

    return render_template('instructor.html', total=total, courses=courses)

@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        image = request.files['image']

        filename = image.filename
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO courses (title, description, price, image) VALUES (%s, %s, %s, %s)",
                    (title, description, price, filename))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('instructor'))

    return render_template('add_course.html')

@app.route('/delete_course/<int:course_id>')
def delete_course(course_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM courses WHERE id=%s", (course_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('instructor'))

# Instructor Login #
@app.route('/instructor/create_course', methods=['GET', 'POST'])
def create_course():
    if 'instructor' not in session:
        return redirect(url_for('instructor_login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']

        image = request.files['image']
        image_name = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_name))

        cur = mysql.connection.cursor()

        # 🔹 Get instructor name
        cur.execute("SELECT name FROM instructors WHERE email=%s", (session['instructor'],))
        instructor_name = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO courses
            (title, description, price, image, instructor_name)
            VALUES (%s, %s, %s, %s, %s)
        """, (title, description, price, image_name, instructor_name))

        mysql.connection.commit()
        cur.close()

        flash("Course created successfully 🎉", "success")
        return redirect(url_for('my_courses'))

    return render_template('instructor/create_course.html')

@app.route('/instructor/my_courses')
def my_courses():
    if 'instructor' not in session:
        return redirect(url_for('instructor_login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()
    cur.close()

    return render_template('instructor/my_courses.html', courses=courses)

@app.route('/instructor/edit_course/<int:id>', methods=['GET', 'POST'])
def edit_course(id):
    if 'instructor' not in session:
        return redirect(url_for('instructor_login'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        image = request.files.get('image')

        # If a new image is uploaded
        if image and image.filename:
            if allowed_file(image.filename):
                if len(image.read()) > 2 * 1024 * 1024:  # 2MB limit
                    flash("File is too large! Max size is 2MB.", "error")
                    return redirect(request.url)
                image.seek(0)  # Reset file pointer after read

                image_name = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
                image.save(image_path)

                cur.execute("""
                    UPDATE courses 
                    SET title=%s, description=%s, price=%s, image=%s 
                    WHERE id=%s
                """, (title, description, price, image_name, id))
            else:
                flash("Invalid image type! Only PNG, JPG, JPEG, GIF allowed.", "error")
                return redirect(request.url)
        else:
            # No new image, keep old
            cur.execute("""
                UPDATE courses 
                SET title=%s, description=%s, price=%s 
                WHERE id=%s
            """, (title, description, price, id))

        mysql.connection.commit()
        cur.close()
        flash("Course updated successfully!", "success")
        return redirect(url_for('my_courses'))

    # GET request: fetch course
    cur.execute("SELECT * FROM courses WHERE id=%s", (id,))
    course = cur.fetchone()
    cur.close()

    return render_template('instructor/edit_course.html', course=course)

@app.route('/instructor/delete_course/<int:id>')
def instructor_delete_course(id):
    if 'instructor' not in session:
        return redirect(url_for('instructor_login'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM courses WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash("Course deleted successfully!", "danger")  # popup message

    return redirect(url_for('my_courses'))

# Upload video #
def get_youtube_id(url):
    if not url: return None
    if "youtu.be/" in url: return url.split("youtu.be/")[-1].split("?")[0]
    if "watch?v=" in url: return url.split("watch?v=")[-1].split("&")[0]
    if "shorts/" in url: return url.split("shorts/")[-1].split("?")[0]
    if "embed/" in url: return url.split("embed/")[-1].split("?")[0]
    return None

@app.route('/instructor/upload_video/<int:course_id>', methods=['GET', 'POST'])
def upload_video(course_id):
    if 'instructor' not in session:
        return redirect(url_for('instructor_login'))

    cur = mysql.connection.cursor()

    # Fetch course info
    cur.execute("SELECT title, image FROM courses WHERE id=%s", (course_id,))
    course = cur.fetchone()

    # Next video number
    cur.execute(
        "SELECT COALESCE(MAX(video_number),0) FROM course_videos WHERE course_id=%s",
        (course_id,)
    )
    next_video_number = cur.fetchone()[0] + 1

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        youtube_url = request.form.get('youtube_url')
        video = request.files.get('video')

        video_filename = None

        if video and video.filename:
            if not allowed_video(video.filename):
                flash("Only MP4 allowed", "danger")
                return redirect(request.url)

            video_filename = secure_filename(video.filename)
            os.makedirs(app.config['VIDEO_UPLOAD_FOLDER'], exist_ok=True)
            video.save(os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], video_filename))

        elif youtube_url:
            youtube_id = get_youtube_id(youtube_url)
            if not youtube_id:
                flash("Invalid YouTube URL", "danger")
                return redirect(request.url)
            youtube_url = f"https://www.youtube.com/embed/{youtube_id}"

        else:
            flash("Upload MP4 or YouTube link", "danger")
            return redirect(request.url)

        cur.execute("""
            INSERT INTO course_videos
            (course_id, video_number, title, description, video_filename, youtube_url)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (course_id, next_video_number, title, description, video_filename, youtube_url))

        mysql.connection.commit()
        flash("Video uploaded successfully 🎉", "success")
        return redirect(request.url)

    # Fetch all videos
    cur.execute("""
        SELECT id, video_number, title, description,
               video_filename, youtube_url, course_id
        FROM course_videos
        WHERE course_id=%s
        ORDER BY video_number
    """, (course_id,))
    videos = cur.fetchall()

    total_videos = len(videos)

    cur.close()

    return render_template('instructor/upload_video.html',
                           videos=videos, next_video_number=next_video_number,
                           course=course, total_videos=total_videos)

# ------------- EDIT VIDEO----------------#
@app.route('/instructor/edit_video/<int:video_id>', methods=['GET', 'POST'])
def edit_video(video_id):
    if 'instructor' not in session:
        return redirect(url_for('instructor_login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, course_id, title, description, video_filename, youtube_url FROM course_videos WHERE id=%s",
                (video_id,))
    video = cur.fetchone()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        youtube_url = request.form.get('youtube_url')

        # Update YouTube URL only if provided
        if youtube_url:
            youtube_id = get_youtube_id(youtube_url)
            if not youtube_id:
                flash("Invalid YouTube URL", "danger")
                return redirect(request.url)
            youtube_url = f"https://www.youtube.com/embed/{youtube_id}"

        cur.execute("UPDATE course_videos SET title=%s, description=%s, youtube_url=%s WHERE id=%s",
                    (title, description, youtube_url, video_id))
        mysql.connection.commit()
        cur.close()
        flash("Video updated successfully ✏️", "success")
        return redirect(url_for('upload_video', course_id=video[1]))

    cur.close()
    return render_template('instructor/edit_video.html', video=video)

# -------------- DELETE VIDEO---------------#
@app.route('/instructor/delete_video/<int:video_id>/<int:course_id>')
def delete_video(video_id, course_id):
    if 'instructor' not in session:
        return redirect(url_for('instructor_login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT video_filename FROM course_videos WHERE id=%s", (video_id,))
    file = cur.fetchone()
    if file and file[0]:
        file_path = os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], file[0])
        if os.path.exists(file_path): os.remove(file_path)

    cur.execute("DELETE FROM course_videos WHERE id=%s", (video_id,))
    mysql.connection.commit()
    cur.close()
    flash("Video deleted successfully ❌", "success")
    return redirect(url_for('upload_video', course_id=course_id))

# ==============================WISHLIST======================
@app.route('/wishlist/add/<int:course_id>')
def add_to_wishlist(course_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    cur.execute("SELECT id FROM registration WHERE username=%s", (session['user'],))
    user_id = cur.fetchone()[0]

    # prevent duplicates
    cur.execute(
        "SELECT id FROM wishlist WHERE user_id=%s AND course_id=%s",
        (user_id, course_id)
    )

    if not cur.fetchone():
        cur.execute(
            "INSERT INTO wishlist (user_id, course_id) VALUES (%s,%s)",
            (user_id, course_id)
        )
        mysql.connection.commit()
        flash("Course added to wishlist ❤️", "success")
    else:
        flash("Course already in wishlist ⚠️", "warning")

    cur.close()
    return redirect(url_for('course_detail', course_id=course_id))

@app.route('/wishlist/remove/<int:course_id>')
def remove_from_wishlist(course_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    cur.execute("SELECT id FROM registration WHERE username=%s", (session['user'],))
    user_id = cur.fetchone()[0]

    cur.execute(
        "DELETE FROM wishlist WHERE user_id=%s AND course_id=%s",
        (user_id, course_id)
    )
    mysql.connection.commit()
    cur.close()

    flash("Removed from wishlist ❌", "danger")
    return redirect(url_for('user_wishlist'))

@app.route('/user/wishlist')
def user_wishlist():
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT c.id, c.title, c.image, c.price
        FROM wishlist w
        JOIN courses c ON w.course_id = c.id
        WHERE w.user_id = (
            SELECT id FROM registration WHERE username=%s
        )
    """, (session['user'],))

    wishlist = cur.fetchall()
    cur.close()

    return render_template('user/wishlist.html', wishlist=wishlist)

# ====================QUIZZES===================
@app.route('/instructor/create_quiz/<int:course_id>', methods=['GET', 'POST'])
def create_quiz(course_id):
    if 'instructor' not in session:
        return redirect(url_for('instructor_login'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        title = request.form['title']
        pass_percentage = request.form['pass_percentage']

        # Insert quiz
        cur.execute("""
            INSERT INTO quizzes (course_id, title, pass_percentage)
            VALUES (%s, %s, %s)
        """, (course_id, title, pass_percentage))
        mysql.connection.commit()

        quiz_id = cur.lastrowid

        # Insert questions with correct answer
        questions = zip(
            request.form.getlist('question[]'),
            request.form.getlist('a[]'),
            request.form.getlist('b[]'),
            request.form.getlist('c[]'),
            request.form.getlist('d[]'),
            request.form.getlist('correct[]')
        )

        for q, a, b, c, d, correct in questions:
            cur.execute("""
                INSERT INTO quiz_questions
                (quiz_id, question, option_a, option_b, option_c, option_d, correct_option)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (quiz_id, q, a, b, c, d, correct))

        mysql.connection.commit()
        flash("Quiz created successfully", "success")

    cur.close()
    return render_template('instructor/create_quiz.html', course_id=course_id)

@app.route('/quiz/attempt/<int:course_id>', methods=['GET', 'POST'])
def attempt_quiz(course_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    cur.execute("SELECT id, pass_percentage FROM quizzes WHERE course_id=%s", (course_id,))
    quiz = cur.fetchone()

    quiz_id, pass_marks = quiz

    cur.execute("SELECT * FROM quiz_questions WHERE quiz_id=%s", (quiz_id,))
    questions = cur.fetchall()

    if request.method == 'POST':
        score = 0
        total = len(questions)

        for q in questions:
            qid = q[0]
            correct = q[7]  # a/b/c/d
            selected = request.form.get(str(qid))

            if selected and selected == correct:
                score += 1

        percent = int((score / total) * 100) if total > 0 else 0
        passed = 1 if percent >= pass_marks else 0

        cur.execute(
            "SELECT id FROM registration WHERE username=%s",
            (session['user'],)
        )
        user_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO quiz_attempts (user_id, quiz_id, score, passed)
            VALUES (%s,%s,%s,%s)
        """, (user_id, quiz_id, percent, passed))
        mysql.connection.commit()

        return redirect(url_for('quiz_result', quiz_id=quiz_id))

    return render_template('user/attempt_quiz.html', questions=questions)

@app.route('/quiz/result/<int:quiz_id>')
def quiz_result(quiz_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    cur.execute("SELECT id FROM registration WHERE username=%s", (session['user'],))
    user_id = cur.fetchone()[0]

    cur.execute("""
        SELECT score, passed
        FROM quiz_attempts
        WHERE quiz_id=%s AND user_id=%s
        ORDER BY attempted_at DESC
        LIMIT 1
    """, (quiz_id, user_id))

    result = cur.fetchone()
    cur.close()

    return render_template('user/quiz_result.html', result=result)

@app.route('/instructor/quizzes/<int:course_id>')
def instructor_quiz_list(course_id):
    if 'instructor' not in session:
        return redirect(url_for('instructor_login'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, title, pass_percentage
        FROM quizzes
        WHERE course_id=%s
    """, (course_id,))
    quizzes = cur.fetchall()
    cur.close()

    return render_template(
        'instructor/quiz_list.html',
        quizzes=quizzes,
        course_id=course_id
    )

@app.route('/instructor/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    if 'instructor' not in session:
        return redirect(url_for('instructor_login'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        title = request.form['title']
        pass_percentage = request.form['pass_percentage']

        cur.execute("""
            UPDATE quizzes
            SET title=%s, pass_percentage=%s
            WHERE id=%s
        """, (title, pass_percentage, quiz_id))

        # delete old questions
        cur.execute("DELETE FROM quiz_questions WHERE quiz_id=%s", (quiz_id,))

        # insert updated questions
        questions = zip(
            request.form.getlist('question[]'),
            request.form.getlist('a[]'),
            request.form.getlist('b[]'),
            request.form.getlist('c[]'),
            request.form.getlist('d[]'),
            request.form.getlist('correct[]')
        )

        for q, a, b, c, d, correct in questions:
            cur.execute("""
                INSERT INTO quiz_questions
                (quiz_id, question, option_a, option_b, option_c, option_d, correct_option)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (quiz_id, q, a, b, c, d, correct))

        mysql.connection.commit()
        flash("Quiz updated successfully", "success")
        return redirect(url_for('edit_quiz', quiz_id=quiz_id))

    # GET DATA
    cur.execute("SELECT title, pass_percentage FROM quizzes WHERE id=%s", (quiz_id,))
    quiz = cur.fetchone()

    cur.execute("SELECT * FROM quiz_questions WHERE quiz_id=%s", (quiz_id,))
    questions = cur.fetchall()

    cur.close()

    return render_template(
        'instructor/edit_quiz.html',
        quiz=quiz,
        questions=questions,
        quiz_id=quiz_id
    )

@app.route('/instructor/delete_quiz/<int:quiz_id>')
def delete_quiz(quiz_id):
    if 'instructor' not in session:
        return redirect(url_for('instructor_login'))

    cur = mysql.connection.cursor()

    # get course_id for redirect
    cur.execute("SELECT course_id FROM quizzes WHERE id=%s", (quiz_id,))
    course = cur.fetchone()

    if not course:
        flash("Quiz not found", "danger")
        return redirect(url_for('instructor_dashboard'))

    course_id = course[0]

    # delete questions first (important)
    cur.execute("DELETE FROM quiz_questions WHERE quiz_id=%s", (quiz_id,))

    # delete quiz
    cur.execute("DELETE FROM quizzes WHERE id=%s", (quiz_id,))
    mysql.connection.commit()

    cur.close()

    flash("Quiz deleted successfully", "success")
    return redirect(url_for('instructor_quiz_list', course_id=course_id))





if __name__ == '__main__':
    app.run(debug=True)


