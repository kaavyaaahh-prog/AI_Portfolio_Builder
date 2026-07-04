"""
internship_service.py
-----------------------
Two jobs:

1. RULE-BASED ROLE RECOMMENDER (works offline, no API key needed)
   Looks at the skills pulled from the student's resume/portfolio and
   suggests matching internship/job titles using a keyword map.

2. REAL LIVE INTERNSHIP SEARCH (Adzuna Jobs API)
   Calls the free Adzuna API to fetch REAL, currently-open internship
   and job listings (title, company, location, salary, apply link,
   posted date) that match the recommended roles + location.

   Adzuna is a legitimate public job-search API with a free tier.
   Sign up at https://developer.adzuna.com/ to get an APP_ID/APP_KEY
   and put them in config.py. If no key is configured, this module
   simply returns an empty list + a flag so the route can show a
   friendly setup notice instead of crashing.
"""

import requests
from config import Config

# ------------------------------------------------------------------
# Keyword -> suggested role title map.
# This is intentionally simple and easy for a beginner to extend:
# just add more "keyword": ["Role A", "Role B"] entries.
# ------------------------------------------------------------------
SKILL_ROLE_MAP = {
    "power bi": ["Power BI Developer Intern", "Data Visualization Intern", "BI Analyst Intern"],
    "tableau": ["Tableau Developer Intern", "Data Visualization Intern", "BI Analyst Intern"],
    "excel": ["Data Analyst Intern", "Business Analyst Intern", "MIS Executive Intern"],
    "sql": ["SQL Developer Intern", "Data Analyst Intern", "Database Intern"],
    "python": ["Python Developer Intern", "Data Analyst Intern", "Automation Intern"],
    "java": ["Java Developer Intern", "Backend Developer Intern"],
    "javascript": ["Frontend Developer Intern", "Full Stack Developer Intern"],
    "react": ["React Developer Intern", "Frontend Developer Intern"],
    "node": ["Node.js Developer Intern", "Backend Developer Intern"],
    "html": ["Web Developer Intern", "Frontend Developer Intern"],
    "css": ["Web Developer Intern", "UI Developer Intern"],
    "machine learning": ["Machine Learning Intern", "AI Intern", "Data Science Intern"],
    "deep learning": ["Deep Learning Intern", "AI Intern"],
    "data science": ["Data Science Intern", "Data Analyst Intern"],
    "data analysis": ["Data Analyst Intern", "Business Analyst Intern"],
    "pandas": ["Data Analyst Intern", "Python Developer Intern"],
    "numpy": ["Data Analyst Intern", "Python Developer Intern"],
    "power query": ["Power BI Developer Intern", "Data Analyst Intern"],
    "dax": ["Power BI Developer Intern", "Data Visualization Intern"],
    "cloud": ["Cloud Support Intern", "DevOps Intern"],
    "aws": ["AWS Cloud Intern", "DevOps Intern"],
    "azure": ["Azure Cloud Intern", "Data Engineer Intern"],
    "networking": ["Network Support Intern", "IT Support Intern"],
    "cybersecurity": ["Cybersecurity Intern", "SOC Analyst Intern"],
    "digital marketing": ["Digital Marketing Intern", "SEO Intern"],
    "content writing": ["Content Writer Intern", "Digital Marketing Intern"],
    "communication": ["Business Analyst Intern", "HR Intern"],
    "c++": ["Software Developer Intern", "Embedded Systems Intern"],
    "c programming": ["Software Developer Intern"],
    "android": ["Android Developer Intern", "Mobile App Developer Intern"],
    "flutter": ["Flutter Developer Intern", "Mobile App Developer Intern"],
    "ui/ux": ["UI/UX Designer Intern", "Product Design Intern"],
    "figma": ["UI/UX Designer Intern"],
    "testing": ["QA Tester Intern", "Software Testing Intern"],
    "manual testing": ["QA Tester Intern"],
}

DEFAULT_ROLES = ["Data Analyst Intern", "Software Developer Intern", "Business Analyst Intern"]


def recommend_roles(skills: dict, limit: int = 6) -> list:
    """
    Takes the portfolio 'skills' dict:
      {"technical_skills": [...], "soft_skills": [...]}
    and returns a ranked, de-duplicated list of suggested role titles.
    Falls back to DEFAULT_ROLES if nothing matches.
    """
    technical = [s.lower().strip() for s in skills.get("technical_skills", []) if s]

    scored = {}
    for skill in technical:
        for keyword, roles in SKILL_ROLE_MAP.items():
            if keyword in skill or skill in keyword:
                for role in roles:
                    scored[role] = scored.get(role, 0) + 1

    if not scored:
        return DEFAULT_ROLES[:limit]

    # Highest matching skill-count first, keep original insertion order as tiebreaker
    ranked = sorted(scored.items(), key=lambda item: item[1], reverse=True)
    roles = [role for role, _count in ranked]
    return roles[:limit]


def _is_configured() -> bool:
    return bool(
        Config.ADZUNA_APP_ID
        and Config.ADZUNA_APP_KEY
        and "your_adzuna" not in Config.ADZUNA_APP_ID
        and "your_adzuna" not in Config.ADZUNA_APP_KEY
    )


def search_internships(role_query: str, location: str = "") -> dict:
    """
    Calls the Adzuna Jobs API and returns REAL, live internship/job
    listings that match `role_query` (e.g. "Data Analyst Intern") and
    `location` (e.g. "Coimbatore").

    Returns:
        {
          "configured": bool,   # False if no Adzuna API key was set
          "results": [ {title, company, location, salary, url,
                        posted, description}, ... ]
        }
    """
    if not _is_configured():
        return {"configured": False, "results": []}

    country = Config.ADZUNA_COUNTRY
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"

    params = {
        "app_id": Config.ADZUNA_APP_ID,
        "app_key": Config.ADZUNA_APP_KEY,
        "what": role_query,
        "where": location or Config.ADZUNA_DEFAULT_LOCATION,
        "results_per_page": Config.ADZUNA_RESULTS_PER_PAGE,
        "content-type": "application/json",
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[Internship Service Error] Adzuna request failed: {e}")
        return {"configured": True, "results": [], "error": str(e)}

    results = []
    for job in data.get("results", []):
        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")
        salary = None
        if salary_min and salary_max:
            salary = f"₹{int(salary_min):,} - ₹{int(salary_max):,} / year"
        elif salary_min:
            salary = f"From ₹{int(salary_min):,} / year"

        results.append({
            "title": job.get("title", "Untitled Role"),
            "company": (job.get("company") or {}).get("display_name", "Unknown Company"),
            "location": (job.get("location") or {}).get("display_name", location or "Not specified"),
            "salary": salary,
            "url": job.get("redirect_url", "#"),
            "posted": job.get("created", "")[:10],
            "description": (job.get("description", "") or "")[:220],
        })

    return {"configured": True, "results": results}
