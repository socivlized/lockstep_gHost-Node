from fastapi.testclient import TestClient
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "gHost_Node_N4AI_NGNE_v1_5.py"
spec = importlib.util.spec_from_file_location("ghostnode_v15", ENGINE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
client = TestClient(module.app)

def test_health_and_status():
    assert client.get("/health").json()["status"] == "ok"
    status = client.get("/status").json()
    assert status["identity_integrity"] == 1.0
    assert status["cycle"] == 0

def test_step_changes_observable_state():
    response = client.post("/step", json={"input_vec":[1,0.25,0.1,-0.05,0.2]})
    assert response.status_code == 200
    assert response.json()["cycle"] == 1
    status = client.get("/status").json()
    assert status["cycle"] == 1
    assert status["current_z"] == "z1"
    assert status["nodes"] == 3
