import json
import google.generativeai as genai
import config

genai.configure(api_key=config.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def analyze_resume(resume_text):

    prompt = f"""
Return ONLY valid JSON.

{{
"resume_score":90,
"summary":"",
"strengths":[],
"weaknesses":[],
"missing_skills":[],
"recommended_roles":[],
"interview_readiness":""
}}

Resume:

{resume_text}
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    return json.loads(text)