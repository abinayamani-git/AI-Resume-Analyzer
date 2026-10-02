# AI Resume Analyzer

**Analyze your resume. Discover your strengths. Improve your career.**

A full-stack portfolio project that analyzes resumes (PDF/DOCX), estimates ATS-style compatibility, detects skills, compares against job descriptions, and presents insights in a professional SaaS-style dashboard.

> Scores are **estimated** for learning and portfolio use. They are **not** real ATS vendor scores and do **not** guarantee interviews or job offers.

---

## Problem statement

Job seekers struggle to understand how resumes look to automated screening and how well they match a role. This project demonstrates a practical AI/ML + full-stack architecture that:

1. Extracts resume text
2. Runs structured analysis (skills, sections, experience, projects)
3. Computes transparent estimated scores
4. Optionally matches a job description
5. Produces actionable recommendations and a downloadable PDF report

---

## Features

- Landing page, upload flow, results dashboard
- PDF & DOCX text extraction
- Modular skill catalog (easy to extend)
- Estimated ATS Compatibility Score (0–100) with breakdown
- Section scores with progress bars
- Detected / strong / missing skills
- Optional job-match percentage and keyword overlap
- Summary, project, and experience analysis
- AI-assisted recommendations (rule-based fallback today)
- PDF report download
- Works **without** an OpenAI API key
- LLM-ready `ai_service` architecture for future integration

---

## Technology stack

| Layer | Technology |
|-------|------------|
| Frontend | React, Vite, JavaScript, CSS3, Lucide React, React Router |
| Backend | Python, FastAPI, Uvicorn |
| Parsing | pypdf, python-docx |
| Reports | reportlab |
| Persistence | SQLite (modular; swappable for PostgreSQL) |
| AI layer | Rule-based fallback + hooks for future LLM APIs |

---

## Architecture

```
Browser (React)
    │  REST JSON
    ▼
FastAPI routes  →  resume_parser  →  ai_service
                         │               │
                         │         ┌─────┴──────┐
                         │         │ fallback   │ (future LLM)
                         │         └─────┬──────┘
                         │               ▼
                         │         analyzer + job_matcher
                         ▼
                   SQLite storage → PDF report
```

Key idea for interviews: **routes stay stable**; swap analysis providers inside `ai_service.py`.

---

## Project structure

```
ai-resume-analyzer/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/api.js
│   │   ├── context/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── .env.example
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routes/
│   │   ├── services/
│   │   ├── models/
│   │   └── utils/
│   ├── requirements.txt
│   └── .env.example
├── uploads/
├── README.md
└── .gitignore
```

---

## Installation

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm ([https://nodejs.org](https://nodejs.org))

### Backend setup

```bash
cd backend
python -m venv venv

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# macOS / Linux
# source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
# On macOS/Linux: cp .env.example .env
```

### Frontend setup

```bash
cd frontend
npm install
copy .env.example .env
# On macOS/Linux: cp .env.example .env
```

---

## Environment variables

### Frontend (`frontend/.env`)

```
VITE_API_URL=http://localhost:8000
```

### Backend (`backend/.env`)

```
HOST=0.0.0.0
PORT=8000
UPLOAD_DIR=../uploads
MAX_FILE_SIZE_MB=5
ALLOWED_EXTENSIONS=.pdf,.docx
AI_PROVIDER=fallback
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

Leave `OPENAI_API_KEY` empty to use the rule-based analyzer.

---

## How to run

Open **two terminals**.

### Start the backend

```bash
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)  
Health: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### Start the frontend

```bash
cd frontend
npm run dev
```

App: [http://localhost:5173](http://localhost:5173)

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/upload` | Upload PDF/DOCX resume |
| POST | `/api/analyze` | Analyze resume (+ optional job description) |
| POST | `/api/job-match` | Standalone job match |
| GET | `/api/report/{id}` | Download PDF report |

---

## Screenshots

> Add screenshots here after running locally:
> - Landing page
> - Upload page
> - Results dashboard
> - Job match section

---

## Future improvements

- Connect OpenAI / other LLM providers in `ai_service.py`
- PostgreSQL instead of SQLite
- User accounts and analysis history UI
- Better OCR for scanned PDFs
- Export to DOCX / shareable links
- Automated tests (pytest + React Testing Library)

---

## Learning outcomes

- Building a production-shaped FastAPI + React app
- File upload validation and document parsing
- Designing modular AI services with safe fallbacks
- Transparent scoring systems you can defend in interviews
- Clean frontend architecture (central API service, context, routes)

---

## Author

Built as a portfolio project for AI/ML, Python, GenAI, and software development roles.

---

## License

MIT — feel free to adapt for your own portfolio (do not claim real ATS certification).
