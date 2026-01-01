# OSINT System Setup Guide

## Prerequisites

### 1. Python Version (CRITICAL)

**Use Python 3.11.x or 3.12.x**

Playwright has compatibility issues with Python 3.13+. Check your version:

```bash
python --version
# Should show: Python 3.11.x or Python 3.12.x
```

If you have Python 3.13, install Python 3.12:

**Windows:**
- Download from: https://www.python.org/downloads/
- Install Python 3.12.x
- Add to PATH
- Use `py -3.12` to run with specific version

**Linux/Mac:**
```bash
pyenv install 3.12.2
pyenv local 3.12.2
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Install Playwright Browsers (REQUIRED)

This is the most common source of "instant empty results" errors!

```bash
playwright install chromium
```

Verify installation:
```bash
playwright --version
# Should show version without errors
```

### 4. Verify OSINT Setup

Start the backend and check logs:

```bash
uvicorn app.main:app --reload
```

Look for these messages:
- ✅ "Playwright is ready for OSINT data collection"
- ❌ "Playwright browsers not found" - Run: `playwright install chromium`
- ⚠️  "Python 3.13 detected" - Downgrade to Python 3.12

## Troubleshooting

### Issue: Deep scan returns instant "no PII" results

**Cause:** Playwright browser not initializing

**Solutions:**
1. Run `playwright install chromium`
2. Check Python version (use 3.12, not 3.13)
3. Check backend logs for browser initialization errors

### Issue: "Browser launch failed" error

**Windows:**
```bash
# Run as administrator
playwright install chromium --with-deps
```

**Linux:**
```bash
# Install system dependencies
sudo playwright install-deps chromium
playwright install chromium
```

### Issue: Python 3.13 compatibility

**Solution:** Use Python 3.12 instead

```bash
# Create new virtual environment with Python 3.12
py -3.12 -m venv venv
# or
python3.12 -m venv venv

# Activate and reinstall
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
playwright install chromium
```

### Issue: "RuntimeError: Failed to initialize Playwright browser"

**This error means Playwright cannot launch the browser. Common causes:**

1. **Browser not installed:**
   ```bash
   playwright install chromium
   ```

2. **Missing system dependencies (Linux):**
   ```bash
   sudo playwright install-deps chromium
   ```

3. **Python 3.13 compatibility:**
   - Switch to Python 3.12 (see above)

4. **Permissions issue (Windows):**
   - Run terminal as Administrator
   - Reinstall: `playwright install chromium`

### Issue: "All platform data collection failed"

**This means ALL platforms failed to initialize browsers.**

**Solutions:**
1. Check if Playwright is installed: `playwright --version`
2. Reinstall browsers: `playwright install chromium`
3. Check Python version: `python --version` (should be 3.11.x or 3.12.x)
4. Review backend startup logs for detailed errors

## Testing OSINT System

Run a test scan:

```bash
# In backend directory
python -m pytest tests/test_osint_collectors.py -v
```

Or test via API:
```bash
curl -X POST http://localhost:8000/api/osint/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "cristiano",
    "platforms": ["instagram"]
  }'
```

Should return actual profile data, not instant empty results.

## Expected Behavior

### Before Fix:
- ❌ Returns in < 1 second
- ❌ Says "no PII, no impersonation"
- ❌ Silent browser initialization failure

### After Fix:
- ✅ Takes 10-30+ seconds (real browser automation)
- ✅ Returns actual Instagram profile data
- ✅ Finds multiple profiles (real + fakes)
- ✅ Extracts PII from bio/profile
- ✅ Proper error messages if browser fails
- ✅ Startup check warns about Python 3.13

## System Requirements

### Minimum:
- Python 3.11 or 3.12
- 2GB RAM
- 500MB disk space (for Chromium browser)

### Recommended:
- Python 3.12.2
- 4GB RAM
- 1GB disk space
- Fast internet connection (for data collection)

## Additional Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [Playwright System Requirements](https://playwright.dev/python/docs/intro#system-requirements)
- [Python Downloads](https://www.python.org/downloads/)

## Support

If you continue to experience issues:
1. Check the backend logs for detailed error messages
2. Ensure all system dependencies are installed
3. Verify Python version compatibility
4. Review Playwright documentation for platform-specific issues
