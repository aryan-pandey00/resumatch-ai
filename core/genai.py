import requests
import json
import re
import time
import os
import streamlit as st

# MODELS
PRIMARY_MODEL = "qwen/qwen3-next-80b-a3b-instruct"
BACKUP_MODEL = "meta-llama/llama-3-8b-instruct"

URL = "https://openrouter.ai/api/v1/chat/completions"

# -------------------------------------------------------
# KEY LOADED LAZILY — never at import time
# This prevents the homepage crash/refresh loop on deploy
# -------------------------------------------------------
_API_KEY = None

def get_api_key():
    global _API_KEY
    if _API_KEY:
        return _API_KEY
    _API_KEY = os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY", None)
    if not _API_KEY:
        st.error("⚠️ API key not found. Set OPENROUTER_API_KEY in Streamlit secrets.")
        st.stop()
    return _API_KEY


def get_headers():
    return {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://resumatch-ai.streamlit.app",  # ← update to your actual URL
        "X-Title": "Resume AI Product"
    }


# UNIVERSAL API CALL

def call_model(prompt, max_tokens=400):

    for model in [PRIMARY_MODEL, BACKUP_MODEL]:
        try:
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4,
                "max_tokens": max_tokens
            }

            response = requests.post(URL, headers=get_headers(), json=data, timeout=20)
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()

            return content

        except Exception as e:
            print(f"⚠️ Model {model} failed:", e)
            time.sleep(1)

    return None


# JD MATCHER

def generate_suggestions(resume_text, missing_skills):

    resume_text = resume_text[:1000]
    missing_skills = missing_skills[:6]

    prompt = f"""
You are a professional resume reviewer.

STRICT RULES:
- Maximum 3 bullet points per section
- Each bullet must be short (8–12 words)
- No extra text, no explanation
- Follow format EXACTLY

OUTPUT FORMAT:

### Improvements
- point
- point
- point

### Skills to Add
- skill
- skill
- skill

### Resume Tips
- tip
- tip
- tip

DATA:

Resume:
{resume_text}

Missing Skills:
{", ".join(missing_skills)}
"""

    content = call_model(prompt, max_tokens=250)

    if content:
        return content

    return "⚠️ Could not generate suggestions (fallback triggered)"


# RESUME BUILDER

def generate_resume_content(ai_input):

    skills = ai_input.get("skills", [])[:6]
    projects = ai_input.get("projects", [])[:3]
    experience = ai_input.get("experience", [])[:2]

    prompt = f"""
You are a professional resume writer.

STRICT RULES:
- Return ONLY valid JSON
- No explanation, no markdown
- Summary must be 50–70 words
- Projects must have EXACTLY 3 bullets each
- Each bullet must be 12–18 words
- No repeated phrases
- Each project must be unique

FORMAT:

{{
  "summary": "text",
  "projects": [
    "bullet1\\nbullet2\\nbullet3",
    "bullet1\\nbullet2\\nbullet3"
  ]
}}

DATA:

Skills: {", ".join(skills)}

Projects:
{json.dumps(projects)}

Experience:
{json.dumps(experience)}
"""

    content = call_model(prompt, max_tokens=500)

    if not content:
        return None

    # CLEAN MARKDOWN
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]

    # JSON EXTRACTION
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if not match:
        print("❌ JSON not found")
        return None

    try:
        parsed = json.loads(match.group())
    except Exception:
        print("❌ JSON parsing failed")
        return None

    # VALIDATION
    if (
        not isinstance(parsed, dict) or
        "summary" not in parsed or
        "projects" not in parsed or
        not isinstance(parsed["projects"], list)
    ):
        return None

    return parsed


# ATS AI SUGGESTIONS + JOB ROLES

def generate_ats_ai_output(ai_input):

    prompt = f"""
You are a resume expert and career advisor.

DATA:
ATS Score: {ai_input['score']}
Skills: {", ".join(ai_input['skills'])}
Issues: {", ".join(ai_input['issues'])}
Missing Sections: {", ".join(ai_input['missing'])}

TASK:
1. Give 5 unique resume improvement suggestions
2. Suggest 5 relevant job roles

RULES:
- Keep each suggestion under 12 words
- No repetition
- Job roles must match skills
- Be realistic (e.g., Data Analyst, Backend Developer)

RETURN ONLY JSON:

{{
  "suggestions": [],
  "job_roles": []
}}
"""

    content = call_model(prompt, max_tokens=300)

    if not content:
        return None

    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]

    match = re.search(r"\{.*\}", content, re.DOTALL)
    if not match:
        return None

    try:
        parsed = json.loads(match.group())
    except Exception:
        return None

    if (
        not isinstance(parsed, dict) or
        "suggestions" not in parsed or
        "job_roles" not in parsed
    ):
        return None

    return parsed


def fallback_ats_output(ai_input):

    skills = [s.lower() for s in ai_input["skills"]]
    suggestions = ai_input["issues"][:5]

    role_scores = {}

    def add_score(role, score):
        role_scores[role] = role_scores.get(role, 0) + score

    def has(skill):
        return any(skill in s for s in skills)

    def has_any(*args):
        return any(has(a) for a in args)

    if has("python"):
        add_score("Data Analyst", 1)
    if has("sql"):
        add_score("Data Analyst", 2)
    if has_any("pandas", "numpy"):
        add_score("Data Analyst", 2)

    if has("python") and has_any("machine learning", "sklearn", "tensorflow"):
        add_score("Machine Learning Engineer", 3)

    if has("python"):
        add_score("Backend Developer", 1)
    if has_any("flask", "django", "api"):
        add_score("Backend Developer", 2)

    if has("java"):
        add_score("Backend Developer", 1)
    if has("spring"):
        add_score("Backend Developer", 2)

    if has_any("javascript", "html", "css"):
        add_score("Frontend Developer", 1)
    if has("react"):
        add_score("Frontend Developer", 2)

    if has_any("react", "javascript") and has_any("node", "express", "django", "flask"):
        add_score("Full Stack Developer", 3)

    if has("kotlin") or has("android"):
        add_score("Android Developer", 3)

    sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)

    roles = [role for role, score in sorted_roles if score >= 2]

    if not roles:
        if len(skills) >= 2:
            roles = ["Software Developer"]
        else:
            roles = ["Entry-level Software Role"]

    return {
        "suggestions": suggestions,
        "job_roles": roles[:5]
    }