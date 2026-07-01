-- PostgreSQL Query Cheat Sheet & Testing Scripts for AI Campus Placement Portal

-- 1. View all users
SELECT * FROM users;

-- 2. View all jobs
SELECT * FROM jobs;

-- 3. View all resume analyses
SELECT * FROM resume_analysis;

-- 4. View job recommendations / matches
SELECT * FROM job_matches;

-- 5. View job applications
SELECT * FROM applications;

-- 6. View shortlisted candidates
SELECT * FROM shortlisted_candidates;

-- 7. Query users by role
SELECT id, name, email, role, company FROM users ORDER BY id DESC;

-- 8. Query job details
SELECT title, company, salary, experience, status FROM jobs;
