from flask import (
    Blueprint,
    request,
    jsonify
)

from ai.gemini_analyzer import analyze_resume

# Create Blueprint
ai = Blueprint("ai", __name__)