from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash,
    current_app
)

from flask import send_file
import os

from database import connection

# Create Blueprint
recruiter = Blueprint("recruiter", __name__)


@recruiter.before_request
def restrict_recruiter_access():
    if "user_id" not in session:
        return redirect("/login")

    # Allow students to access download_resume (ownership checked inside route)
    if request.endpoint == 'recruiter.download_resume':
        return

    if session.get("role") != "Recruiter":
        flash("Access Denied: Recruiter account required.", "danger")
        return redirect("/student_dashboard")


# ==========================
# Recruiter Dashboard
# ==========================

@recruiter.route("/recruiter_dashboard")
def recruiter_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "Recruiter":
        flash("Unauthorized access.", "danger")
        return redirect("/student_dashboard")

    cursor = connection.cursor()

    recruiter_id = session["user_id"]

    # Total Jobs posted by this recruiter
    cursor.execute("SELECT COUNT(*) AS total_jobs FROM jobs WHERE recruiter_id=%s", (recruiter_id,))
    total_jobs = cursor.fetchone()["total_jobs"]

    # Total Students registered (global)
    cursor.execute("""
        SELECT COUNT(*) AS total_students
        FROM users
        WHERE role='Student'
    """)
    total_students = cursor.fetchone()["total_students"]

    # Total Resume Uploads (global)
    cursor.execute("""
        SELECT COUNT(*) AS total_resumes
        FROM resume_analysis
    """)
    total_resumes = cursor.fetchone()["total_resumes"]

    # Fetch jobs posted by this recruiter
    cursor.execute("""
        SELECT
            jobs.*,
            COUNT(applications.id) AS applicant_count
        FROM jobs
        LEFT JOIN applications
        ON jobs.id = applications.job_id
        WHERE jobs.recruiter_id=%s
        GROUP BY jobs.id
        ORDER BY jobs.id DESC
    """, (recruiter_id,))

    jobs = cursor.fetchall()
    if jobs is None:
        jobs = []

    # Total Applications for this recruiter's jobs
    cursor.execute("""
        SELECT COUNT(applications.id) AS total_applications
        FROM applications
        JOIN jobs ON applications.job_id = jobs.id
        WHERE jobs.recruiter_id=%s
    """, (recruiter_id,))
    total_applications = cursor.fetchone()["total_applications"]

    # Total Shortlisted for this recruiter's jobs
    cursor.execute("""
        SELECT COUNT(shortlisted_candidates.id) AS total_shortlisted
        FROM shortlisted_candidates
        JOIN jobs ON shortlisted_candidates.job_id = jobs.id
        WHERE jobs.recruiter_id=%s
    """, (recruiter_id,))
    total_shortlisted = cursor.fetchone()["total_shortlisted"]

    # Average Match Score for this recruiter's jobs
    cursor.execute("""
        SELECT ROUND(AVG(job_matches.match_score),0) AS average_match
        FROM job_matches
        JOIN jobs ON job_matches.job_id = jobs.id
        WHERE jobs.recruiter_id=%s
    """, (recruiter_id,))
    result = cursor.fetchone()
    average_match = result["average_match"] or 0

    # Applications Per Job Chart (only for this recruiter's jobs)
    cursor.execute("""
        SELECT
           jobs.title,
           COUNT(applications.id) AS total
        FROM jobs
        LEFT JOIN applications
        ON jobs.id = applications.job_id
        WHERE jobs.recruiter_id=%s
        GROUP BY jobs.id
    """, (recruiter_id,))
    chart = cursor.fetchall()

    # Fetch 5 Recent Applicants for this recruiter's jobs
    cursor.execute("""
        SELECT
            users.id as student_id,
            users.name as student_name,
            users.email as student_email,
            jobs.title as job_title,
            jobs.id as job_id,
            applications.applied_at,
            job_matches.match_score
        FROM applications
        JOIN users ON applications.student_id = users.id
        JOIN jobs ON applications.job_id = jobs.id
        LEFT JOIN job_matches ON job_matches.job_id = jobs.id AND job_matches.student_id = users.id
        WHERE jobs.recruiter_id=%s
        ORDER BY applications.applied_at DESC
        LIMIT 5
    """, (recruiter_id,))
    recent_applicants = cursor.fetchall()
    if recent_applicants is None:
        recent_applicants = []

    cursor.execute("SELECT * FROM users WHERE id=%s", (recruiter_id,))
    recruiter_user = cursor.fetchone()

    return render_template(
        "recruiter_dashboard.html",
        total_jobs=total_jobs,
        total_students=total_students,
        total_resumes=total_resumes,
        total_applications=total_applications,
        total_shortlisted=total_shortlisted,
        average_match=average_match,
        jobs=jobs,
        chart=chart,
        recent_applicants=recent_applicants,
        user=recruiter_user
    )

# ==========================
# Create Job
# ==========================

@recruiter.route("/create_job", methods=["GET", "POST"])
def create_job():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "Recruiter":
        flash("Unauthorized access.", "danger")
        return redirect("/student_dashboard")

    if request.method == "POST":

        title = request.form["title"]
        company = request.form["company"]
        location = request.form["location"]
        description = request.form["description"]
        salary = request.form.get("salary", "")
        required_skills = request.form.get("required_skills", "")
        experience = request.form.get("experience", "")
        employment_type = request.form.get("employment_type", "")
        deadline = request.form.get("deadline", "")

        # Format deadline for SQL (NULL if empty)
        deadline_val = deadline if deadline else None

        cursor = connection.cursor()

        sql = """
        INSERT INTO jobs
        (
            title,
            company,
            location,
            description,
            salary,
            required_skills,
            experience,
            employment_type,
            deadline,
            status,
            recruiter_id
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,'Open',%s)
        """

        try:

            cursor.execute(
                sql,
                (
                    title,
                    company,
                    location,
                    description,
                    salary,
                    required_skills,
                    experience,
                    employment_type,
                    deadline_val,
                    session["user_id"]
                )
            )

            connection.commit()
            job_id = cursor.lastrowid

            # Calculate match score for all students who have uploaded resumes
            cursor.execute("SELECT DISTINCT user_id FROM resume_analysis")
            students = cursor.fetchall()
            from ai.job_matcher import calculate_and_save_match
            for stud in students:
                try:
                    calculate_and_save_match(stud["user_id"], job_id, cursor, connection)
                except Exception as ex:
                    print(f"Error matching new job {job_id} with student {stud['user_id']}: {ex}")

            flash("Job posted successfully!", "success")

        except Exception as e:

            print("Database Error:", e)
            flash("Failed to post job. Database error.", "danger")

        return redirect("/recruiter_dashboard")

    return render_template("create_job.html")


@recruiter.route("/delete_job/<int:job_id>")
def delete_job(job_id):

    if "user_id" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM jobs WHERE id=%s",
        (job_id,)
    )

    connection.commit()

    flash("Job deleted successfully!", "success")

    return redirect("/recruiter_dashboard")

@recruiter.route("/view_applicants/<int:job_id>")
def view_applicants(job_id):

    if "user_id" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    cursor.execute("""
SELECT

    users.id,
    users.name,
    users.email,

    resume_analysis.resume_score,
    resume_analysis.summary,
    resume_analysis.recommended_roles,

    job_matches.match_score,
    job_matches.matched_skills,
    job_matches.missing_skills,
    job_matches.recommendation

FROM applications

JOIN users
ON applications.student_id = users.id

LEFT JOIN resume_analysis
ON users.id = resume_analysis.user_id

LEFT JOIN job_matches
ON job_matches.student_id = users.id
AND job_matches.job_id = applications.job_id

WHERE applications.job_id=%s

ORDER BY job_matches.match_score DESC

""", (job_id,))

    applicants = cursor.fetchall()

    return render_template(
    "view_applicants.html",
    applicants=applicants,
    job_id=job_id
    ) 

@recruiter.route("/shortlist_candidate/<int:job_id>/<int:student_id>")
def shortlist_candidate(job_id, student_id):

    if "user_id" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    # Check if already shortlisted
    cursor.execute(
        """
        SELECT *
        FROM shortlisted_candidates
        WHERE job_id=%s
        AND student_id=%s
        """,
        (job_id, student_id)
    )

    existing = cursor.fetchone()

    if existing:

        flash("Candidate already shortlisted.", "warning")

    else:

        cursor.execute(
            """
            INSERT INTO shortlisted_candidates
            (
                job_id,
                student_id
            )
            VALUES
            (%s,%s)
            """,
            (job_id, student_id)
        )

        connection.commit()

        flash("Candidate shortlisted successfully!", "success")

    return redirect(f"/view_applicants/{job_id}")


@recruiter.route("/shortlisted_candidates")
def shortlisted_candidates():

    if "user_id" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    cursor.execute("""
        SELECT

            users.id,
            users.name,
            users.email,

            jobs.title,

            resume_analysis.resume_score,

            job_matches.match_score

        FROM shortlisted_candidates

        JOIN users
        ON shortlisted_candidates.student_id = users.id

        JOIN jobs
        ON shortlisted_candidates.job_id = jobs.id

        LEFT JOIN resume_analysis
        ON users.id = resume_analysis.user_id

        LEFT JOIN job_matches
        ON job_matches.student_id = users.id
        AND job_matches.job_id = jobs.id

        ORDER BY job_matches.match_score DESC
    """)

    candidates = cursor.fetchall()

    return render_template(
        "shortlisted_candidates.html",
        candidates=candidates
    )


@recruiter.route("/edit_job/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "Recruiter":
        flash("Unauthorized access.", "danger")
        return redirect("/student_dashboard")

    cursor = connection.cursor()

    if request.method == "POST":

        title = request.form["title"]
        company = request.form["company"]
        location = request.form["location"]
        description = request.form["description"]
        salary = request.form.get("salary", "")
        required_skills = request.form.get("required_skills", "")
        experience = request.form.get("experience", "")
        employment_type = request.form.get("employment_type", "")
        deadline = request.form.get("deadline", "")
        status = request.form.get("status", "Open")

        deadline_val = deadline if deadline else None

        cursor.execute("""
            UPDATE jobs
            SET
                title=%s,
                company=%s,
                location=%s,
                description=%s,
                salary=%s,
                required_skills=%s,
                experience=%s,
                employment_type=%s,
                deadline=%s,
                status=%s
            WHERE id=%s
        """,
        (
            title,
            company,
            location,
            description,
            salary,
            required_skills,
            experience,
            employment_type,
            deadline_val,
            status,
            job_id
        ))

        connection.commit()

        # Recalculate match score for all students who have uploaded resumes
        cursor.execute("SELECT DISTINCT user_id FROM resume_analysis")
        students = cursor.fetchall()
        from ai.job_matcher import calculate_and_save_match
        for stud in students:
            try:
                calculate_and_save_match(stud["user_id"], job_id, cursor, connection)
            except Exception as ex:
                print(f"Error recalculating job matches: {ex}")

        flash("Job updated successfully!", "success")

        return redirect("/recruiter_dashboard")

    cursor.execute(
        "SELECT * FROM jobs WHERE id=%s",
        (job_id,)
    )

    job = cursor.fetchone()
    

    if job is None:
      job = {}

    return render_template(
        "edit_job.html",
        job=job
    )

@recruiter.route("/download_resume/<int:student_id>")
def download_resume(student_id):

    if "user_id" not in session:
        return redirect("/login")

    # IDOR check: Students can only download their own resume
    if session.get("role") == "Student" and session["user_id"] != student_id:
        flash("Unauthorized access: You can only download your own resume.", "danger")
        return redirect("/student_dashboard")

    # Access control check
    if session.get("role") not in ("Student", "Recruiter"):
        flash("Unauthorized access.", "danger")
        return redirect("/login")

    cursor = connection.cursor()

    cursor.execute("""
        SELECT resume_path
        FROM resume_analysis
        WHERE user_id=%s
        ORDER BY created_at DESC
        LIMIT 1
    """, (student_id,))

    resume = cursor.fetchone()

    if resume is None:

        flash("Resume not found.", "danger")
        if session.get("role") == "Student":
            return redirect("/student_dashboard")
        return redirect("/recruiter_dashboard")

    filepath = resume["resume_path"]
    
    # Check if file exists on disk
    if not filepath or not os.path.exists(filepath):
        flash("Resume file not found on server disk.", "danger")
        if session.get("role") == "Student":
            return redirect("/student_dashboard")
        return redirect("/recruiter_dashboard")

    return send_file(
        filepath,
        as_attachment=True
    )

@recruiter.route("/student_profile/<int:student_id>")
def student_profile(student_id):

    if "user_id" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            phone,
            college,
            branch,
            year,
            profile_pic
        FROM users
        WHERE id=%s
    """, (student_id,))

    student = cursor.fetchone()

    if not student:
        flash("Student not found.", "danger")
        return redirect("/shortlisted_candidates")

    cursor.execute("""
        SELECT
            resume_score,
            summary,
            detected_skills,
            strengths,
            weaknesses,
            missing_skills,
            recommended_roles,
            interview_readiness,
            resume_name,
            resume_path
        FROM resume_analysis
        WHERE user_id=%s
        ORDER BY id DESC
        LIMIT 1
    """, (student_id,))

    analysis = cursor.fetchone()

    if analysis is None:
        analysis = None

    return render_template(
        "student_profile.html",
        student=student,
        analysis=analysis,
        recruiter_view=True
    )


@recruiter.route("/recruiter_profile", methods=["GET", "POST"])
def recruiter_profile():

    if "user_id" not in session:
        return redirect("/login")

    cursor = connection.cursor()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        company = request.form["company"]
        designation = request.form["designation"]
        website = request.form["website"]
        company_location = request.form["company_location"]

        profile_pic_path = None
        if "profile_pic" in request.files:
            file = request.files["profile_pic"]
            if file and file.filename != "":
                allowed_image_extensions = {"png", "jpg", "jpeg", "gif"}
                ext = file.filename.rsplit(".", 1)[-1].lower()
                if ext not in allowed_image_extensions:
                    flash("Only PNG, JPG, JPEG, and GIF images are allowed.", "danger")
                    return redirect("/recruiter_profile")

                file.seek(0, os.SEEK_END)
                size = file.tell()
                file.seek(0)
                if size > 2 * 1024 * 1024:
                    flash("Profile picture must be under 2MB.", "danger")
                    return redirect("/recruiter_profile")

                filename = f"recruiter_{session['user_id']}.{ext}"
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
                    company=%s,
                    designation=%s,
                    website=%s,
                    company_location=%s,
                    profile_pic=%s
                WHERE id=%s
            """,
            (
                name,
                email,
                phone,
                company,
                designation,
                website,
                company_location,
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
                    company=%s,
                    designation=%s,
                    website=%s,
                    company_location=%s
                WHERE id=%s
            """,
            (
                name,
                email,
                phone,
                company,
                designation,
                website,
                company_location,
                session["user_id"]
            ))

        connection.commit()

        session["name"] = name

        flash("Profile updated successfully!", "success")

        return redirect("/recruiter_profile")

    cursor.execute(
        "SELECT * FROM users WHERE id=%s",
        (session["user_id"],)
    )

    recruiter_data = cursor.fetchone()
    if recruiter_data is None:
        recruiter_data = {}

    return render_template(
        "recruiter_profile.html",
        recruiter=recruiter_data
    )