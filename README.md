# AI Portfolio Builder

A beginner-friendly full-stack web app where students upload a resume (PDF),
AI (Llama3.1 via Ollama) extracts the details and generates a portfolio,
and students can preview, edit, save, and publish it — plus get an ATS
resume score.

Built with **Flask + MySQL + Bootstrap 5 + vanilla JS**, using a simple
**MVC folder structure**. No React/Angular/Vue.

---

## 1. Project Structure

```
AI_Portfolio_Builder/
│
├── frontend/                  # Views (HTML templates + static assets)
│   ├── base.html              # Shared layout (navbar/footer)
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── forgot_password.html
│   ├── verify_otp.html
│   ├── reset_password.html
│   ├── dashboard.html
│   ├── upload_resume.html
│   ├── portfolio_preview.html
│   ├── edit_portfolio.html
│   ├── ats_score.html
│   ├── css/style.css
│   ├── js/app.js
│   └── images/
│
├── backend/                   # Controller + Model logic
│   ├── app.py                 # App entry point
│   ├── config.py              # All settings (DB, upload, Ollama)
│   ├── database.py            # MySQL connection helper
│   ├── routes/                # Controllers (Blueprints)
│   │   ├── auth.py            # Register/Login/OTP/Dashboard
│   │   ├── resume.py          # Resume upload
│   │   ├── portfolio.py       # Generate/Preview/Edit/Publish
│   │   └── ats.py             # ATS score
│   └── services/               # Business logic (Model helpers)
│       ├── auth_service.py    # bcrypt + OTP helpers
│       ├── pdf_parser.py      # PyMuPDF text extraction
│       └── ollama_service.py  # Ollama AI calls
│
├── database/
│   └── schema.sql             # MySQL table definitions
│
├── uploads/resumes/           # Uploaded PDF resumes are stored here
├── requirements.txt
└── README.md
```

---

## 2. Prerequisites

- Python 3.10+
- MySQL Server running locally
- [Ollama](https://ollama.com) installed locally, with the model pulled:
  ```bash
  ollama pull llama3.1
  ollama serve
  ```

---

## 3. Setup Steps

### Step 1 — Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Create the MySQL database
```bash
mysql -u root -p < database/schema.sql
```

### Step 4 — Configure your database password
Open `backend/config.py` and set your MySQL password:
```python
MYSQL_PASSWORD = "your_mysql_password"
```

### Step 5 — Run the app
```bash
cd backend
python app.py
```

Open your browser at: **http://localhost:5000**

---

## 4. How It Works (Module by Module)

1. **Register / Login** — bcrypt-hashed passwords, MySQL-backed accounts.
2. **Forgot Password** — generates a 6-digit OTP (printed to the console
   in development mode instead of a real email), stored with a 5-minute
   expiry.
3. **Dashboard** — quick links to Upload Resume, My Portfolio, ATS Score,
   and Published Portfolio status.
4. **Upload Resume** — accepts PDF only (max 5 MB), saved under
   `uploads/resumes/`.
5. **Text Extraction** — `PyMuPDF` reads the PDF and stores the plain text
   in MySQL.
6. **AI Portfolio Generation** — the resume text is sent to the local
   Ollama `llama3.1` model with a prompt asking for structured JSON
   (name, title, about, education, skills, projects, etc.).
7. **Preview / Edit / Save / Publish** — students can review the
   AI-generated content, tweak it, save it as a draft, then publish it to
   get a public link: `http://localhost:5000/portfolio/<id>`.
8. **ATS Resume Score** — the resume text is sent to Ollama again with a
   different prompt that scores it like an Applicant Tracking System and
   returns strengths, weaknesses, suggestions and missing keywords.

---

## 5. Notes for Beginners

- All AI calls happen inside `backend/services/ollama_service.py` — read
  through it to see exactly how the prompt is built and how the JSON
  response is parsed.
- All database queries go through the single helper function
  `run_query()` in `backend/database.py`, so you don't need to repeat
  connect/cursor/close code everywhere.
- Every route file inside `backend/routes/` is a **Flask Blueprint** —
  a way to keep related pages/URLs grouped together in their own file.
- In production, always change `SECRET_KEY` in `config.py` and connect
  to a real email service instead of printing the OTP to the console.
