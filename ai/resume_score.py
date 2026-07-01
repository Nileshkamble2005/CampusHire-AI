def calculate_resume_score(skills):

    total_skills = 30

    score = (len(skills) / total_skills) * 100

    return round(score)