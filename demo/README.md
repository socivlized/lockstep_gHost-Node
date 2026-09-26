# Coherence Service Demo

This surface is a thin demo around the existing gHost Node v1.5 engine. It does not simulate coherence telemetry.

## Run

```bash
python -m pip install numpy networkx fastapi uvicorn
python gHost_Node_N4AI_NGNE_v1_5.py
```

The service binds to `127.0.0.1:8000` by default. Then serve this directory from the repository root:

```bash
python -m http.server 5173 --directory demo
```

Open `http://127.0.0.1:5173`.

## API contract

- `GET /health` — process readiness
- `GET /status` — current engine telemetry
- `POST /step` — execute one real engine transition

The demo reads cycle, regime, φ, tension, energy budget, identity integrity and graph state from the engine. It does not claim LLM integration or production readiness.
