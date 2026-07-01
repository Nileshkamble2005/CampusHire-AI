skills = [

"python",

"R",

"sql",

"machine learning",

"ML",

"deep learning",

"Artificial Intelligence",

"AI",

"AI Agents",

"PyTorch",

"Keras",

"Scikit-learn",

"Transformers",

"NLP",

"Gemini AI",

"Prompt Engineering",

"flask",

"fastapi",

"html",

"css",

"javascript",

"mysql",

"mongodb",

"pandas",

"numpy",

"tensorflow",

"opencv",

"HuggingFace",

"git",

"github"

]

def extract_skills(text):

    text = text.lower()

    found_skills = []

    for skill in skills:

        if skill in text:
            found_skills.append(skill)

    return found_skills