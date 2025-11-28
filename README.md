Phase-1
# 🔍 Digital Footprint Analyzer [RP]

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)

A **Sri Lanka-focused OSINT (Open Source Intelligence) web application** that helps ordinary users (non-technical citizens) understand their digital footprint across social media platforms.

## 🌟 Overview

Digital Footprint Analyzer is designed to help Sri Lankan citizens:

1. **Discover Personal Information Exposure** - Find out what personal information you've accidentally exposed on social media (emails, phone numbers, locations, etc.)

2. **Detect Potential Impersonation** - Check for fake profiles or accounts that might be impersonating you across major platforms

3. **Assess Privacy Risks** - Get a risk assessment score and actionable recommendations to improve your online privacy

## ✨ Features

### 🔐 PII (Personally Identifiable Information) Extraction
- **Email Detection** - RFC 5322 compliant email pattern matching
- **Sri Lankan Phone Numbers** - Support for local (07X-XXXXXXX) and international (+94) formats
- **URL Extraction** - General and social media platform-specific URL detection
- **@Mention Detection** - Social media handle extraction

### 🇱🇰 Sri Lankan Context
- **Local Phone Formats** - Full support for Sri Lankan mobile number formats with E.164 normalization
- **Sri Lankan Names** - Recognition of common family names (Perera, Silva, Fernando, Bandara, etc.)
- **Local Cities** - NER support for major Sri Lankan cities (Colombo, Kandy, Galle, Jaffna, etc.)
- **Local Organizations** - Recognition of Sri Lankan companies and institutions

### 👤 Username Analysis
- **Platform URL Generation** - Direct links to profiles on Facebook, Instagram, X (Twitter), LinkedIn, TikTok, YouTube
- **Username Variations** - Generate potential impersonation usernames to monitor
- **Pattern Analysis** - Detect suspicious username patterns that might indicate fake accounts

### 🧠 Named Entity Recognition (NER)
- **Person Detection** - Identify names in text
- **Location Recognition** - Detect cities, countries, and places
- **Organization Identification** - Find company and institution names

### 🌐 Internationalization (i18n)
- **English** - Full English language support
- **Sinhala (සිංහල)** - Complete Sinhala translation for all UI text

## 🛠️ Tech Stack

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

### DevOps
| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **Docker Compose** | Multi-container orchestration |
| **nginx** | Frontend production server |

## 📁 Project Structure

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

## 📡 API Documentation

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

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Test Coverage

```bash
pytest tests/ -v --cov=app
```

## 🎨 Design System

### Colors
- **Primary Blues**: `#1e40af`, `#3b82f6` - Main brand colors
- **Accent Teals**: `#0d9488`, `#14b8a6` - Secondary accent colors
- **Risk Colors**: Green (low), Amber (medium), Red (high)

### Typography
- **Display Font**: Plus Jakarta Sans
- **Body Font**: Inter

## 🔮 Roadmap

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
- [ ] Browser extension
- [ ] Mobile application
- [ ] Tamil language support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [spaCy](https://spacy.io/) for NLP capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://reactjs.org/) for the frontend framework
- [Tailwind CSS](https://tailwindcss.com/) for styling

## ⚠️ Disclaimer

This tool is designed for personal privacy awareness and educational purposes. It analyzes only publicly available information. Users are responsible for ensuring their use of this tool complies with all applicable laws and platform terms of service.

---

<p align="center">🇱🇰</p>
