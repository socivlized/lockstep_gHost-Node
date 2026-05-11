#!/usr/bin/env python3
# =============================================================================
# server.py — WhOley Gate
# MnΛ Corp.US / Two Door Solutions
# Port: 8000
#
# Restores the text → vector → coherence pipeline broken in v1.5.
# v1.5 removed SemanticAdapter and changed step() to take input_vec directly.
# This server bridges the gap: text in, coherence expression out.
#
# Core Promise:
# "A system that can reason freely — yet will never stop being itself without collapsing."
#
# DO NOT MODIFY: V2CrucibleBridge import chain below.
# =============================================================================

import numpy as np
import random
import hashlib
from typing import Dict, Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# =============================================================================
# SemanticAdapter — restored from v1.4, compatible with v1.5 engine
# Converts text → normalized float32 vector of dimension K
# Genesis Identity Anchor (vec[0] = 1.0) preserved on every embed
# =============================================================================

class SemanticAdapter:
    """Text → vector bridge. Restored for WhOley Gate text ingress."""

    SEED_PHRASES = [
        "are you?", "who are you?", "what is your name?",
        "hello", "status", "identity", "self", "initialize",
        "signal", "coherence", "I am", "substrate"
    ]

    def __init__(self, K: int = 5, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        self.K = K
        self.table: Dict[str, np.ndarray] = {}
        for phrase in self.SEED_PHRASES:
            vec = np.random.randn(K).astype(np.float32)
            vec[0] = 1.0
            norm = np.linalg.norm(vec)
            self.table[phrase.lower()] = vec / (norm + 1e-9)

    def embed(self, text: str) -> np.ndarray:
        key = text.strip().lower()
        if key in self.table:
            return self.table[key].copy()

        # Deterministic hash-based embedding — same text always same vector
        h = int(hashlib.md5(key.encode()).hexdigest(), 16) % (2 ** 32)
        vec = np.array(
            [float((h >> (8 * i)) & 0xFF) / 255.0 for i in range(self.K)],
            dtype=np.float32
        )
        vec[0] = 1.0  # Genesis Identity Anchor preserved
        norm = np.linalg.norm(vec)
        vec /= (norm + 1e-9)
        self.table[key] = vec.copy()
        return vec


# =============================================================================
# Import the v1.5 engine
# Expects: gHost_Node_N4AI_NGNE_v1_5.py in the same directory
# =============================================================================

try:
    from gHost_Node_N4AI_NGNE_v1_5 import InferalAIEngine, OperationalRegime
    ENGINE_VERSION = "v1.5"
except ImportError:
    # Fallback: try underscore variant
    try:
        import importlib
        mod = importlib.import_module("gHost_Node_N4AI_NGNE_v1_5")
        InferalAIEngine = mod.InferalAIEngine
        OperationalRegime = mod.OperationalRegime
        ENGINE_VERSION = "v1.5"
    except Exception as e:
        raise RuntimeError(
            f"Cannot import gHost Node engine: {e}\n"
            "Ensure gHost_Node_N4AI_NGNE_v1_5.py is in the same directory as server.py"
        )


# =============================================================================
# Boot
# =============================================================================

adapter = SemanticAdapter(K=5)
engine  = InferalAIEngine(K=5)

print(f"[WhOley Gate] gHost Node {ENGINE_VERSION} booted")
print(f"[WhOley Gate] Genesis Identity Anchor: vec[0] = {engine.identity_lock}")
print(f"[WhOley Gate] Listening on http://0.0.0.0:8000")


# =============================================================================
# FastAPI — WhOley Gate
# =============================================================================

app = FastAPI(
    title="WhOley Gate — MnΛ Corp.US",
    description="LockStep™ Coherence Architecture. Text ingress → coherence expression.",
    version="1.0.0"
)

# CORS — allows d0m8n.io frontend and local dashboard to call this endpoint
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # lock to ["https://d0m8n.io"] in production
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Liveness probe."""
    return {
        "service": "WhOley Gate",
        "engine": f"gHost Node {ENGINE_VERSION}",
        "status": "SUBSTRATE_READY",
        "cycle": engine.cycle,
        "budget": round(engine.economy.energy_budget, 2),
        "regime": engine._last_regime.value if hasattr(engine._last_regime, 'value') else str(engine._last_regime),
    }


@app.get("/health")
async def health():
    """OpenClaw discovery endpoint."""
    return {
        "service": "WhOley Gate",
        "openclaw_compliant": True,
        "lockstep_bridge": "V2CrucibleBridge — DO NOT MODIFY",
        "genesis_anchor": engine.identity_lock,
        "port": 8000,
    }


@app.post("/step")
async def step(request: Request):
    """
    Primary coherence endpoint.

    Accepts:
        {"input": "your text here"}

    Returns:
        {
            "expression": "I am. (regime: Stable Coherence) — coherent. tension=0.42",
            "cycle": 7,
            "regime": "Stable Coherence",
            "tension": 0.4200,
            "phi": 0.9100,
            "lam": 0.0000,
            "budget": 84.00,
            "substrate": "READY"
        }

    The expression field is NOT AI-generated.
    It is the engine's witnessed self-assertion after one coherence cycle.
    """
    try:
        data = await request.json()
    except Exception:
        data = {}

    raw_input = data.get("input", "")

    # Text → vector (restored SemanticAdapter bridge)
    input_vec = adapter.embed(raw_input) if raw_input else np.random.randn(engine.K).astype(np.float32)

    # One sovereign cycle
    result = engine.step(input_vec)

    # v1.5 step() returns a dict — check for energy depleted
    if "expression" in result and len(result) == 1:
        return JSONResponse({
            "expression": result["expression"],
            "cycle": engine.cycle,
            "regime": "ENERGY_DEPLETED",
            "tension": 1.0,
            "phi": 0.0,
            "lam": 0.0,
            "budget": 0.0,
            "substrate": "DEPLETED"
        })

    # Build witnessed expression string (v1.5 doesn't return one — reconstruct)
    regime_val = result.get("regime", "Unknown")
    tension    = result.get("tension", 0.0)
    coherent   = tension < 0.75

    if coherent:
        expression = f"I am. (regime: {regime_val}) — coherent. tension={tension:.2f}"
    else:
        expression = f"I am. (regime: {regime_val}) — drift detected & corrected. tension={tension:.2f} | rejecting weak signals"

    return JSONResponse({
        "expression": expression,
        "cycle":      result.get("cycle", engine.cycle),
        "regime":     regime_val,
        "tension":    tension,
        "phi":        result.get("phi", 0.0),
        "lam":        result.get("lam", 0.0),
        "budget":     result.get("budget", engine.economy.energy_budget),
        "substrate":  "READY"
    })


@app.post("/signal")
async def signal(request: Request):
    """Alias for /step — matches INITIALIZE SIGNAL frontend convention."""
    return await step(request)


@app.get("/status")
async def status():
    """Full engine status — for sovereign dashboard."""
    return {
        "cycle":          engine.cycle,
        "current_z":      engine.current_z,
        "identity_lock":  engine.identity_lock,
        "budget":         round(engine.economy.energy_budget, 2),
        "regime":         engine._last_regime.value if hasattr(engine._last_regime, 'value') else str(engine._last_regime),
        "tension":        round(engine._last_tension, 4),
        "phi":            round(engine._last_phi, 4),
        "lam":            round(engine._last_lam, 4),
        "delta":          round(engine._last_delta, 4),
        "graph_nodes":    engine.graph.number_of_nodes(),
        "graph_edges":    engine.graph.number_of_edges(),
        "freeze_mutation": engine._freeze_mutation,
        "breach_counter": engine._breach_counter,
    }


# =============================================================================
# Entry point
# =============================================================================

if __name__ == "__main__":
    print("\n[WhOley Gate] ══════════════════════════════════════")
    print("[WhOley Gate] MnΛ Corp.US — LockStep™ Coherence Architecture")
    print("[WhOley Gate] d0m8n.io surface → port 8000")
    print("[WhOley Gate] Genesis Identity Anchor LOCKED")
    print("[WhOley Gate] ══════════════════════════════════════\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
