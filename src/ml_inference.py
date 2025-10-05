import torch
import torch.nn as nn
import numpy as np
from pathlib import Path

# Caminho absoluto garantido, mesmo quando executado fora do diretório principal
MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "exoai_model.pt"


class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(1, 8, 3, padding=1),
            nn.ReLU(),
            nn.Conv1d(8, 16, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
            nn.Linear(16, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.net(x)
        

def load_model():
    model = SimpleCNN()
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    return model


def predict_lightcurve(npz_path: str):
    data = np.load(npz_path)
    flux = (data["flux"] - data["flux"].mean()) / (data["flux"].std() + 1e-8)
    x = torch.tensor(flux, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
    model = load_model()
    with torch.no_grad():
        prob = model(x).item()
    return prob
