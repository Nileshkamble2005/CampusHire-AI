CREATE DATABASE AI_Campus_Placement;
USE AI_Campus_Placement;

SHOW DATABASES;

CREATE TABLE users (

    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    email VARCHAR(100) NOT NULL UNIQUE,

    password VARCHAR(255) NOT NULL,

    phone VARCHAR(15),

    college VARCHAR(150),

    branch VARCHAR(100),

    year VARCHAR(20),

    role VARCHAR(20) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


SHOW TABLES;

DESCRIBE users;

ALTER TABLE users
ADD COLUMN company VARCHAR(150),
ADD COLUMN designation VARCHAR(100);

DESCRIBE users;

SELECT * FROM users;

SELECT id, email, password
FROM users
ORDER BY id DESC;


CREATE TABLE jobs (

    id INT PRIMARY KEY AUTO_INCREMENT,

    title VARCHAR(150),

    company VARCHAR(150),

    location VARCHAR(100),

    description TEXT,

    required_skills TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

DESC jobs;

SELECT * FROM jobs;

CREATE TABLE resume_analysis (

    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    resume_name VARCHAR(255),

    resume_score INT,

    detected_skills TEXT,

    ai_analysis LONGTEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id)
);


SHOW TABLES;

DESC resume_analysis;

SELECT * FROM resume_analysis;

SELECT ai_analysis
FROM resume_analysis;

DROP TABLE IF EXISTS resume_analysis;

CREATE TABLE resume_analysis (

    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    resume_name VARCHAR(255),

    resume_score INT,

    detected_skills TEXT,

    summary TEXT,

    strengths TEXT,

    weaknesses TEXT,

    missing_skills TEXT,

    recommended_roles TEXT,

    interview_readiness VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE

);

DESC resume_analysis;

ALTER TABLE resume_analysis
MODIFY interview_readiness TEXT;


SELECT summary,
       strengths,
       weaknesses,
       missing_skills,
       recommended_roles,
       interview_readiness
FROM resume_analysis
ORDER BY id DESC
LIMIT 1;

SELECT
summary,
strengths,
weaknesses,
missing_skills,
recommended_roles,
interview_readiness
FROM resume_analysis
ORDER BY id DESC
LIMIT 1;


CREATE TABLE job_matches (

    id INT AUTO_INCREMENT PRIMARY KEY,

    job_id INT NOT NULL,

    student_id INT NOT NULL,

    match_score INT,

    matched_skills TEXT,

    missing_skills TEXT,

    recommendation TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(job_id) REFERENCES jobs(id),

    FOREIGN KEY(student_id) REFERENCES users(id)

);


SELECT * FROM jobs;

CREATE TABLE applications (

    id INT AUTO_INCREMENT PRIMARY KEY,

    job_id INT NOT NULL,

    student_id INT NOT NULL,

    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (job_id) REFERENCES jobs(id),

    FOREIGN KEY (student_id) REFERENCES users(id)

);

SHOW TABLES;

select * from applications;

SELECT * FROM job_matches;

CREATE TABLE shortlisted_candidates (

    id INT AUTO_INCREMENT PRIMARY KEY,

    job_id INT NOT NULL,

    student_id INT NOT NULL,

    shortlisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(job_id, student_id),

    FOREIGN KEY(job_id) REFERENCES jobs(id),

    FOREIGN KEY(student_id) REFERENCES users(id)

);

SELECT * FROM shortlisted_candidates;

select * from resume_analysis;

ALTER TABLE resume_analysis
ADD COLUMN resume_path VARCHAR(255);

DESCRIBE resume_analysis;

SELECT resume_name, resume_path
FROM resume_analysis
ORDER BY id DESC
LIMIT 1;
