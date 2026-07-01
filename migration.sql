-- Migration script for AI Campus Placement Portal

USE AI_Campus_Placement;

-- 1. Alter users table to add website and company_location for recruiters
ALTER TABLE users ADD COLUMN website VARCHAR(255) DEFAULT NULL;
ALTER TABLE users ADD COLUMN company_location VARCHAR(255) DEFAULT NULL;

-- 2. Alter jobs table to add detailed attributes and recruiter_id
ALTER TABLE jobs ADD COLUMN salary VARCHAR(100) DEFAULT NULL;
ALTER TABLE jobs ADD COLUMN experience VARCHAR(100) DEFAULT NULL;
ALTER TABLE jobs ADD COLUMN employment_type VARCHAR(100) DEFAULT NULL;
ALTER TABLE jobs ADD COLUMN deadline DATE DEFAULT NULL;
ALTER TABLE jobs ADD COLUMN status VARCHAR(20) DEFAULT 'Open';
ALTER TABLE jobs ADD COLUMN recruiter_id INT DEFAULT NULL;

-- Add foreign key constraint for recruiter_id in jobs
ALTER TABLE jobs ADD CONSTRAINT fk_jobs_recruiter FOREIGN KEY (recruiter_id) REFERENCES users(id) ON DELETE SET NULL;

-- 3. Modify existing foreign keys to include ON DELETE CASCADE

-- Drop old foreign keys in job_matches and add ON DELETE CASCADE
ALTER TABLE job_matches DROP FOREIGN KEY job_matches_ibfk_1;
ALTER TABLE job_matches DROP FOREIGN KEY job_matches_ibfk_2;
ALTER TABLE job_matches ADD CONSTRAINT fk_job_matches_job FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE;
ALTER TABLE job_matches ADD CONSTRAINT fk_job_matches_student FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE;

-- Drop old foreign keys in applications and add ON DELETE CASCADE
ALTER TABLE applications DROP FOREIGN KEY applications_ibfk_1;
ALTER TABLE applications DROP FOREIGN KEY applications_ibfk_2;
ALTER TABLE applications ADD CONSTRAINT fk_applications_job FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE;
ALTER TABLE applications ADD CONSTRAINT fk_applications_student FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE;

-- Drop old foreign keys in shortlisted_candidates and add ON DELETE CASCADE
ALTER TABLE shortlisted_candidates DROP FOREIGN KEY shortlisted_candidates_ibfk_1;
ALTER TABLE shortlisted_candidates DROP FOREIGN KEY shortlisted_candidates_ibfk_2;
ALTER TABLE shortlisted_candidates ADD CONSTRAINT fk_shortlisted_job FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE;
ALTER TABLE shortlisted_candidates ADD CONSTRAINT fk_shortlisted_student FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE;

-- 4. Alter users table to add profile_pic for students and recruiters
ALTER TABLE users ADD COLUMN profile_pic VARCHAR(255) DEFAULT NULL;
