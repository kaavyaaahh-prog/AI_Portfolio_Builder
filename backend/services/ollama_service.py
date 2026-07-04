"""
ollama_service.py
-------------------
Handles all communication with the local Ollama AI model (Llama3.1).
Two jobs:
  1. Turn resume text into structured portfolio JSON.
  2. Turn resume text into an ATS (Applicant Tracking System) score report.

Beginners: Ollama must be running locally (ollama serve) with the
llama3.1 model pulled (ollama pull llama3.1) for this to work.
"""

import json
import requests
from config import Config


def _call_ollama(prompt: str) -> str:
    """
    Sends a prompt to the local Ollama HTTP API and returns the raw
    text response. Returns an empty string if anything goes wrong.
    """
    payload = {
        "model": Config.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(Config.OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except Exception as e:
        print(f"[Ollama Error] Request failed: {e}")
        return ""


def _extract_json(raw_text: str) -> dict:
    """
    AI models sometimes wrap JSON with extra text or markdown fences.
    This pulls out just the { ... } block and parses it safely.
    """
    if not raw_text:
        return {}

    start = raw_text.find("{")
    end = raw_text.rfind("}")

    if start == -1 or end == -1:
        return {}

    json_chunk = raw_text[start:end + 1]

    try:
        return json.loads(json_chunk)
    except json.JSONDecodeError as e:
        print(f"[Ollama Error] Could not parse AI JSON: {e}")
        return {}


def generate_portfolio_from_resume(resume_text: str) -> dict:
    """
    Sends the resume text to Ollama and asks it to extract structured
    portfolio fields. Returns a Python dict (empty dict on failure).
    """
    prompt = f"""
Read this resume carefully and extract the following details.

Resume:
\"\"\"{resume_text}\"\"\"

Return ONLY valid JSON (no explanation, no markdown) with exactly these keys:
{{
  "full_name": "",
  "professional_title": "",
  "about_me": "",
  "career_objective": "",
  "education": [ {{"degree": "", "institution": "", "year": ""}} ],
  "skills": {{"technical_skills": [], "soft_skills": []}},
  "projects": [ {{"title": "", "description": ""}} ],
  "certificates": [],
  "achievements": [],
  "github": "",
  "linkedin": "",
  "email": "",
  "phone": ""
}}

If a field is not found in the resume, leave it as an empty string, empty list, or empty object.
Return only the JSON object, nothing else.
"""
    raw_response = _call_ollama(prompt)
    return _extract_json(raw_response)


def generate_ats_score(resume_text: str) -> dict:
    """
    Sends the resume text to Ollama and asks it to score it like an
    Applicant Tracking System would. Returns a Python dict.
    """
    prompt = f"""
Analyze this resume like an Applicant Tracking System (ATS) would.

Resume:
\"\"\"{resume_text}\"\"\"

Evaluate: resume structure, summary, skills, projects, keywords,
formatting, certificates, education and experience.

Return ONLY valid JSON (no explanation, no markdown) with exactly these keys:
{{
  "overall_score": 0,
  "strengths": [],
  "weaknesses": [],
  "suggestions": [],
  "missing_keywords": []
}}

overall_score must be a whole number between 0 and 100.
Return only the JSON object, nothing else.
"""
    raw_response = _call_ollama(prompt)
    result = _extract_json(raw_response)

    # Provide safe defaults if the AI response was incomplete
    result.setdefault("overall_score", 0)
    result.setdefault("strengths", [])
    result.setdefault("weaknesses", [])
    result.setdefault("suggestions", [])
    result.setdefault("missing_keywords", [])
    return result
