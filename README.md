# JIVY

**When patient care can't wait, JIVY doesn't either.**

JIVY is an MVP for showcasing **agentic AI** in hospital flow: a React frontend backed by a Python API that runs a **hospital flow engine** (risk, pressure, decisions) and **reasoning** (LLM via Ollama) for patient summaries. No database — simulation and LLM only.

---

## Project structure

```
nexus_Jivy/
├── backend/              # FastAPI app (simulation + reasoning API)
├── hospital_flow_engine/ # Risk, pressure, decision engines + data
├── reasoning/            # LLM chains (analysis + explanation, Ollama)
├── jivy-frontend/        # Vite + React (Login, Doctor, Ops dashboards)
├── scripts/              # test_stack.py
├── requirements.txt      # Python deps (backend + engine + reasoning)
└── README.md
```

---

## Prerequisites

- **Python** 3.10+ (backend, simulation, reasoning)
- **Node.js** 18+ and **npm** (frontend)
- **Ollama** (optional): for full LLM summaries; [install Ollama](https://ollama.ai) and run `ollama pull mistral`. Without Ollama, the API returns a fallback explanation.

---

## Quick start (development)

### 1. Backend

From the project root:

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend: **http://127.0.0.1:8000**  
API docs: **http://127.0.0.1:8000/docs**

### 2. Frontend

In another terminal:

```bash
cd jivy-frontend
npm install
npm run dev
```

Frontend: **http://localhost:5173**  
The app proxies `/api` to the backend.

### 3. Use the app

1. Open http://localhost:5173  
2. Pick role (Doctor / Operations Manager / Hospital Admin) → **Login**  
3. **Doctor** or **Ops** dashboard loads simulation data from the backend (stats, patient list)  
4. Click a **patient ID** to open a modal with an LLM summary (or fallback if Ollama is not running)

---

## "Connection refused" to localhost:11434 (Ollama not running)

If you see **HTTPConnectionPool(host='localhost', port=11434): Max retries exceeded** or **Connection refused** in logs when clicking a patient:

- **Ollama is not running.** The backend uses Ollama (port 11434) for LLM summaries.
- **You can ignore it:** the API still returns a fallback explanation (engine text + instructions). The modal will show that and ask you to start Ollama for full summaries.
- **To enable LLM summaries:**
  1. Install [Ollama](https://ollama.ai) and start it (open the app, or run `ollama serve` in a terminal).
  2. Pull the model used in `reasoning/llm.py`: run `ollama pull mistral`.
  3. Click a patient again; you should get an AI-generated summary.

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/simulation/run` | Run hospital flow simulation; returns `{ ok, outputs }` (patient_id, risk_level, decision, pressure, etc.) |
| POST | `/api/reasoning/explain` | Body: `{ "simulation_record", "audience" }` (e.g. `"doctor"` or `"operations manager"`). Returns `{ ok, explanation, llm_available }` from LLM or fallback. |

---

## Testing

With the backend running on port 8000:

```bash
python scripts/test_stack.py
```

- **GET /api/simulation/run** → 120 outputs (backend reflected)  
- **POST /api/reasoning/explain** → explanation (LLM if Ollama + model available, else fallback)

---

## Deployment

### Backend (production)

- Use a process manager (e.g. systemd, Docker, or a PaaS) to run:

  ```bash
  uvicorn backend.main:app --host 0.0.0.0 --port 8000
  ```

- Set **CORS** in `backend/main.py` to your frontend origin(s) (e.g. `https://your-domain.com`).  
- Optional: use **Gunicorn + Uvicorn workers**:

  ```bash
  pip install gunicorn
  gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
  ```

### Frontend (production)

1. Build:

   ```bash
   cd jivy-frontend
   npm ci
   npm run build
   ```

2. Either:
   - **Option A:** Serve the `jivy-frontend/dist` folder with a static server (e.g. nginx, Vercel, Netlify) and configure the server to **proxy `/api`** to your backend URL, or  
   - **Option B:** Set frontend env (e.g. `VITE_API_BASE=https://your-api.com`) and point API requests to that base; then serve `dist` as static files.

### Environment (optional)

- Backend: create a `.env` in the project root if you add config (e.g. `PORT=8000`).  
- Frontend: use `VITE_*` env vars for build-time config (e.g. API base URL); reference them in code as `import.meta.env.VITE_*`.

### Ollama (reasoning)

- For full LLM summaries in production, run **Ollama** on a server the backend can reach (same host or `OLLAMA_HOST`), and pull the model used in `reasoning/llm.py` (e.g. `mistral`).

---

## Dashboards

- **Doctor:** Stats from backend (total patients, risk breakdown, decision breakdown, avg pressure). Clickable patient IDs → modal with LLM summary (audience: doctor).  
- **Ops:** Same simulation data; clickable patient IDs → LLM summary (audience: operations manager).  
- **Admin:** Placeholder route; extend as needed.

---

## License

Use as needed for the nexus_Jivy project.
