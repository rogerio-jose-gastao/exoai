# src/agent_orchestrator.py
"""
Agent Orchestrator (síncrono, pronto para rodar com `python -m src.agent_orchestrator`)
- coleta (data_collector.fetch_light_curves)
- detecta (predict_lightcurve com modelo PyTorch)
- registra cada inferência no ledger JSON (blockchain_ledger.add_entry)
- salva resumo em last_run_summary.json
"""

import json
import hashlib
import time
import numpy as np
from pathlib import Path

from src.data_collector import fetch_light_curves
from src.blockchain_ledger import add_entry
from src.ml_inference import predict_lightcurve
from src.utils.metrics import compute_metrics

ROOT = Path(__file__).resolve().parent.parent
SUMMARY_FILE = ROOT / "last_run_summary.json"


def _make_detection_hash(payload: dict) -> str:
    s = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(s).hexdigest()


def run_once(targets=None, limit=3, mission="TESS"):
    print("Agent: Starting collection...")
    collected = fetch_light_curves(targets=targets, limit=limit, mission=mission)
    results = []

    for meta in collected:
        file = meta.get("file")
        target = meta.get("target")
        print(f"Agent: Processing {target} -> {file}")
        try:
            prob = predict_lightcurve(file)
            label = "candidate" if prob > 0.5 else "none"
            depth = float(abs(prob - 0.5) * 0.005)
            duration = 0.02 + prob * 0.02
            pred = {"label": label, "prob": prob, "depth": depth, "duration": duration}
        except Exception as e:
            pred = {"label": "error", "prob": 0.0, "error": str(e)}

        det_payload = {
            "target": target,
            "file": file,
            "prediction": pred,
            "collected_at": meta.get("collected_at"),
        }
        det_hash = _make_detection_hash(det_payload)

        try:
            add_entry(candidate_id=target, probability=float(pred["prob"]), detection_hash=det_hash)
        except Exception as e:
            print("⚠️ Ledger update failed:", e)

        entry = {
            "target": target,
            "file": file,
            "prediction": pred,
            "collected_at": meta.get("collected_at"),
            "detection_hash": det_hash,
        }
        results.append(entry)
        print(f"✅ Agent: Logged {target} -> {pred['label']} (prob={pred['prob']}) hash={det_hash}")

    # Métricas de performance (simuladas)
    y_true, y_prob = [], []
    for r in results:
        try:
            d = np.load(r["file"])
            y_true.append(int(d.get("label", 0)))
        except Exception:
            y_true.append(0)
        y_prob.append(float(r["prediction"].get("prob", 0.0)))

    metrics = compute_metrics(y_true, y_prob, threshold=0.5)
    summary = {"run_at": time.time(), "metrics": metrics, "results": results}

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("📊 Metrics:", metrics)
    print("✅ Agent: Done. Summary saved to", SUMMARY_FILE)


if __name__ == "__main__":
    run_once(limit=3)
