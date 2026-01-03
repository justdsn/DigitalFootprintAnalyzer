# Digital Footprint Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Playwright](https://img.shields.io/badge/Playwright-1.57+-blue.svg)](https://playwright.dev/)

A **comprehensive OSINT (Open Source Intelligence) platform** for digital footprint analysis, privacy awareness, impersonation detection, and risk assessment across social media platforms.

---

## ✨ Key Features

### 🔍 Multi-Mode Scanning
- **Light Scan**: Fast Google Dorking-based profile discovery (no authentication required)
- **Deep Scan**: Comprehensive OSINT analysis with authenticated platform scraping via Playwright
- **Direct Backend OSINT**: Full name search support with intelligent platform-specific strategies

### 🎯 Advanced OSINT Capabilities
- **Automated Social Media Scraping**: Instagram, Facebook, LinkedIn, and X (Twitter)
- **Intelligent Search Strategy**: 
  - Direct URL navigation for usernames
  - In-app search functionality for full names (Instagram)
  - Search URL generation for other platforms
- **Session Management**: Persistent authenticated sessions with validity checking
- **Anti-Bot Protection**: User-agent rotation, stealth patches, request randomization

### 🛡️ Privacy & Security Analysis
- **PII Extraction**: Detects emails, phone numbers (Sri Lankan format), URLs, names, locations
- **Risk Scoring**: Comprehensive risk assessment based on exposure levels
- **Impersonation Detection**: Cross-platform profile correlation and analysis
- **NER (Named Entity Recognition)**: Intelligent entity extraction using spaCy

### 🌐 Internationalization
- **Multi-language UI**: English and Sinhala support
- **Transliteration**: Sinhala-to-English username generation

### 📊 Reporting
- **PDF Report Generation**: Comprehensive downloadable reports
- **Real-time Analysis**: Live results as data is collected

---

## 🏗️ Architecture & Tech Stack

### Backend
- **Framework**: FastAPI 0.109+
- **Python**: 3.11.9 (required for Playwright compatibility)
- **Browser Automation**: Playwright 1.57+, Playwright-stealth
- **NLP**: spaCy (en_core_web_sm)
- **Data Validation**: Pydantic
- **Server**: Uvicorn (ASGI)
- **Logging**: python-json-logger

### Frontend
- **Framework**: React 18
- **Styling**: Tailwind CSS
- **State Management**: Context API
- **Routing**: React Router v6
- **Internationalization**: i18next

### DevOps
- **Containerization**: Docker, Docker Compose
- **Web Server**: nginx
- **Environment**: .env configuration

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.11.x** (Playwright does not officially support Python 3.13)
- **Node.js 18+** and npm
- **Git**
- **Docker** (recommended) or manual setup

### 🐳 Docker Setup (Recommended)
```sh
git clone https://github.com/justdsn/DigitalFootprintAnalyzer.git
cd DigitalFootprintAnalyzer
docker-compose up --build
```

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 🔧 Manual Setup

#### Backend Setup
```sh
cd backend

# Create virtual environment with Python 3.11
python3.11 -m venv .venv311

# Activate virtual environment
# Windows:
.venv311\Scripts\activate
# Linux/Mac:
source .venv311/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Download spaCy model
python -m spacy download en_core_web_sm

# Run backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```sh
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at http://localhost:3000

---

## 🔌 API Reference

All endpoints are prefixed with `/api/`. Full interactive documentation available at http://localhost:8000/docs.

### Core Analysis Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analyze` | POST | Main text analysis with PII detection and risk scoring |
| `/api/extract-pii` | POST | Extract PII (emails, phones, names, locations) from text |
| `/api/analyze-username` | POST | Analyze username patterns and security |

### OSINT Scan Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/light-scan` | POST | Google Dorking-based profile discovery |
| `/api/deep-scan/direct` | POST | **Backend OSINT deep scan** (supports usernames and full names) |
| `/api/deep-scan/analyze` | POST | Analyze deep scan results for impersonation |
| `/api/full-scan` | POST | Combined light + deep + analysis scan |
| `/api/exposure-scan` | POST | Analyze PII exposure across platforms |
| `/api/scan` | POST | Flexible scan with configurable options |

### Configuration Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/scan-options` | GET | Get available scan types and options |
| `/api/health` | GET | Health check endpoint |

### Deep Scan Features
- **Usernames**: Direct URL navigation to profiles
- **Full Names**: Intelligent search-based collection with:
  - **Instagram**: In-app search with enhanced selectors (10+ fallback strategies including keyboard shortcuts)
  - **Facebook/LinkedIn/X**: Search URL generation
- **Session Validation**: Automatic session health checks before scraping
- **Anti-Bot Protection**: Playwright-stealth, user-agent rotation, randomized delays

**Example Deep Scan Request:**
```json
{
  "identifier": "cristiano ronaldo",
  "identifier_type": "name",
  "platforms": ["instagram"]
}
```

---

## 📁 Project Structure

```
DigitalFootprintAnalyzer/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   ├── routes.py      # Main endpoints
│   │   │   └── routes/        # Additional route modules
│   │   ├── core/              # Configuration and logging
│   │   ├── models/            # Pydantic schemas
│   │   ├── osint/             # OSINT engine
│   │   │   ├── collectors/    # Platform-specific scrapers
│   │   │   ├── discovery/     # URL generation
│   │   │   ├── parsers/       # Data extraction
│   │   │   ├── sessions/      # Session management
│   │   │   ├── tools/         # Utility functions
│   │   │   ├── orchestrator.py # OSINT coordinator
│   │   │   └── session_manager.py
│   │   └── services/          # Business logic
│   │       ├── correlation/   # Cross-platform analysis
│   │       ├── report/        # PDF generation
│   │       ├── scan/          # Scan strategies
│   │       ├── social/        # Social media utilities
│   │       └── transliteration/
│   ├── tests/                 # Unit and integration tests
│   ├── requirements.txt       # Python dependencies
│   ├── runtime.txt            # Python version (3.11.9)
│   └── Dockerfile
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── context/           # React Context
│   │   ├── services/          # API clients
│   │   ├── utils/             # Utilities
│   │   └── i18n/              # Translations
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── extension/                 # Chrome extension (optional)
│   ├── manifest.json
│   ├── background/
│   ├── content/
│   └── popup/
├── docker-compose.yml
└── README.md
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OSINT_SESSION_DIR` | Directory for session JSONs | `backend/app/osint/sessions` |
| `OSINT_BROWSER_HEADLESS` | Playwright headless mode | `true` |
| `OSINT_BROWSER_TIMEOUT` | Browser/page timeout (ms) | `30000` |
| `OSINT_RATE_LIMIT_DELAY` | Delay between requests (s) | `2` |
| `OSINT_MAX_RETRIES` | Max retries for collection | `3` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:3000` |
| `LOG_LEVEL` | Logging level | `INFO` |

See [backend/DEPLOYMENT.md](backend/DEPLOYMENT.md) for production configuration details.

### Session Management

Authenticated sessions are stored in `backend/app/osint/sessions/`:
- `instagram_session.json`
- `facebook_session.json`
- `linkedin_session.json`
- `x_session.json`

Sessions are validated before each scan and refreshed automatically when expired.

---

## 🧪 Testing

```sh
cd backend
.venv311\Scripts\activate  # or source .venv311/bin/activate on Linux/Mac
pytest tests/ -v
```

**Available Tests:**
- `test_osint_discovery.py` - URL generation
- `test_osint_parsers.py` - Data extraction
- `test_osint_session_manager.py` - Session management
- `test_pii_extractor.py` - PII detection
- `test_username_analyzer.py` - Username analysis
- `test_correlation.py` - Cross-platform correlation
- `test_pdf_generator.py` - Report generation
- `test_playwright_error_handling.py` - Anti-bot and error handling

**Available Tests:**
- `test_osint_discovery.py` - URL generation
- `test_osint_parsers.py` - Data extraction
- `test_osint_session_manager.py` - Session management
- `test_pii_extractor.py` - PII detection
- `test_username_analyzer.py` - Username analysis
- `test_correlation.py` - Cross-platform correlation
- `test_pdf_generator.py` - Report generation
- `test_playwright_error_handling.py` - Anti-bot and error handling

---

## 🔍 Instagram Search Enhancements

The Instagram collector implements robust search functionality with multiple fallback strategies:

### Search Features
1. **10+ Search Icon Selectors**: SVG paths, aria-labels, nav buttons, data-testid attributes
2. **Keyboard Shortcut Fallback**: Ctrl+K shortcut when UI selectors fail
3. **Enhanced Input Detection**: Multiple input field selectors for reliability
4. **Intelligent Typing**: 100ms character delay for autocomplete triggers
5. **Result Extraction**: Visibility checks, username validation, direct click fallback
6. **Debug Screenshots**: Automatic capture at key points for troubleshooting

### Search Strategy
- **Direct URL Navigation**: Used for username identifiers
- **In-App Search**: Used for full names (e.g., "cristiano ronaldo")
- **Autocomplete Handling**: Waits for and clicks on search results
- **Error Recovery**: Multiple retry mechanisms and fallback strategies

---

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)**: Detailed setup instructions
- **[DEPLOYMENT.md](backend/DEPLOYMENT.md)**: Production deployment guide
- **[OSINT_SETUP.md](backend/OSINT_SETUP.md)**: OSINT module configuration
- **[IMPLEMENTATION_DETAILS.md](IMPLEMENTATION_DETAILS.md)**: Technical implementation details
- **API Documentation**: http://localhost:8000/docs (when backend is running)

---

## 🛠️ Troubleshooting

### Python Version Issues
- **Problem**: Playwright not working with Python 3.13
- **Solution**: Use Python 3.11.x (specified in `runtime.txt`)

### Instagram Search Not Working
- **Problem**: Search icon not found or profile not appearing
- **Solution**: The collector implements 10+ fallback selectors and keyboard shortcuts. Check debug screenshots in logs.

### Session Expired
- **Problem**: "Session expired or invalid" errors
- **Solution**: Re-authenticate and save new session JSON files in `backend/app/osint/sessions/`

### Playwright Installation
- **Problem**: Browser binaries not found
- **Solution**: Run `playwright install chromium` after pip install

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [spaCy](https://spacy.io/) - NLP and entity extraction
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Playwright](https://playwright.dev/) - Browser automation
- [React](https://reactjs.org/) - Frontend framework
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS

---

## ⚠️ Disclaimer

This tool is designed for **privacy awareness and educational purposes only**. It analyzes **publicly available information** from social media platforms to help users understand their digital footprint and identify potential privacy risks.

**Important Guidelines:**
- Use responsibly and ethically
- Comply with all applicable laws and regulations
- Respect platform Terms of Service
- Obtain proper authorization before analyzing others' data
- Use only for legitimate security research and privacy awareness

The developers are not responsible for misuse of this tool.

---

<p align="center">Made with ❤️ for privacy awareness</p>
<p align="center">🇱🇰 Sri Lanka</p>
