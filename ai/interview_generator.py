import json
import google.generativeai as genai
import config

genai.configure(api_key=config.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_interview_questions(resume_summary, job_description):

    prompt = f"""
You are a senior technical interviewer.

Based on the candidate's resume summary and the job description, generate interview questions.

Return ONLY valid JSON.

{{
    "technical_questions":[
        "...",
        "...",
        "..."
    ],
    "hr_questions":[
        "...",
        "...",
        "..."
    ]
}}

Resume Summary:
{resume_summary}

Job Description:
{job_description}
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    text = text.replace("```json", "")
    text = text.replace("```", "")

    return json.loads(text)