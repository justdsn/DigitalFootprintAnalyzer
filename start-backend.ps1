Set-Location "D:\SLIIT\Y4\RP\RP-Prod-2\DigitalFootprintAnalyzer\backend"
& "D:\SLIIT\Y4\RP\RP-Prod-2\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
