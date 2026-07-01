from ai.interview_generator import generate_interview_questions

summary = """
Python Developer with Flask, SQL,
Machine Learning and API experience.
"""

job = """
Looking for a Backend Developer
with Flask, SQL and REST API experience.
"""

questions = generate_interview_questions(
    summary,
    job
)

print(questions)