# Digital Footprint Analyzer - Setup and Testing Guide

## 🚨 Current Situation

Your system has:
- ✅ Python 3.11.9 installed
- ✅ Instagram session files present
- ✅ All code properly configured
- ❌ Docker NOT installed
- ✅ Python 3.11 compatible with Playwright

## 🎯 Solutions (Choose One)

---

### ⭐ OPTION 1: Install Docker Desktop (RECOMMENDED)

This is the **easiest and most reliable** solution.

#### Step 1: Download Docker Desktop
1. Visit: https://www.docker.com/products/docker-desktop/
2. Download Docker Desktop for Windows
3. Install and restart your computer

#### Step 2: Start Docker Desktop
1. Launch Docker Desktop application
2. Wait for it to fully start (whale icon in system tray)

#### Step 3: Run the Application
```powershell
cd "D:\SLIIT\Y4\RP\RP-Prod-2\DigitalFootprintAnalyzer"
docker compose up --build
```

#### Step 4: Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

#### Step 5: Test Deep Scan
Open your browser and navigate to http://localhost:3000, then:
1. Enter identifier: "cristiano ronaldo"
2. Select identifier type: "Name"
3. Choose platform: "Instagram"
4. Click "Start Deep Scan"

**Benefits**:
- ✅ Uses Python 3.11 (fully compatible)
- ✅ All dependencies pre-installed
- ✅ Isolated environment
- ✅ Production-ready setup

---

### 🔧 OPTION 2: Install Python 3.11 or 3.12

If you prefer not to use Docker:

#### Step 1: Download Python 3.11
1. Visit: https://www.python.org/downloads/
2. Download Python 3.11.x (NOT 3.13)
3. Install (check "Add to PATH")

#### Step 2: Create New Virtual Environment
```powershell
cd "D:\SLIIT\Y4\RP\RP-Prod-2\DigitalFootprintAnalyzer\backend"

# Create venv with Python 3.11
py -3.11 -m venv .venv311

# Activate it
.venv311\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

#### Step 3: Run Backend
```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 4: Test Deep Scan
```powershell
python test_instagram_direct.py
```

---

### 🧪 OPTION 3: Use Mock Data (Testing Only)

If you just want to see what the system SHOULD return:

```powershell
cd "D:\SLIIT\Y4\RP\RP-Prod-2\DigitalFootprintAnalyzer\backend"
D:\SLIIT\Y4\RP\RP-Prod-2\.venv\Scripts\python.exe mock_deep_scan_results.py
```

This shows expected output but doesn't actually scrape Instagram.

---

## 📊 What the Deep Scan Does

### 1. **Instagram Profile Search**
- Searches for profiles matching "cristiano ronaldo"
- Uses authenticated session (stored in `sessions/instagram_session.json`)
- Extracts profile data via Playwright browser automation

### 2. **PII Detection**
Identifies and categorizes:
- **Critical Risk**: Phone numbers, addresses, national IDs
- **High Risk**: Email addresses, birthdates
- **Medium Risk**: Locations, coordinates
- **Low Risk**: URLs, mentions, bio content

### 3. **Impersonation Analysis**
Calculates:
- Username similarity (0-100%)
- Bio content similarity
- Overall impersonation risk score
- Confidence level

### 4. **Risk Assessment**
Generates:
- Overall risk level (Low/Medium/High)
- Risk score (0-100)
- Specific risk factors
- Actionable recommendations

---

## 🔍 Expected Results for "Cristiano Ronaldo"

Based on the mock data, you should see:

### Profiles Found
1. **@cristiano** (Official)
   - Verified account
   - Bio: "Manchester United, Portugal, Al Nassr, Nike Athlete"
   - PII: URLs, mentions (@nike, @manchesterunited)
   - Impersonation Score: Low

2. **@cristiano_ronaldo_official** (Potential Impersonation)
   - Not verified
   - Bio: "Official Cristiano Ronaldo fan page"
   - PII: Email (cr7fan@gmail.com)
   - Impersonation Score: Medium (75%)

### Risk Assessment
- **Overall Risk**: Medium (45/100)
- **PII Exposure**: Yes (6 items)
- **Impersonation Detected**: Yes (1 account)

### Recommendations
- Review privacy settings
- Monitor for unauthorized identity use
- Remove exposed personal information

---

## 🐛 Troubleshooting

### Issue: "Docker not found"
**Solution**: Install Docker Desktop (Option 1)

### Issue: "Playwright browser fails"
**Solution**: Use Python 3.11/3.12 (Option 2) or Docker (Option 1)

### Issue: "Session expired"
**Solution**: Re-authenticate Instagram session
```powershell
cd backend
python app/osint/tools/create_session.py --platform instagram
```

### Issue: "No profiles found"
**Possible causes**:
- Session expired (re-authenticate)
- Instagram blocking automated access
- Network issues
- Profile doesn't exist or is private

---

## 📁 Important Files

### Configuration
- [`docker-compose.yml`](file:///d:/SLIIT/Y4/RP/RP-Prod-2/DigitalFootprintAnalyzer/docker-compose.yml) - Docker orchestration (updated with Playwright)
- [`backend/Dockerfile`](file:///d:/SLIIT/Y4/RP/RP-Prod-2/DigitalFootprintAnalyzer/backend/Dockerfile) - Backend container (updated with Playwright)

### Testing Scripts
- [`test_instagram_direct.py`](file:///d:/SLIIT/Y4/RP/RP-Prod-2/DigitalFootprintAnalyzer/backend/test_instagram_direct.py) - Standalone test script
- [`test_deep_scan.py`](file:///d:/SLIIT/Y4/RP/RP-Prod-2/DigitalFootprintAnalyzer/backend/test_deep_scan.py) - API-based test
- [`mock_deep_scan_results.py`](file:///d:/SLIIT/Y4/RP/RP-Prod-2/DigitalFootprintAnalyzer/backend/mock_deep_scan_results.py) - Mock data

### Sessions
- [`app/osint/sessions/instagram_session.json`](file:///d:/SLIIT/Y4/RP/RP-Prod-2/DigitalFootprintAnalyzer/backend/app/osint/sessions/instagram_session.json) - Instagram authentication

---

## ✅ Next Steps

**Choose your preferred option above and follow the steps.**

For the **best experience**, I recommend **Option 1 (Docker Desktop)** because:
- ✅ No Python version conflicts
- ✅ Everything pre-configured
- ✅ Production-ready
- ✅ Easy to restart/rebuild
- ✅ Isolated from your system

Once Docker is installed, simply run:
```powershell
docker compose up --build
```

Then open http://localhost:3000 and test the deep scan!
