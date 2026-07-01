# PostgreSQL Database Migration Guide

This guide explains how to set up, initialize, and run the **CampusHire AI** placement portal using the newly integrated **PostgreSQL** database layer.

---

## 1. Database Setup

Ensure PostgreSQL is installed locally and running on your computer.

### Create Database
1. Open your terminal or PGAdmin.
2. Log in using your admin user `postgres` (or your custom database user).
3. Create a database named `AI_Campus_Placement`.
   - **SQL Command**:
     ```sql
     CREATE DATABASE "AI_Campus_Placement";
     ```
   *(Note: The migration script `run_migration.py` will also automatically check and create the database for you if it does not exist).*

---

## 2. Environment Configuration

Create a `.env` file in the root directory of the project (copying from `.env.example`).
Update the database credentials using the keys prefix `DB_*`:

```env
# Flask App Configurations
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=campushire_ai_secret_key

# PostgreSQL Connection Credentials
DB_HOST=localhost
DB_PORT=5432
DB_NAME=AI_Campus_Placement
DB_USER=postgres
DB_PASSWORD=your_postgres_password

# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key
```

---

## 3. Run Schema Migrations

With your virtual environment active, run the migration script:

```bash
# Windows
venv\Scripts\python.exe run_migration.py

# macOS / Linux
source venv/bin/activate
python run_migration.py
```

This script will:
1. Connect to your local PostgreSQL server.
2. Automatically verify/create the database `AI_Campus_Placement`.
3. Read the translated schema from `migration.sql`.
4. Drop any pre-existing tables (`CASCADE` rules) and recreate the 6 tables (`users`, `jobs`, `resume_analysis`, `job_matches`, `applications`, and `shortlisted_candidates`) using optimal PostgreSQL constraints and indexing.

---

## 4. Run the Application

You can now start the web application:

### In Development (Flask server):
```bash
python app.py
```

### In Production (Waitress WSGI server):
```bash
waitress-serve --port=5000 app:app
```
