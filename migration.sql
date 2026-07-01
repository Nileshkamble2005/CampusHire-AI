-- PostgreSQL Migration script for AI Campus Placement Portal

-- Drop tables if they exist (to allow re-running the migration)
DROP TABLE IF EXISTS shortlisted_candidates CASCADE;
DROP TABLE IF EXISTS applications CASCADE;
DROP TABLE IF EXISTS job_matches CASCADE;
DROP TABLE IF EXISTS resume_analysis CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 1. Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    college VARCHAR(150),
    branch VARCHAR(100),
    year VARCHAR(20),
    role VARCHAR(20) NOT NULL,
    company VARCHAR(150),
    designation VARCHAR(100),
    website VARCHAR(255) DEFAULT NULL,
    company_location VARCHAR(255) DEFAULT NULL,
    profile_pic VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create jobs table
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150),
    company VARCHAR(150),
    location VARCHAR(100),
    description TEXT,
    required_skills TEXT,
    salary VARCHAR(100) DEFAULT NULL,
    experience VARCHAR(100) DEFAULT NULL,
    employment_type VARCHAR(100) DEFAULT NULL,
    deadline DATE DEFAULT NULL,
    status VARCHAR(20) DEFAULT 'Open',
    recruiter_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_jobs_recruiter FOREIGN KEY (recruiter_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 3. Create resume_analysis table
CREATE TABLE resume_analysis (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    resume_name VARCHAR(255),
    resume_score INT,
    detected_skills TEXT,
    summary TEXT,
    strengths TEXT,
    weaknesses TEXT,
    missing_skills TEXT,
    recommended_roles TEXT,
    interview_readiness TEXT,
    resume_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_resume_analysis_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Create job_matches table
CREATE TABLE job_matches (
    id SERIAL PRIMARY KEY,
    job_id INT NOT NULL,
    student_id INT NOT NULL,
    match_score INT,
    matched_skills TEXT,
    missing_skills TEXT,
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_job_matches_job FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    CONSTRAINT fk_job_matches_student FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. Create applications table
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    job_id INT NOT NULL,
    student_id INT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_applications_job FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    CONSTRAINT fk_applications_student FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 6. Create shortlisted_candidates table
CREATE TABLE shortlisted_candidates (
    id SERIAL PRIMARY KEY,
    job_id INT NOT NULL,
    student_id INT NOT NULL,
    shortlisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_job_student UNIQUE (job_id, student_id),
    CONSTRAINT fk_shortlisted_job FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    CONSTRAINT fk_shortlisted_student FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);
