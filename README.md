# Digital Footprint Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)

A **Sri Lanka-focused OSINT (Open Source Intelligence) solution** for privacy awareness, impersonation detection, and risk assessment across social media.

---

## Key Features

- **Automated Social Media OSINT**: Authenticated scraping for Instagram, Facebook, LinkedIn, and X (Twitter) via Playwright.
- **Advanced Anti-bot**: User-agent rotation, stealth patches, proxy support, and request randomization.
- **Session Management**: Persistent, API-validated sessions for each platform.
- **Personal Data Extraction**: Accurate detection of emails, Sri Lankan mobile numbers, URLs, names, etc.
- **Username Analysis & Risk Scoring**: Pattern analysis with privacy recommendations.
- **Internationalization**: English and Sinhala UI.
- **Production-ready**: Docker, Compose, environment configs, structured logging.

---

## Architecture & Tech Stack

- **Backend**: Python 3.10+, FastAPI, Playwright, spaCy, Pydantic, Uvicorn, python-json-logger
- **Frontend**: React 18, Tailwind CSS, Context API, i18n, React Router
- **Chrome Extension**: Manifest V3, Service Worker, Content Scripts (optional, see `/extension`)
- **DevOps**: Docker, Compose, nginx

---

## Getting Started

### Docker (Recommended)
```sh
git clone https://github.com/justdsn/DigitalFootprintAnalyzer.git
cd DigitalFootprintAnalyzer
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

**Backend**
```sh
cd backend
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend**
```sh
cd frontend
npm install
npm start
```

---

## Environment Variables

| Variable                  | Description                           |
|---------------------------|---------------------------------------|
| `OSINT_SESSION_DIR`       | Directory for session JSONs           |
| `OSINT_BROWSER_HEADLESS`  | Playwright headless mode (true/false) |
| `OSINT_BROWSER_TIMEOUT`   | Browser/page timeout (ms)             |
| `OSINT_RATE_LIMIT_DELAY`  | Delay between requests (s)            |
| `OSINT_MAX_RETRIES`       | Max retries for collection            |
| `CORS_ORIGINS`            | Allowed frontend origins              |
| `LOG_LEVEL`               | Logging level                         |

See `backend/DEPLOYMENT.md` for details.

---

## API Overview

- `POST /api/osint/analyze` — Main OSINT analysis
- `GET /api/osint/sessions/status` — Session status summary
- `POST /api/osint/sessions/validate` — Validate a specific session

See full documentation under `/docs` after backend startup.

---

## Testing

```sh
cd backend
.venv/Scripts/activate
pytest tests/
```
---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file.

---

## Acknowledgments

- [spaCy](https://spacy.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)

---

## ⚠️Disclaimer

This tool is for privacy awareness and educational purposes only. It analyzes only publicly available information. Use responsibly and comply with all applicable laws and platform terms.

<p align="center">🇱🇰</p>
