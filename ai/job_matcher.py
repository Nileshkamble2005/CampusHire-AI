import json
import os
import google.generativeai as genai
import config

genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


def match_resume_with_job(resume_text, job_description):
    """
    Legacy Gemini-based job matcher.
    """
    prompt = f"""
You are an expert AI Recruiter.

Compare the resume with the job description.

Return ONLY valid JSON.

Format:

{{
    "match_score":90,
    "matched_skills":[
        "Python",
        "Flask"
    ],
    "missing_skills":[
        "Docker"
    ],
    "recommendation":"Strong candidate. Learn Docker."
}}

Resume:

{resume_text}

Job Description:

{job_description}

Do not explain anything.
Return JSON only.
"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def calculate_match_details(analysis, job, resume_text=""):
    """
    Calculate match score using: Skills, Recommended Roles, and Resume Score.
    Returns:
    - match_score: int
    - matched_skills: list of strings
    - missing_skills: list of strings
    - recommendation: string
    """
    # 1. Required Skills Matching
    req_skills_str = job.get("required_skills") or ""
    req_skills = [s.strip().lower() for s in req_skills_str.split(",") if s.strip()]
    
    detected_skills_str = analysis.get("detected_skills") or ""
    detected_skills = [s.strip().lower() for s in detected_skills_str.split(",") if s.strip()]
    
    matched_skills = []
    missing_skills = []
    
    if req_skills:
        for s in req_skills:
            if s in detected_skills:
                matched_skills.append(s.title())
            else:
                missing_skills.append(s.title())
        skills_match_score = (len(matched_skills) / len(req_skills)) * 100
    else:
        # If no skills are explicitly required, look for detected skills in the description
        desc_lower = (job.get("description") or "").lower()
        matched = [s for s in detected_skills if s in desc_lower]
        matched_skills = [s.title() for s in matched]
        # Baseline score: if candidate has skills, match score is based on count up to 5, else 100
        skills_match_score = min(100, len(matched) * 20) if detected_skills else 100

    # 2. Recommended Roles Matching
    job_title_lower = (job.get("title") or "").lower()
    rec_roles_str = analysis.get("recommended_roles") or ""
    rec_roles = [r.strip().lower() for r in rec_roles_str.split(",") if r.strip()]
    
    role_fit_score = 0
    role_matched = False
    
    if rec_roles:
        for r in rec_roles:
            if r in job_title_lower or job_title_lower in r:
                role_fit_score = 100
                role_matched = True
                break
        
        if not role_matched:
            # Word-level overlap check
            job_words = set(job_title_lower.replace("/", " ").replace("-", " ").split())
            for r in rec_roles:
                r_words = set(r.replace("/", " ").replace("-", " ").split())
                if job_words.intersection(r_words):
                    role_fit_score = 70
                    role_matched = True
                    break
                    
        if not role_matched:
            role_fit_score = 30  # Baseline role alignment for analyzed resume
    else:
        role_fit_score = 50  # Default middle ground if no recommendations are found

    # 3. Resume Score
    resume_score = analysis.get("resume_score") or 0
    if isinstance(resume_score, str):
        try:
            resume_score = int(resume_score)
        except ValueError:
            resume_score = 50

    # Weighted Average Match Score
    # 50% Skills Match + 30% Role Fit + 20% Resume Score
    final_score = round(0.5 * skills_match_score + 0.3 * role_fit_score + 0.2 * resume_score)
    
    # Ensure score bounds
    final_score = max(0, min(100, final_score))

    # Recommendation Formulation
    if final_score >= 85:
        badge = "Excellent Match"
        rec_text = f"Excellent candidate alignment ({final_score}%). Matches key skills and aligns strongly with recommended roles."
    elif final_score >= 60:
        badge = "Good Match"
        if missing_skills:
            rec_text = f"Good match ({final_score}%). Solid core skills. Upskilling in {', '.join(missing_skills[:2])} will make this fit perfect."
        else:
            rec_text = f"Good match ({final_score}%). Solid core skills and profile alignment."
    else:
        badge = "Average Match"
        if missing_skills:
            rec_text = f"Average match ({final_score}%). Recommended to learn {', '.join(missing_skills[:3])} to better suit the requirements."
        else:
            rec_text = f"Average match ({final_score}%). Profile alignment can be improved through core placement training."

    return {
        "match_score": final_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommendation": rec_text,
        "match_badge": badge
    }


def calculate_and_save_match(student_id, job_id, cursor, connection):
    """
    Helper function to calculate match details for a student and a job,
    and save them in the job_matches table.
    """
    # Fetch job details
    cursor.execute("SELECT * FROM jobs WHERE id=%s", (job_id,))
    job = cursor.fetchone()
    if not job:
        return None
        
    # Fetch latest resume analysis
    cursor.execute("""
        SELECT * FROM resume_analysis 
        WHERE user_id=%s 
        ORDER BY created_at DESC LIMIT 1
    """, (student_id,))
    analysis = cursor.fetchone()
    if not analysis:
        return None
        
    resume_text = ""
    # Try reading PDF text from disk if path exists
    if analysis.get("resume_path") and os.path.exists(analysis["resume_path"]):
        try:
            from ai.resume_parser import extract_text
            resume_text = extract_text(analysis["resume_path"])
        except Exception as e:
            print(f"Error extracting resume text during migration match: {e}")
            
    match_details = calculate_match_details(analysis, job, resume_text)
    
    # Save match to database
    cursor.execute("""
        SELECT id FROM job_matches 
        WHERE job_id=%s AND student_id=%s
    """, (job_id, student_id))
    existing = cursor.fetchone()
    
    matched_skills_str = ", ".join(match_details["matched_skills"])
    missing_skills_str = ", ".join(match_details["missing_skills"])
    
    if existing:
        cursor.execute("""
            UPDATE job_matches
            SET
                match_score=%s,
                matched_skills=%s,
                missing_skills=%s,
                recommendation=%s
            WHERE id=%s
        """, (
            match_details["match_score"],
            matched_skills_str,
            missing_skills_str,
            match_details["recommendation"],
            existing["id"]
        ))
    else:
        cursor.execute("""
            INSERT INTO job_matches
            (job_id, student_id, match_score, matched_skills, missing_skills, recommendation)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            job_id,
            student_id,
            match_details["match_score"],
            matched_skills_str,
            missing_skills_str,
            match_details["recommendation"]
        ))
    connection.commit()
    return match_details