# =============================================================================
# DEPLOYMENT & OPERATIONS GUIDE
# =============================================================================

## Digital Footprint Analyzer - Backend Deployment

This guide covers production deployment, environment variables, and troubleshooting for the OSINT backend.

---

## 1. Prerequisites
- Python 3.10+
- Node.js (for frontend)
- Playwright browsers: `python -m playwright install chromium`
- Docker (optional, for containerized deployment)

---

## 2. Environment Variables
Set these in your environment or a `.env` file:

| Variable                | Description                                 | Example                        |
|-------------------------|---------------------------------------------|---------------------------------|
| `OSINT_SESSION_DIR`     | Directory for session JSONs                 | `sessions`                      |
| `OSINT_BROWSER_HEADLESS`| Run Playwright headless (true/false)        | `true`                          |
| `OSINT_BROWSER_TIMEOUT` | Browser/page timeout (ms)                   | `20000`                         |
| `OSINT_RATE_LIMIT_DELAY`| Min delay between requests (s)               | `2`                             |
| `OSINT_MAX_RETRIES`     | Max retries for collection                  | `3`                             |
| `OSINT_RETRY_DELAY`     | Delay between retries (s)                    | `5`                             |
| `CORS_ORIGINS`          | Allowed frontend origins (comma-separated)   | `http://localhost:3000`         |
| `LOG_LEVEL`             | Logging level (`INFO`, `DEBUG`, etc.)       | `INFO`                          |

---

## 3. Running Locally

```sh
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers
python -m playwright install chromium

# 4. Start the backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 4. Docker Deployment

```sh
docker build -t digital-footprint-backend ./backend
# Or use docker-compose
docker-compose up --build
```

---

## 5. Health & Session Monitoring
- API root: `GET /` (shows API info)
- Health: `GET /api/health` (add if needed)
- Session status: `GET /api/osint/sessions/status`

---

## 6. Troubleshooting
- **Port in use**: Change `--port` or stop other processes.
- **Playwright errors**: Ensure browsers are installed and not blocked by antivirus.
- **Session expired**: Use the CLI or `/api/osint/sessions/validate` to check and refresh sessions.
- **Logging**: All logs are structured JSON. Set `LOG_LEVEL=DEBUG` for verbose output.

---

## 7. Updating Sessions
- Use the CLI tool in `backend/app/osint/tools/create_session.py` to create or refresh OSINT platform sessions.

---

## 8. Production Tips
- Use a process manager (e.g., Gunicorn, Supervisor) for resilience.
- Set strong OSINT account passwords and rotate regularly.
- Monitor logs for anti-bot blocks or session expiry.
- Secure session directory permissions.

---

## 9. Useful Commands

```sh
# Run all backend tests
.venv\Scripts\activate
cd backend
pytest tests

# Install Playwright browsers (if missing)
python -m playwright install chromium
```

---

For more, see the code comments and API docs at `/docs` after starting the backend.
