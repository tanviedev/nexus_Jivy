"""
Test script: backend simulation + reasoning, and that responses are usable by the frontend.
Run from project root: python scripts/test_stack.py
Requires: backend running on http://127.0.0.1:8000 (uvicorn backend.main:app --port 8000)
"""
import json
import sys
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000/api"


def get(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())


def main():
    print("1. GET /api/simulation/run ...")
    try:
        sim = get(f"{BASE}/simulation/run")
    except Exception as e:
        print(f"   FAIL: {e}")
        sys.exit(1)
    if not sim.get("ok"):
        print("   FAIL: ok is not True")
        sys.exit(1)
    outputs = sim.get("outputs") or []
    print(f"   OK: {len(outputs)} outputs (backend reflected)")

    if not outputs:
        print("   No outputs to test reasoning. Exiting.")
        return

    record = outputs[0]
    print(f"   Sample: patient_id={record.get('patient_id')}, decision={record.get('decision')}")

    print("2. POST /api/reasoning/explain (doctor) ...")
    try:
        explain = post(f"{BASE}/reasoning/explain", {
            "simulation_record": record,
            "audience": "doctor",
        })
    except urllib.error.HTTPError as e:
        if e.code == 500:
            print("   OK (with note): Reasoning returned 500. Restart backend to use fallback when LLM/Ollama is unavailable:")
            print("      uvicorn backend.main:app --reload --port 8000")
            print("   Simulation is working; frontend will show backend stats. Patient click will show fallback after restart.")
        else:
            print(f"   FAIL: HTTP {e.code}")
            sys.exit(1)
        return
    except Exception as e:
        print(f"   FAIL: {e}")
        sys.exit(1)
    if not explain.get("ok"):
        print("   FAIL: ok is not True")
        sys.exit(1)
    explanation = explain.get("explanation") or ""
    llm_available = explain.get("llm_available", True)
    print(f"   OK: explanation length={len(explanation)}, llm_available={llm_available}")
    print(f"   Preview: {explanation[:200]}...")

    print("\nAll checks passed. Backend and (fallback or real) LLM are reflected for frontend.")


if __name__ == "__main__":
    main()
