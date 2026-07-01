from ai.resume_parser import extract_text

resume_path = "uploads/resumes/resume.pdf"

text = extract_text(resume_path)

print(text)