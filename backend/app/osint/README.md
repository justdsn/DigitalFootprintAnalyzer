# OSINT Module - Playwright-based Data Collection

## Overview

This module replaces the browser extension with a Playwright-based headless browser automation system for OSINT data collection from social media platforms.

## Features

- **Persistent Sessions**: Maintains login sessions across collection runs
- **Platform Support**: Instagram, Facebook, LinkedIn, X (Twitter)
- **Parallel Collection**: Collects data from multiple platforms simultaneously
- **Integration**: Seamlessly integrates with existing analysis services (NER, PII, correlation)
- **API Endpoints**: RESTful API for OSINT operations

## Architecture

```
app/osint/
├── __init__.py                 # Module exports
├── session_manager.py          # Session persistence
├── orchestrator.py             # Main workflow controller
├── collectors/                 # Platform collectors
│   ├── base_collector.py       # Abstract base
│   ├── instagram_collector.py
│   ├── facebook_collector.py
│   ├── linkedin_collector.py
│   └── twitter_collector.py
├── parsers/                    # HTML parsers
│   ├── profile_parser.py       # Generic parser
│   ├── instagram_parser.py
│   ├── facebook_parser.py
│   ├── linkedin_parser.py
│   └── twitter_parser.py
└── discovery/                  # Discovery utilities
    ├── identifier_detector.py
    ├── url_generator.py
    └── search_engine.py
```

## Installation

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Playwright Browsers

```bash
playwright install chromium
```

### 3. Set up Environment Variables (Optional)

Create a `.env` file in the `backend/` directory:

```env
# OSINT Configuration
OSINT_BROWSER_HEADLESS=true
OSINT_BROWSER_TIMEOUT=30000
OSINT_MAX_RETRIES=3

# Google Custom Search (Optional - for profile discovery)
GOOGLE_API_KEY=your_api_key_here
GOOGLE_CSE_ID=your_cse_id_here
```

## Session Management

### Creating Sessions

Sessions must be created manually by logging into each platform:

1. Run Playwright in headed mode:
   ```python
   from playwright.sync_api import sync_playwright
   
   with sync_playwright() as p:
       browser = p.chromium.launch(headless=False)
       context = browser.new_context()
       page = context.new_page()
       
       # Navigate and login
       page.goto("https://www.instagram.com/")
       # Perform manual login...
       
       # Save session
       storage_state = context.storage_state()
       # Save to app/osint/sessions/instagram_session.json
   ```

2. Save the session file as `{platform}_session.json` in `app/osint/sessions/`

### Session File Format

```json
{
  "metadata": {
    "platform": "instagram",
    "created_at": "2024-01-15T10:30:00",
    "version": "1.0"
  },
  "storageState": {
    "cookies": [...],
    "origins": [...]
  }
}
```

### Session Management API

Check session status:
```bash
GET /api/osint/sessions/status
```

Validate specific session:
```bash
POST /api/osint/sessions/validate
{
  "platform": "instagram"
}
```

## Usage

### API Endpoints

#### 1. Analyze Identifier

```bash
POST /api/osint/analyze
Content-Type: application/json

{
  "identifier": "johndoe",
  "platforms": ["instagram", "facebook"],  # Optional
  "use_search": false                      # Optional
}
```

**Response:**
```json
{
  "input": "johndoe",
  "identifier_type": "username",
  "username": "johndoe",
  "timestamp": "2024-01-15T10:30:00",
  "profiles_found": [
    {
      "platform": "instagram",
      "url": "https://instagram.com/johndoe",
      "username": "johndoe",
      "name": "John Doe",
      "bio": "Software Developer",
      "pii": {
        "emails": ["john@example.com"],
        "phones": [],
        "urls": ["https://example.com"]
      },
      "followers": 1234,
      "analysis": {
        "username_similarity": 100,
        "bio_similarity": 50,
        "pii_exposure_score": 20,
        "timeline_risk": "medium",
        "impersonation_score": 56
      }
    }
  ],
  "correlation": {
    "correlated": true,
    "impersonation_score": 15,
    "impersonation_level": "low"
  },
  "overall_risk": {
    "exposure": "Low",
    "impersonation": "Low",
    "score": 23,
    "profiles_analyzed": 2
  },
  "processing_time_ms": 5234.5
}
```

### Programmatic Usage

```python
from app.osint.orchestrator import OSINTOrchestrator

# Initialize orchestrator
orchestrator = OSINTOrchestrator()

# Perform analysis
result = await orchestrator.analyze(
    identifier="johndoe",
    platforms=["instagram", "facebook"],
    use_search=False
)

print(f"Found {len(result['profiles_found'])} profiles")
print(f"Overall risk: {result['overall_risk']}")
```

## Integration with Existing Services

The orchestrator automatically integrates with:

- **NER Engine** (`services/ner_engine.py`): Extracts named entities from bios
- **PII Extractor** (`services/pii_extractor.py`): Identifies PII in profile data
- **Username Analyzer** (`services/username_analyzer.py`): Analyzes username patterns
- **Correlator** (`services/correlation/`): Cross-platform profile correlation

## Configuration

All configuration is managed through `app/core/config.py`:

```python
# OSINT Configuration
OSINT_BROWSER_HEADLESS: bool = True
OSINT_BROWSER_TIMEOUT: int = 30000  # 30 seconds
OSINT_SESSION_DIR: str = "osint/sessions"
OSINT_MAX_RETRIES: int = 3
OSINT_RETRY_DELAY: int = 2  # seconds
OSINT_RATE_LIMIT_DELAY: float = 1.0  # seconds
OSINT_MAX_CONCURRENT_COLLECTORS: int = 4
```

## Testing

Run the test suite:

```bash
# All OSINT tests
pytest tests/test_osint_*.py -v

# Specific component
pytest tests/test_osint_session_manager.py -v
pytest tests/test_osint_discovery.py -v
pytest tests/test_osint_parsers.py -v
```

## Security Considerations

1. **Session Storage**: Session files contain authentication cookies
   - Stored in `app/osint/sessions/` (ignored by git)
   - Expire after 30 days
   - Should be protected with appropriate file permissions

2. **Rate Limiting**: Built-in delays to avoid platform detection

3. **Public Data Only**: Only collects publicly visible profile information

4. **No Permanent Storage**: Analysis results are returned via API, not stored

## Troubleshooting

### "Login wall detected"
- Session has expired or doesn't exist
- Create a new session for the platform

### "Navigation failed"
- Check internet connection
- Verify profile URL is accessible
- Increase timeout in config

### "Browser not found"
- Run `playwright install chromium`

### Import errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`

## Development

### Adding a New Platform

1. Create collector in `collectors/new_platform_collector.py`:
```python
from .base_collector import BaseCollector

class NewPlatformCollector(BaseCollector):
    def get_platform_name(self) -> str:
        return "new_platform"
    
    async def collect(self, url: str) -> Dict[str, Any]:
        # Implementation
```

2. Create parser in `parsers/new_platform_parser.py`
3. Update `COLLECTORS` and `PARSERS` in `orchestrator.py`
4. Add to `URLGenerator.PLATFORMS` in `discovery/url_generator.py`

## License

MIT License - See LICENSE file for details
