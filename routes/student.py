from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    current_app,
    flash
)

from werkzeug.utils import secure_filename

from database import connection

import os
from ai.resume_parser import extract_text
from ai.skill_matcher import extract_skills
from ai.resume_score import calculate_resume_score

from ai.gemini_analyzer import analyze_resume
from ai.job_matcher import match_resume_with_job


# Create Blueprint
student = Blueprint("student", __name__)


@student.before_request
def restrict_student_access():
    if "user_id" not in session:
        return redirect("/login")
    if session.get("role") != "Student":
        flash("Access Denied: Student account required.", "danger")
        return redirect("/recruiter_dashboard")


# Allowed File Extensions
ALLOWED_EXTENSIONS = {"pdf"}


# Check File Extension
def allowed_file(filename):

    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ==========================
# Student Dashboard
# ==========================

import json

@student.route("/student_dashboard")
def student_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM resume_analysis
        WHERE user_id=%s
        ORDER BY created_at DESC
        LIMIT 1
    """, (session["user_id"],))

    analysis = cursor.fetchone()

    cursor.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    user_data = cursor.fetchone()

    local_score = 0
    if analysis and analysis.get("detected_skills"):
        skills_list = [s.strip() for s in analysis["detected_skills"].split(",") if s.strip()]
        local_score = calculate_resume_score(skills_list)

    if analysis is None:
        analysis = None

    search = request.args.get("search", "")

    cursor = connection.cursor()

    if search:

        cursor.execute("""
            SELECT 
                jobs.*,
                job_matches.match_score,
                job_matches.matched_skills,
                job_matches.missing_skills,
                job_matches.recommendation
            FROM jobs
            LEFT JOIN job_matches
            ON jobs.id = job_matches.job_id
            AND job_matches.student_id = %s
            WHERE
                (jobs.title LIKE %s
                OR jobs.company LIKE %s
                OR jobs.location LIKE %s)
                AND jobs.status = 'Open'
            ORDER BY COALESCE(job_matches.match_score, 0) DESC, jobs.id DESC
        """,
        (
            session["user_id"],
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ))

    else:

        cursor.execute("""
            SELECT 
                jobs.*,
                job_matches.match_score,
                job_matches.matched_skills,
                job_matches.missing_skills,
                job_matches.recommendation
            FROM jobs
            LEFT JOIN job_matches
            ON jobs.id = job_matches.job_id
            AND job_matches.student_id = %s
            WHERE jobs.status = 'Open'
            ORDER BY COALESCE(job_matches.match_score, 0) DESC, jobs.id DESC
        """, (session["user_id"],))

    jobs = cursor.fetchall()

    return render_template(
        "student_dashboard.html",
        analysis=analysis,
        jobs=jobs,
        search=search,
        local_score=local_score,
        user=user_data
    )

# ==========================
# Upload Resume
# ==========================

@student.route("/upload_resume", methods=["POST"])
def upload_resume():

    if "user_id" not in session:
        return redirect("/login")

    if "resume" not in request.files:
        flash("Please select a resume.", "danger")
        return redirect("/student_dashboard")

    file = request.files["resume"]

    if file.filename == "":
        flash("Please select a PDF file.", "danger")
        return redirect("/student_dashboard")

    if file and allowed_file(file.filename):

        # Check file size (limit to 5MB)
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0) # Reset pointer
        
        if size > 5 * 1024 * 1024:
            flash("Resume file size must be under 5MB.", "danger")
            return redirect("/student_dashboard")

        filename = secure_filename(file.filename)

        filepath = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)

        resume_path = os.path.join(
          "uploads",
           "resumes",
           filename
        )

        # ----------------------------
        # Extract Resume Text
        # ----------------------------

        text = extract_text(filepath)

        # ----------------------------
        # Local AI
        # ----------------------------

        skills = extract_skills(text)

        score = calculate_resume_score(skills)

        # ----------------------------
        # Gemini AI
        # ----------------------------

        try:

            analysis = analyze_resume(text)

            print("\n========== GEMINI RESPONSE ==========")
            print(analysis)
            print("=====================================\n")

        except Exception as e:

            print("Gemini Error:", e)

            analysis = {
                "resume_score": score,
                "summary": "Unable to generate AI summary.",
                "strengths": [],
                "weaknesses": [],
                "missing_skills": [],
                "recommended_roles": [],
                "interview_readiness": "Not Available"
            }

        # ----------------------------
        # Prepare Data
        # ----------------------------

        resume_score = analysis.get("resume_score", score)

        summary = analysis.get("summary", "")

        strengths = ", ".join(
            analysis.get("strengths", [])
        )

        weaknesses = ", ".join(
            analysis.get("weaknesses", [])
        )

        missing_skills = ", ".join(
            analysis.get("missing_skills", [])
        )

        recommended_roles = ", ".join(
            analysis.get("recommended_roles", [])
        )

        interview_readiness = analysis.get(
            "interview_readiness",
            ""
        )

        skills_text = ", ".join(skills)

        # ----------------------------
        # Save to Database
        # ----------------------------

        cursor = connection.cursor()

        sql = """
        INSERT INTO resume_analysis
        (
          user_id,
          resume_name,
          resume_score,
          detected_skills,
          summary,
          strengths,
          weaknesses,
          missing_skills,
          recommended_roles,
          interview_readiness,
          resume_path
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        cursor.execute(
            sql,
            (
                session["user_id"],
                filename,
                resume_score,
                skills_text,
                summary,
                strengths,
                weaknesses,
                missing_skills,
                recommended_roles,
                interview_readiness,
                resume_path
            )
        )

        connection.commit()

        # ==========================================
        # Fetch all jobs from database
        # ==========================================

        cursor.execute("SELECT * FROM jobs")
        jobs = cursor.fetchall()

        # ==========================================
        # Compare Resume with Every Job
        # ==========================================

        from ai.job_matcher import calculate_and_save_match

        for job in jobs:

            try:

                calculate_and_save_match(session["user_id"], job["id"], cursor, connection)

            except Exception as e:

                print("Job Match Error:", e)

        print("✅ Resume Uploaded Successfully!")
        print("Skills:", skills)
        print("Score:", resume_score)

        flash("Resume analyzed successfully!", "success")

    else:

        flash("Only PDF files are allowed.", "danger")

    return redirect("/student_dashboard")


@student.route("/apply_job/<int:job_id>")
def apply_job(job_id):

    if "user_id" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    # Check if already applied
    cursor.execute(
        """
        SELECT *
        FROM applications
        WHERE job_id=%s
        AND student_id=%s
        """,
        (job_id, session["user_id"])
    )

    existing = cursor.fetchone()

    if existing:

        flash("You have already applied for this job.", "warning")

    else:

        cursor.execute(
            """
            INSERT INTO applications
            (job_id, student_id)
            VALUES (%s,%s)
            """,
            (job_id, session["user_id"])
        )

        connection.commit()

        flash("Application submitted successfully!", "success")

    return redirect("/student_dashboard")


@student.route("/student_profile", methods=["GET", "POST"])
def student_profile():

    if "user_id" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        college = request.form["college"]
        branch = request.form["branch"]
        year = request.form["year"]

        profile_pic_path = None
        if "profile_pic" in request.files:
            file = request.files["profile_pic"]
            if file and file.filename != "":
                allowed_image_extensions = {"png", "jpg", "jpeg", "gif"}
                ext = file.filename.rsplit(".", 1)[-1].lower()
                if ext not in allowed_image_extensions:
                    flash("Only PNG, JPG, JPEG, and GIF images are allowed.", "danger")
                    return redirect("/student_profile")

                file.seek(0, os.SEEK_END)
                size = file.tell()
                file.seek(0)
                if size > 2 * 1024 * 1024:
                    flash("Profile picture must be under 2MB.", "danger")
                    return redirect("/student_profile")

                filename = f"student_{session['user_id']}.{ext}"
                filepath = os.path.join(current_app.config["PROFILE_PIC_FOLDER"], filename)
                file.save(filepath)
                profile_pic_path = f"/uploads/profile_pics/{filename}"

        if profile_pic_path:
            cursor.execute("""
                UPDATE users
                SET
                    name=%s,
                    email=%s,
                    phone=%s,
                    college=%s,
                    branch=%s,
                    year=%s,
                    profile_pic=%s
                WHERE id=%s
            """,
            (
                name,
                email,
                phone,
                college,
                branch,
                year,
                profile_pic_path,
                session["user_id"]
            ))
        else:
            cursor.execute("""
                UPDATE users
                SET
                    name=%s,
                    email=%s,
                    phone=%s,
                    college=%s,
                    branch=%s,
                    year=%s
                WHERE id=%s
            """,
            (
                name,
                email,
                phone,
                college,
                branch,
                year,
                session["user_id"]
            ))

        connection.commit()

        session["name"] = name

        flash("Profile updated successfully!", "success")

        return redirect("/student_profile")

    cursor.execute(
        "SELECT * FROM users WHERE id=%s",
        (session["user_id"],)
    )

    student = cursor.fetchone()
    if student is None:
        student = {}

    cursor.execute("""
        SELECT *
        FROM resume_analysis
        WHERE user_id=%s
        ORDER BY created_at DESC
        LIMIT 1
    """, (session["user_id"],))
    analysis = cursor.fetchone()

    return render_template(
        "student_profile.html",
        student=student,
        analysis=analysis
    )