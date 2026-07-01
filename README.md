# CampusHire AI: AI Campus Placement Portal

CampusHire AI is an intelligent placement portal built using Flask, PostgreSQL, Bootstrap 5, and Google Gemini. The application is designed to streamline the campus hiring process for both students and recruiters by utilizing AI to analyze resumes, calculate resume quality scores, suggest career roles, and rank candidates for job matching.

---

## Key Features

### 👤 For Students
- **Authentication**: Secure register and login.
- **Student Profile**: Manage academic records (College, Branch, Year), contact details, and upload/set a profile photo.
- **Resume Upload**: Upload PDF resumes (under 5MB limit).
- **AI Resume Analysis**: Instant extraction of technical skills, resume score, professional summary, strengths, areas of improvement, missing skills, recommended roles, and interview readiness evaluation.
- **AI Recommended Jobs**: Search and explore matching job opportunities automatically sorted by calculated AI match percentage.
- **Job Application**: Apply to open opportunities in one click.

### 💼 For Recruiters
- **Authentication**: Secure recruiter signup.
- **Recruiter Profile**: Edit corporate details including Company Name, Designation, Website, Location, and upload/set a profile photo.
- **Job Postings Management**: Create, edit, and delete job opportunities with detailed fields:
  - Job Title & Description
  - Required Skills (comma-separated list)
  - Salary Package & Experience Level
  - Employment Type (Full Time, Internship, Part Time, Remote)
  - Application Deadline & Status (Open/Closed)
- **AI Applicant Ranking**: View and review job applicants automatically sorted by their computed match percentage with visual badges:
  - **Excellent Match** (Score >= 85%)
  - **Good Match** (Score >= 60% and < 85%)
  - **Average Match** (Score < 60%)
- **Shortlisting**: Star and shortlist top candidates.
- **Interactive Recruiter Dashboard**: Live statistics (Total Jobs, Applications, Avg Match Score) and a Bar Chart displaying applications analytics per job.

---

## AI Job Matching Algorithm

Match scores are calculated using a weighted average in Python:
1. **Skills Match Score (50%)**: Percentage of job's required skills present in the student's detected skills.
2. **Role Fit Score (30%)**: Checks for alignment/overlap between the candidate's recommended roles and the job title.
3. **Resume Score (20%)**: Candidate's overall resume analysis score from Gemini.

`Match Score = (0.5 * SkillsMatch) + (0.3 * RoleFit) + (0.2 * ResumeScore)`

---

## Tech Stack
- **Backend**: Python Flask
- **Database**: PostgreSQL (psycopg2-binary client)
- **Frontend**: HTML5, CSS3 (Vanilla CSS + Bootstrap 5), JavaScript
- **AI Integration**: Google Gemini API (`gemini-2.5-flash` model)
- **Resume Parsing**: `pdfplumber` (text extraction) & Local regex-based skill parser

---

## Installation & Setup

### 1. Clone the Codebase
Navigate into your project folder.

### 2. Virtual Environment Setup
Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Copy `.env.example` to `.env` and fill in your details:
```bash
copy .env.example .env
```
Ensure you provide a valid `GEMINI_API_KEY` from Google AI Studio.

### 5. Run Database Migrations
Make sure your **PostgreSQL server is running** (default port `5432`). Then run the migration script — it will automatically create the `AI_Campus_Placement` database if it doesn't exist and build all tables:
```bash
python run_migration.py
```
This script creates 6 tables (`users`, `jobs`, `resume_analysis`, `job_matches`, `applications`, `shortlisted_candidates`) with all required columns, foreign keys, and `ON DELETE CASCADE` constraints.

> **Note**: See `POSTGRES_MIGRATION.md` for a full guide on PostgreSQL setup, environment variables, and re-running the schema.

### 6. Run the Application (Development)
Start the Flask development server:
```bash
python app.py
```
Access the application locally at `http://127.0.0.1:5000`.

### 7. Production Serving (Windows & Linux)
To run the application inside a production environment using the production-grade **Waitress** WSGI server:
```bash
waitress-serve --port=5000 app:app
```

---

## Security Highlights
- **Password Hashing**: Enforced using Werkzeug's `pbkdf2:sha256` hashing algorithms.
- **Role-Based Security**: Handled via blueprint-level `before_request` filters to ensure students cannot access recruiter panels, and vice versa.
- **IDOR Protection**: Enforced on `/download_resume/<int:student_id>` endpoints to ensure students can only download their own resumes, while recruiters can download any applicant's resume.
- **File Upload Validation**: Restricts resume uploads strictly to PDF formats under a 5MB size threshold, and limits profile picture uploads to PNG, JPG, JPEG, and GIF formats under a 2MB threshold.
- **SQL Injection Prevention**: psycopg2 parameterized queries (`%s` placeholders) used for all database operations to prevent SQL injection.
