from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import connection

# Create Blueprint
auth = Blueprint("auth", __name__)


# ==========================
# Home Page
# ==========================

@auth.route("/")
def home():
    return render_template("index.html")


# ==========================
# Login
# ==========================

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        try:
            cursor = connection.cursor()

            cursor.execute(
                "SELECT * FROM users WHERE email=%s",
                (email,)
            )

            user = cursor.fetchone()

            if user:

                if check_password_hash(user["password"], password):

                    session["user_id"] = user["id"]
                    session["name"] = user["name"]
                    session["role"] = user["role"]

                    flash("Login Successful!", "success")

                    if user["role"] == "Student":
                        return redirect("/student_dashboard")

                    else:
                        return redirect("/recruiter_dashboard")

                else:
                    flash("Incorrect Password!", "danger")

            else:
                flash("Email not registered!", "danger")

        except Exception as e:
            print(f"Login DB error: {e}")
            flash("Database connection error. Please try again later.", "danger")

    return render_template("login.html")


# ==========================
# Register
# ==========================

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        phone = request.form["phone"]

        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        role = request.form["role"]

        college = request.form.get("college", "")
        branch = request.form.get("branch", "")
        year = request.form.get("year", "")

        company = request.form.get("company", "")
        designation = request.form.get("designation", "")

        if password != confirm_password:
           flash("Passwords do not match!", "danger")
           return redirect("/register")

        try:
            cursor = connection.cursor()

            # Check Duplicate Email
            cursor.execute(
                "SELECT * FROM users WHERE email=%s",
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:
                flash("Email already registered!", "warning")
                return redirect("/register")

            hashed_password = generate_password_hash(password)

            sql = """
            INSERT INTO users
            (
                name,
                email,
                password,
                phone,
                college,
                branch,
                year,
                company,
                designation,
                role
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """

            cursor.execute(
                sql,
                (
                    fullname,
                    email,
                    hashed_password,
                    phone,
                    college,
                    branch,
                    year,
                    company,
                    designation,
                    role
                )
            )

            connection.commit()

            flash("Registration Successful! Please login.", "success")
            return redirect("/login")

        except Exception as e:
            print(f"Register DB error: {e}")
            connection.rollback()
            flash("Database connection error. Please try again later.", "danger")

    return render_template("register.html")


# ==========================
# Logout
# ==========================

@auth.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully!", "info")

    return redirect("/login")


