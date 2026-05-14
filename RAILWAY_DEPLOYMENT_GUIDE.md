# Railway Deployment Guide for Team Nexus

To deploy Team Nexus to Railway, follow these steps to set up both the **Backend** and **Frontend** services from your single repository.

## 1. Backend Service (FastAPI)
1. **Create New Service**: In Railway, select "GitHub Repo" and choose this repository.
2. **Root Directory**: Set this to `/` (the root).
3. **Build Command**: Railway will automatically detect the `Dockerfile` in the root.
4. **Environment Variables**: Add the following:
   - `DATABASE_URL`: Your PostgreSQL connection string (Railway can provide this if you add a Database to the project).
   - `SECRET_KEY`: Generate a random string (`openssl rand -hex 32`).
   - `ENVIRONMENT`: `production`
   - `BACKEND_CORS_ORIGINS`: `["https://your-frontend-url.up.railway.app"]` (Update this after deploying the frontend).

## 2. Frontend Service (React/Vite)
1. **Create New Service**: Select the same GitHub Repo again.
2. **Root Directory**: Set this to `/web`.
3. **Build Command**: `npm install && npm run build`
4. **Start Command**: `npx serve -s dist` (Railway's Nixpacks usually handles this, but you can specify it).
5. **Environment Variables**:
   - `VITE_API_URL`: Your Backend Service URL (e.g., `https://backend-service.up.railway.app`).

## 3. Database
1. Click **+ New** -> **Database** -> **Add PostgreSQL**.
2. Railway will automatically link it. Use the provided internal connection string for the backend's `DATABASE_URL`.

## 4. Final Polish
- Once the Frontend is deployed, copy its URL and add it to the Backend's `BACKEND_CORS_ORIGINS` variable to enable secure communication.
- Make sure to run your migrations on the production database:
  `alembic upgrade head` (You can add this to your `entrypoint.sh` or run it via Railway's shell).
