Remove-Item -ErrorAction SilentlyContinue npm_install.ps1
git add .
git commit -m "feat: SQLite + FastAPI backend, 150 Indianised clusters, live data frontend

- db/database.py: SQLAlchemy engine + session factory
- db/models.py: Cluster + Tweet ORM models with lat/lng
- db/schemas.py: Pydantic response models
- api/clusters.py: GET/PATCH cluster routes
- api/stats.py: overview, velocity, dept-load, locations, priority-load
- main.py: extended with DB routers + legacy /api/process kept
- seed.py: 150 Hinglish-flavoured clusters across 40 Delhi areas
- requirements.txt: added fastapi, uvicorn, sqlalchemy, pydantic
- frontend/vite.config.js: /api proxy to localhost:8000
- frontend/src/api/*: axios client + clusters/stats API modules
- frontend/src/hooks/*: useClusters + useStats with loading/error states
- Dashboard.jsx: live data, skeleton loaders, server-side filters
- Analytics.jsx: all charts driven by live API stats
- Maps.jsx: lat/lng from DB, no more static CLUSTER_COORDS
- start_backend.ps1 / start_frontend.ps1: one-command startup scripts"
git push origin main
Remove-Item -ErrorAction SilentlyContinue ..\npm_install.ps1
Remove-Item -ErrorAction SilentlyContinue ..\pycheck.ps1
Remove-Item -ErrorAction SilentlyContinue ..\check_env.ps1
