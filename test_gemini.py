from ai.gemini_analyzer import analyze_resume

sample_resume = """
Nilesh Kamble

Skills:
Python
SQL
Flask
Machine Learning
Git
FastAPI

Projects:
AI Campus Placement Portal
"""

result = analyze_resume(sample_resume)

print(result)