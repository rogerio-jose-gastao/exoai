# src/ml_detector.py
import torch
import numpy as np
import os
from pathlib import Path

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "..", "models", "simple_cnn.pth")
MODEL_PATH = os.path.abspath(MODEL_PATH)
from src.models.cnn import SimpleConv1D

def _prepare(flux, maxlen=2000):
    f = np.array(flux)
    if len(f) < maxlen:
        pad = np.full(maxlen - len(f), f.mean())
        f = np.concatenate([f, pad])
    else:
        f = f[:maxlen]
    f = (f - np.mean(f)) / (np.std(f) + 1e-9)
    x = torch.from_numpy(f.astype('float32')).unsqueeze(0).unsqueeze(0)
    return x

def load_model(device=None):
    device = device or (torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu"))
    model = SimpleConv1D().to(device)
    if os.path.exists(MODEL_PATH):
        state = torch.load(MODEL_PATH, map_location=device)
        model.load_state_dict(state)
    model.eval()
    return model, device

# Returns {label, prob, depth, duration}
def detect_transit_with_model(time, flux):
    model, device = load_model()
    x = _prepare(flux).to(device)
    with torch.no_grad():
        logits = model(x)
        prob = torch.softmax(logits, dim=1)[0,1].item()
    # best-effort depth/duration: reuse simple heuristic for explainability
    depth = float(max(0.0, np.nanmedian(1.0 - flux)))
    duration = 0.0
    return {"label": "candidate" if prob>0.5 else "none", "prob": float(prob), "depth": depth, "duration": duration}

def load_npz_and_detect(path):
    d = np.load(path)
    t = d["time"]
    f = d["flux"]
    return detect_transit_with_model(t, f)
