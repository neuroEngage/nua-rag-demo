# Nua RAG Demo - Verification Instructions

## 1. Start the Server
Open a terminal in this directory and run:
```powershell
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --port 8000 --reload
```

## 2. Run Verification
In a **new** terminal window, run:
```powershell
.\venv\Scripts\Activate.ps1
python verify_agents.py
```

## What to Expect
You should see output demonstrating all agents in action:

1. **Safety Agent**: Will flag the "severe cramps" query with a warning.
2. **Product Agent**: Will recommend pads based on "heavy flow".
3. **Education Agent**: Will explain "brown blood".
4. **Analytics**: Will show the JSON output of the top business concerns.

## Troubleshooting
- If you see `ConnectionRefusedError`, ensure the server is running on port 8000.
- If you see `ImportError`, ensure you activated the venv.
