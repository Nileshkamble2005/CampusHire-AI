from ai.resume_parser import extract_text
from ai.skill_matcher import extract_skills

text = extract_text("uploads/resumes/Blood_Relation.pdf")

skills = extract_skills(text)

print(skills)