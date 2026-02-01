"""
JIVY Backend API: hospital flow engine + reasoning (Llama).
No database — MVP for showcasing agentic AI.
Run from project root: uvicorn backend.main:app --reload
"""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="JIVY API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _serialize_outputs(outputs):
    """Make simulation outputs JSON-safe (timestamps, etc.)."""
    result = []
    for o in outputs:
        rec = dict(o)
        ts = rec.get("timestamp")
        if ts is not None and hasattr(ts, "isoformat"):
            rec["timestamp"] = ts.isoformat()
        result.append(rec)
    return result


# ----- Simulation (hospital_flow_engine) -----
@app.get("/api/simulation/run")
def run_simulation():
    from hospital_flow_engine.simulate import run_simulation as run_sim
    try:
        outputs = run_sim()
        return {"ok": True, "outputs": _serialize_outputs(outputs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----- Reasoning (Llama) -----
class ExplainRequest(BaseModel):
    simulation_record: dict
    audience: str = "doctor"


def _ollama_unavailable_message():
    return (
        "Ollama is not running. To get LLM summaries:\n"
        "1. Install Ollama from https://ollama.ai\n"
        "2. Start Ollama (open the app, or run 'ollama serve' in a terminal)\n"
        "3. Pull a model: ollama pull mistral\n"
        "Then click a patient again for an AI-generated summary."
    )


@app.post("/api/reasoning/explain")
def explain(req: ExplainRequest):
    rec = req.simulation_record or {}
    audience = req.audience or "doctor"
    try:
        from reasoning.post_simulation_chain import explain_simulation_output
        explanation = explain_simulation_output(
            simulation_record=rec,
            audience=audience,
        )
        return {"ok": True, "explanation": explanation, "llm_available": True}
    except (ConnectionError, OSError) as e:
        # Ollama not running (e.g. connection refused on localhost:11434)
        fallback = rec.get("engine_explanation") or "No explanation available."
        fallback += "\n\n---\n" + _ollama_unavailable_message()
        return {"ok": True, "explanation": fallback, "llm_available": False}
    except Exception as e:
        err = str(e).lower()
        if "11434" in err or "connection" in err or "refused" in err or "ollama" in err:
            fallback = rec.get("engine_explanation") or "No explanation available."
            fallback += "\n\n---\n" + _ollama_unavailable_message()
            return {"ok": True, "explanation": fallback, "llm_available": False}
        # Other errors (e.g. missing langchain): still return fallback, don't 500
        fallback = rec.get("engine_explanation") or "No explanation available."
        fallback += f"\n\n---\n[LLM unavailable: {e!s}]"
        return {"ok": True, "explanation": fallback, "llm_available": False}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
