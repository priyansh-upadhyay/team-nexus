# 🚀 Team Nexus: Production Deployment Guide (Railway)

This guide provides a clean-slate, step-by-step process to deploy Team Nexus as two separate services (Backend + Frontend). This is the most stable and production-ready architecture.

---

## 🛑 Step 0: The Clean Slate
Before starting, **Delete any existing services** for this project in your Railway dashboard to avoid configuration conflicts.

---

## 📦 Step 1: Backend Service (FastAPI)

1.  **Create Service**: Click **+ New** -> **GitHub Repo** -> Choose your repo.
2.  **Service Settings**:
    *   **Root Directory**: `/`
    *   **Build Command**: (Leave empty, Railway will auto-detect the `Dockerfile`)
    *   **Start Command**: (Leave empty, `entrypoint.sh` handles this)
3.  **Environment Variables**:
    *   `DATABASE_URL`: (Railway will provide this once you add the DB).
    *   `SECRET_KEY`: Generate a secure string (e.g., `openssl rand -hex 32`).
    *   `ENVIRONMENT`: `production`
    *   `BACKEND_CORS_ORIGINS`: `["https://your-frontend-url.up.railway.app"]` (Add this *after* the frontend is deployed).

---

## 🎨 Step 2: Frontend Service (React/TanStack)

1.  **Create Service**: Click **+ New** -> **GitHub Repo** -> Choose the same repo again.
2.  **Service Settings**:
    *   **Root Directory**: `/web`
    *   **Build Command**: `npm install && npm run build`
    *   **Start Command**: `npx serve -s dist` (Nixpacks usually handles this automatically).
3.  **Environment Variables**:
    *   `VITE_API_BASE_URL`: The URL of your **Backend Service** (e.g., `https://team-nexus-backend.up.railway.app/api`). 
    *   **CRITICAL**: Ensure the URL ends with `/api`.

---

## 🗄️ Step 3: Database (PostgreSQL)

1.  Click **+ New** -> **Database** -> **Add PostgreSQL**.
2.  Railway will automatically create the database.
3.  Go to the **Backend Service** -> **Variables** -> **New Variable** -> **Reference Variable** -> Select `DATABASE_URL` from the PostgreSQL service.

---

## 🧪 Step 4: Verification Checklist

1.  **Migrations**: Check the Backend logs. You should see `[OK] Migrations complete.` (The `entrypoint.sh` runs this automatically).
2.  **Health Check**: Visit `https://your-backend.up.railway.app/api/health/check`. It should return `{"status":"ok"}`.
3.  **CORS**: Once the Frontend is up, ensure its URL is added to the Backend's `BACKEND_CORS_ORIGINS` (as a JSON array).
4.  **Login**: Try to register a new user on the live site.

---

### 💡 Pro Tips
- **Port Handling**: The project is now configured to use Railway's `$PORT` automatically. No manual port setting is required.
- **Troubleshooting**: If you see a "Bad Gateway" during the first 2 minutes, wait—it's usually the database migration finishing.
