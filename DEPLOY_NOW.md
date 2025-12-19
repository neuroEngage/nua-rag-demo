# 🚀 DEPLOYMENT INSTRUCTIONS

Your Nua RAG System is fully configured for deployment. All necessary files (`Procfile`, `requirements.txt`, `Dockerfile`) have been created.

Choose **ONE** method below to deploy instantly:

## OPTION 1: Railway (Recommended - Easiest)
1. Go to [railway.app](https://railway.app/) and sign up/login.
2. Click **"New Project"** -> **"Deploy from GitHub repo"** (if you pushed this code) OR use their CLI.
3. **Easier Method**: Install Railway CLI and deploy from here:
   ```powershell
   npm install -g @railway/cli
   railway login
   railway init
   railway up
   ```
4. **Environment Variables**:
   In Railway dashboard, add these variables:
   - `OPENAI_API_KEY`: [Your Key]
   - `DATABASE_URL`: (Railway will provide a PostgreSQL variable if you add a Database plugin, or use the in-memory fallback)

## OPTION 2: Replit (Fastest for Demos)
1. Go to [replit.com](https://replit.com/).
2. Click **"Create Repl"** -> **"Import from GitHub"**.
3. OR: Create a blank Python Repl and manually upload all files from this folder.
4. Click **Run**. Replit will auto-detect `main.py` and install dependencies.

## OPTION 3: Heroku
1. Install Heroku CLI.
2. Run:
   ```powershell
   heroku create nua-rag-demo
   heroku config:set OPENAI_API_KEY=your_key
   git push heroku main
   ```

## ⚠️ IMPORTANT NOTE
For the **Day 1 Demo**, you do NOT need a real cloud database (Postgres). The system is designed to use in-memory mocking for `VectorDB` and `PostgresDB` if connection strings are missing.

**Just make sure to set `OPENAI_API_KEY` in your cloud provider's settings.**
