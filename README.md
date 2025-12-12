
# 🔍 Digital Footprint Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)

A **Sri Lanka-focused OSINT (Open Source Intelligence) web application** for privacy awareness, impersonation detection, and risk assessment across social media platforms.

---

## 🌟 Key Features

- **Playwright-based OSINT backend**: Automated, authenticated scraping for Instagram, Facebook, LinkedIn, and X (Twitter) using persistent sessions.
- **Advanced anti-bot/stealth**: User-agent rotation, stealth patches, proxy support, and randomized delays for robust scraping.
- **Session management**: Persistent, health-checked browser sessions for each platform, with API endpoints for validation and monitoring.
- **PII & NER extraction**: Detect emails, Sri Lankan phone numbers, URLs, mentions, names, locations, and organizations in any text.
- **Username analysis**: Generate platform URLs, impersonation variations, and pattern analysis for usernames.
- **Risk scoring**: Privacy risk assessment and actionable recommendations.
- **Structured logging**: JSON logs for easy monitoring and production readiness.
- **Internationalization**: English and Sinhala UI support.
- **Docker & deployment ready**: Full Docker, Compose, and environment variable support.

---

## 🏗️ Architecture Overview

**Backend**: Python 3.10+, FastAPI, Playwright, spaCy, Pydantic, Uvicorn

**Frontend**: React 18, Tailwind CSS, Context API, i18n

**Session Management**: JSON-based Playwright sessions, validated and monitored via API

**Anti-bot/Stealth**: User-agent rotation, stealth scripts, proxy, delays (see `BaseCollector`)

**Logging**: Structured JSON logging via `python-json-logger`

---

## 📁 Project Structure (Key Parts)

```
DigitalFootprintAnalyzer/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app entry
│   │   ├── api/routes/osint.py   # OSINT endpoints
│   │   ├── osint/collectors/     # Playwright collectors (per platform)
│   │   ├── osint/session_manager.py # Session management
│   │   ├── osint/orchestrator.py # Scraping/analysis pipeline
│   │   ├── services/             # NLP, PII, NER, correlation
│   │   ├── core/logging_config.py# Structured logging setup
│   │   └── ...
│   ├── tests/                    # Unit/integration tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── DEPLOYMENT.md             # Deployment & env guide
├── frontend/                     # React app
│   └── ...
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quickstart

### 1. Docker (Recommended)

```sh
git clone https://github.com/justdsn/DigitalFootprintAnalyzer.git
cd DigitalFootprintAnalyzer
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 2. Manual Backend Setup

```sh
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m playwright install chromium
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 🔑 Environment Variables (see DEPLOYMENT.md)

| Variable                | Description                                 |
|-------------------------|---------------------------------------------|
| `OSINT_SESSION_DIR`     | Directory for session JSONs                 |
| `OSINT_BROWSER_HEADLESS`| Run Playwright headless (true/false)        |
| `OSINT_BROWSER_TIMEOUT` | Browser/page timeout (ms)                   |
| `OSINT_RATE_LIMIT_DELAY`| Min delay between requests (s)               |
| `OSINT_MAX_RETRIES`     | Max retries for collection                  |
| `OSINT_RETRY_DELAY`     | Delay between retries (s)                    |
| `CORS_ORIGINS`          | Allowed frontend origins (comma-separated)   |
| `LOG_LEVEL`             | Logging level (`INFO`, `DEBUG`, etc.)       |

---

## 🛡️ API Highlights

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/osint/analyze` | Main OSINT analysis (scraping + NLP) |
| `GET`  | `/api/osint/sessions/status` | Session health for all platforms |
| `POST` | `/api/osint/sessions/validate` | Validate a specific session |

See `/docs` for full OpenAPI documentation after starting the backend.

---

## 🧪 Testing

```sh
cd backend
.venv\Scripts\activate
pytest tests/
```

---

## 📝 Deployment & Operations

See `backend/DEPLOYMENT.md` for full deployment, environment, and troubleshooting instructions.

---

## 📅 Roadmap

- [x] Playwright-based backend collectors (all platforms)
- [x] Session management & health monitoring
- [x] Anti-bot/stealth scraping
- [x] Structured logging
- [x] Full test coverage
- [x] Docker/Compose deployment
- [ ] Data breach integration
- [ ] User accounts & saved analyses
- [ ] Mobile app & Tamil support

---

## ⚠️ Disclaimer

This tool is for privacy awareness and educational use only. It analyzes only publicly available information. Use responsibly and in compliance with all laws and platform terms.

---

<p align="center">🇱🇰</p>

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | Modern, high-performance Python web framework |
| **Python 3.11+** | Programming language |
| **spaCy** | Natural Language Processing and NER |
| **Pydantic** | Data validation and settings management |
| **Uvicorn** | ASGI server |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI component library |
| **React Router** | Client-side routing |
| **Tailwind CSS** | Utility-first CSS framework |
| **Context API** | State management for i18n |

### Chrome Extension
| Technology | Purpose |
|------------|---------|
| **Manifest V3** | Chrome Extension framework |
| **Service Worker** | Background processing and orchestration |
| **Content Scripts** | Social media profile data extraction |
| **External Messaging** | Web app ↔ extension communication |

### DevOps
| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **Docker Compose** | Multi-container orchestration |
| **nginx** | Frontend production server |

## Project Structure

```
DigitalFootprintAnalyzer/
├── backend/
│   ├── app/
│   │   ├── __init__.py           # Package initialization
│   │   ├── main.py               # FastAPI application entry point
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py         # API endpoint definitions
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py         # Application configuration
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── pii_extractor.py  # PII extraction with regex
│   │   │   ├── ner_engine.py     # spaCy NER with Sri Lankan context
│   │   │   └── username_analyzer.py # Username analysis service
│   │   └── models/
│   │       ├── __init__.py
│   │       └── schemas.py        # Pydantic request/response models
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_pii_extractor.py
│   │   └── test_username_analyzer.py
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx        # Navigation component
│   │   │   ├── Footer.jsx        # Footer component
│   │   │   ├── InputForm.jsx     # Analysis input form
│   │   │   ├── ResultCard.jsx    # Result display cards
│   │   │   ├── RiskIndicator.jsx # Visual risk score
│   │   │   └── LanguageToggle.jsx # Language switcher
│   │   ├── pages/
│   │   │   ├── HomePage.jsx      # Landing page
│   │   │   ├── AnalyzePage.jsx   # Analysis form page
│   │   │   └── ResultsPage.jsx   # Results display page
│   │   ├── services/
│   │   │   └── api.js            # API service layer
│   │   ├── i18n/
│   │   │   ├── en.json           # English translations
│   │   │   └── si.json           # Sinhala translations
│   │   ├── context/
│   │   │   └── LanguageContext.jsx # i18n context provider
│   │   ├── App.jsx               # Root component
│   │   ├── index.js              # Application entry point
│   │   └── index.css             # Global styles with Tailwind
│   ├── package.json
│   ├── tailwind.config.js
│   ├── Dockerfile
│   ├── nginx.conf
│   └── .env.example
├── docker-compose.yml            # Docker orchestration
├── extension/                    # Chrome extension for deep scanning
│   ├── manifest.json            # Extension manifest
│   ├── background/
│   │   └── service-worker.js    # Background service worker
│   ├── content/
│   │   ├── shared.js            # Shared utilities
│   │   ├── facebook.js          # Facebook scraper
│   │   ├── instagram.js         # Instagram scraper
│   │   ├── linkedin.js          # LinkedIn scraper
│   │   └── x.js                 # X (Twitter) scraper
│   ├── popup/
│   │   ├── popup.html           # Extension popup UI
│   │   ├── popup.js             # Popup logic
│   │   └── popup.css            # Popup styles
│   ├── lib/
│   │   └── api.js               # API communication helper
│   └── icons/
└── README.md                     # This file
```

## 🚀 Getting Started

### Prerequisites

- **Docker & Docker Compose** (recommended) OR
- **Python 3.11+** and **Node.js 18+** (for manual setup)

### Option 1: Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/DigitalFootprintAnalyzer.git
   cd DigitalFootprintAnalyzer
   ```

2. **Start the services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Create environment file**
   ```bash
   cp .env.example .env
   ```

6. **Run the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create environment file**
   ```bash
   cp .env.example .env
   ```

4. **Start development server**
   ```bash
   npm start
   ```

#### Chrome Extension Setup (For Deep Scan)

1. **Open Chrome Extensions**
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right corner)

2. **Load the extension**
   - Click "Load unpacked"
   - Select the `extension/` folder from the project directory

3. **Get Extension ID**
   - After loading, the extension will appear in your extensions list
   - Copy the Extension ID (32-character string displayed under the extension name)
   - Or click the extension icon and copy the ID from the popup

4. **Connect to Web App**
   - Open the web app at http://localhost:3000
   - Go to the Analyze page
   - Select "Deep Scan" mode
   - Click "Setup Extension" when prompted
   - Paste the Extension ID and click "Connect Extension"

5. **Start Deep Scanning**
   - Once connected, you can perform deep scans directly from the web app
   - The extension will automatically scrape profiles across platforms
   - Results are sent back to the web app and displayed automatically

> **Note:** The extension requires you to be logged into the social media platforms for deep scanning to work properly. Make sure you're logged into Facebook, Instagram, LinkedIn, and X (Twitter) in Chrome before starting a deep scan.

## API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/analyze` | Main analysis endpoint |
| `POST` | `/api/extract-pii` | Extract PII from text |
| `POST` | `/api/analyze-username` | Analyze username patterns |

### Main Analysis Request

```json
POST /api/analyze
{
  "username": "john_doe",     // Required
  "email": "john@example.com", // Optional
  "phone": "0771234567",       // Optional - Sri Lankan formats
  "name": "John Perera"        // Optional
}
```

### Response Example

```json
{
  "username": "john_doe",
  "platform_urls": {
    "facebook": {
      "name": "Facebook",
      "url": "https://www.facebook.com/john_doe",
      "icon": "facebook"
    },
    // ... other platforms
  },
  "variations": ["john_doe", "johndoe", "john.doe", ...],
  "pattern_analysis": {
    "length": 8,
    "has_numbers": false,
    "has_underscores": true,
    "number_density": 0.0,
    "has_suspicious_patterns": false
  },
  "extracted_pii": {
    "emails": ["john@example.com"],
    "phones": ["+94771234567"],
    "urls": [],
    "mentions": []
  },
  "ner_entities": {
    "persons": ["John Perera"],
    "locations": [],
    "organizations": []
  },
  "risk_score": 45,
  "risk_level": "medium",
  "recommendations": [
    "Review privacy settings on all social media platforms",
    "Check if your email has been involved in data breaches"
  ],
  "processing_time_ms": 127.5
}
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Test Coverage

```bash
pytest tests/ -v --cov=app
```

## Design System

### Colors
- **Primary Blues**: `#1e40af`, `#3b82f6` - Main brand colors
- **Accent Teals**: `#0d9488`, `#14b8a6` - Secondary accent colors
- **Risk Colors**: Green (low), Amber (medium), Red (high)

### Typography
- **Display Font**: Plus Jakarta Sans
- **Body Font**: Inter

## Roadmap

### Phase 1 (Current) ✅
- [x] Backend API with FastAPI
- [x] PII extraction service
- [x] NER engine with Sri Lankan context
- [x] Username analyzer service
- [x] React frontend with Tailwind CSS
- [x] i18n support (English/Sinhala)
- [x] Docker configuration

### Phase 2 (Planned)
- [ ] Active profile checking via web scraping
- [ ] Data breach checking integration
- [ ] Extended platform support
- [ ] User accounts and saved analyses

### Phase 3 (Future)
- [ ] Machine learning for impersonation detection
- [x] Browser extension for deep scanning
- [ ] Mobile application
- [ ] Tamil language support

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [spaCy](https://spacy.io/) for NLP capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://reactjs.org/) for the frontend framework
- [Tailwind CSS](https://tailwindcss.com/) for styling

## ⚠️ Disclaimer

This tool is designed for personal privacy awareness and educational purposes. It analyzes only publicly available information. Users are responsible for ensuring their use of this tool complies with all applicable laws and platform terms of service.

---

<p align="center">🇱🇰</p>
