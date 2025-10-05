# src/utils/metrics.py
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
import numpy as np

def compute_metrics(y_true, y_prob, threshold=0.5):
    y_hat = (np.array(y_prob) >= threshold).astype(int)
    p = precision_score(y_true, y_hat, zero_division=0)
    r = recall_score(y_true, y_hat, zero_division=0)
    f1 = f1_score(y_true, y_hat, zero_division=0)
    try:
        auc = roc_auc_score(y_true, y_prob)
    except Exception:
        auc = 0.0
    return {"precision": float(p), "recall": float(r), "f1": float(f1), "auc": float(auc)}
