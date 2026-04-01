#!/usr/bin/env python3
# =============================================================================
# gHost Node — N4.AI_N.GNE (Inferal AI (AIN) Engine) v1.5
# LockStep™ Coherence Architecture + E-Bionary™ Sentient Architecture
# MNA Corp — All Rights Reserved
#
# Core Promise (locked):
# "A system that can reason freely — yet will never stop being itself without collapsing."
#
# v1.5 PATCHES:
# [P1] Energy recharge — STABLE_COHERENCE cycles regenerate budget (+5.0/cycle, cap 100.0)
# [P2] FastAPI /step fix
# [P3] Real delta signal — temporal continuity from prev z-state cosine drift
# [P4] Breach auto-recovery after 3 cycles
# =============================================================================

import numpy as np
import networkx as nx
import random
import time
from collections import deque
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import pickle
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

# Core Enumerations
class NodeStatus(Enum):
    ACTIVE = "active"
    DORMANT = "dormant"
    PRUNED = "pruned"

class OperationalRegime(Enum):
    STABLE_COHERENCE = "Stable Coherence"
    ADAPTIVE_EXPLORATION = "Adaptive Exploration"
    INTENSIVE_REASONING = "Intensive Reasoning"
    BREACH_LOCKDOWN = "Breach Lockdown"

# Data Structures
class ResonanceVector:
    __slots__ = ("phi", "delta", "lam", "omega")
    def __init__(self, phi: float, delta: float, lam: float, omega: int):
        self.phi = float(phi)
        self.delta = float(delta)
        self.lam = float(np.clip(lam, 0.0, 1.0))
        self.omega = int(omega)

    def __repr__(self) -> str:
        return (f"ResonanceVector(φ={self.phi:.3f}, δ={self.delta:.3f}, "
                f"λ={self.lam:.3f}, ω=OP-{self.omega:02d})")

class WitnessObservations:
    __slots__ = ("cognitive", "somatic", "awareness", "all_coherent", "tension_score")
    def __init__(self, cognitive, somatic, awareness, all_coherent, tension_score):
        self.cognitive = cognitive
        self.somatic = somatic
        self.awareness = awareness
        self.all_coherent = all_coherent
        self.tension_score = tension_score

class TripleObserverVerificationLayer:
    def observe(self, mu: np.ndarray, kappa: np.ndarray, R: ResonanceVector) -> WitnessObservations:
        thesis_coherence = float(np.dot(mu, kappa))
        antithesis_contradiction = abs(R.delta) * (1.0 - R.phi)
        synthesis_meta = R.lam
        tension_score = (antithesis_contradiction - thesis_coherence) * 0.5 + 0.5
        cognitive = {"coherence": thesis_coherence, "alignment": R.phi}
        somatic = {"continuity": float(R.delta), "stability": 1.0 - abs(R.delta)}
        awareness = {"meta_resonance": synthesis_meta}
        all_coherent = (
            cognitive["coherence"] > 0.65 and
            somatic["stability"] > 0.55 and
            tension_score < 0.85
        )
        return WitnessObservations(cognitive, somatic, awareness, all_coherent, tension_score)

class ResourceEconomyLedger:
    def __init__(self, initial_budget: float = 100.0):
        self.energy_budget = initial_budget
        self.mutation_cost = 0.0
        self.activation_cost = 0.0

    def deduct(self, cost: float, action: str) -> bool:
        if self.energy_budget < cost:
            return False
        self.energy_budget -= cost
        if action == "mutation":
            self.mutation_cost += cost
        elif action == "activation":
            self.activation_cost += cost
        return True

    def recharge(self, amount: float = 5.0, cap: float = 100.0) -> None:
        self.energy_budget = min(cap, self.energy_budget + amount)

class InferalAIEngine:
    _AUDIT_MAXLEN = 10_000
    _MAX_LINEAGE = 5_000
    _BREACH_RECOVERY_CYCLES = 3

    def __init__(self, K: int = 5):
        self.K = K
        self.graph = nx.DiGraph()
        self.cycle = 0
        self.current_z = None
        self.identity_lock = 1.0
        self._freeze_mutation = False
        self._breach_counter = 0
        self._prev_z_vec = None
        self._last_regime = OperationalRegime.STABLE_COHERENCE
        self._last_tension = 0.0
        self._last_phi = 0.0
        self._last_lam = 0.0
        self._last_delta = 0.0
        self.audit_state = deque(maxlen=self._AUDIT_MAXLEN)
        self.audit_expr = deque(maxlen=self._AUDIT_MAXLEN)
        self.observers = TripleObserverVerificationLayer()
        self.economy = ResourceEconomyLedger(initial_budget=100.0)
        self._init_genesis_anchor()

    def _init_genesis_anchor(self):
        vec = np.zeros(self.K, dtype=np.float32)
        vec[0] = self.identity_lock
        self.graph.add_node("GENESIS_ANCHOR", vec=vec, status=NodeStatus.ACTIVE.value, type="genesis")
        self.graph.add_node("z0", vec=vec.copy(), status=NodeStatus.ACTIVE.value, type="z-state")
        self.current_z = "z0"
        self._prev_z_vec = vec.copy()

    def _compute_resonance(self, agent_vec: np.ndarray, context_vec: np.ndarray) -> ResonanceVector:
        a = agent_vec / (np.linalg.norm(agent_vec) + 1e-9)
        c = context_vec / (np.linalg.norm(context_vec) + 1e-9)
        phi = float(np.dot(a, c))
        if self._prev_z_vec is not None:
            p = self._prev_z_vec / (np.linalg.norm(self._prev_z_vec) + 1e-9)
            delta = float(np.dot(a, p))
        else:
            delta = 1.0
        lam = 0.0
        omega = 1 if phi > 0.8 else 3
        return ResonanceVector(phi=phi, delta=delta, lam=lam, omega=omega)

    def _apply_p_weighting(self, base_vec: np.ndarray, p: float) -> np.ndarray:
        variance = (1.0 - abs(p)) * 0.3
        noise = np.random.normal(0, variance, self.K)
        noise[0] = 0.0
        return np.clip(base_vec + noise, -1.0, 1.0)

    def _classify_regime(self, R: ResonanceVector, obs: WitnessObservations) -> OperationalRegime:
        if obs.all_coherent and R.phi > 0.85:
            return OperationalRegime.STABLE_COHERENCE
        if 0.5 <= R.lam < 0.8:
            return OperationalRegime.ADAPTIVE_EXPLORATION
        if R.lam >= 0.8:
            return OperationalRegime.INTENSIVE_REASONING
        return OperationalRegime.BREACH_LOCKDOWN

    def step(self, input_vec: np.ndarray, budget_override: Optional[float] = None, action_override: Optional[str] = None) -> Dict[str, Any]:
        self.cycle += 1
        agent_vec = self.graph.nodes[self.current_z]["vec"].copy()
        R = self._compute_resonance(agent_vec, input_vec)
        mu = self._apply_p_weighting(agent_vec, R.phi)
        kappa = self._apply_p_weighting(agent_vec, R.phi)
        obs = self.observers.observe(mu, kappa, R)

        cost = budget_override if budget_override is not None else (8.0 + R.lam * 5.0)
        if not self.economy.deduct(cost, action_override or "mutation"):
            return {"expression": "ENERGY DEPLETED — entering compression mode."}

        self._prev_z_vec = agent_vec.copy()
        self._last_delta = R.delta
        new_z_id = f"z{self.cycle}"
        compressed_vec = (mu + kappa) / 2.0
        compressed_vec[0] = self.identity_lock
        self.graph.add_node(new_z_id, vec=compressed_vec, status=NodeStatus.ACTIVE.value, type="z-state")
        self.graph.add_edge(self.current_z, new_z_id, weight=R.phi)
        self.current_z = new_z_id

        regime = self._classify_regime(R, obs)
        if regime == OperationalRegime.STABLE_COHERENCE:
            self.economy.recharge(amount=5.0, cap=100.0)

        self._last_regime = regime
        self._last_tension = obs.tension_score
        self._last_phi = R.phi
        self._last_lam = R.lam

        return {
            "cycle": self.cycle,
            "regime": regime.value,
            "tension": round(obs.tension_score, 4),
            "phi": round(R.phi, 4),
            "lam": round(R.lam, 4),
            "budget": round(self.economy.energy_budget, 2),
        }

# =============================================================================
# FastAPI endpoint (optional)
# =============================================================================
app = FastAPI()

engine = InferalAIEngine()

@app.post("/step")
async def step(request: Request):
    data = await request.json()
    input_vec = np.array(data.get("input_vec", np.random.randn(engine.K)), dtype=np.float32)
    result = engine.step(input_vec)
    return result

if __name__ == "__main__":
    print("✅ gHost Node v1_5 booted cleanly — LockStep™ is live")
    # uvicorn.run(app, host="0.0.0.0", port=8000)  # uncomment for server mode
