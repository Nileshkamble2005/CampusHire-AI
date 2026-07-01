from flask import Flask
import os

from routes.auth import auth
from routes.student import student
from routes.recruiter import recruiter
from routes.ai_routes import ai

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "campushire_ai_secret_key"
)

UPLOAD_FOLDER = "uploads/resumes"
PROFILE_PIC_FOLDER = "uploads/profile_pics"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROFILE_PIC_FOLDER"] = PROFILE_PIC_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROFILE_PIC_FOLDER, exist_ok=True)

from flask import send_from_directory

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory('uploads', filename)

app.register_blueprint(auth)
app.register_blueprint(student)
app.register_blueprint(recruiter)
app.register_blueprint(ai)


from flask import render_template

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)