from dash import Dash, html, dcc, Input, Output
import plotly.graph_objs as go
import numpy as np
import json
from pathlib import Path

def latest_npz_files(n=10):
    data_dir = Path(__file__).resolve().parent.parent / "data"
    files = sorted(data_dir.glob("*.npz"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [str(f) for f in files[:n]]

APP = Dash(__name__)

APP.layout = html.Div([
    html.H2("ExoAI — Dashboard (MVP)"),
    dcc.Dropdown(id="file-list", options=[{"label": Path(f).name, "value": f} for f in latest_npz_files()], placeholder="Choose a light curve"),
    dcc.Graph(id="lc-plot"),
    html.Div(id="prediction-info"),
    html.H4("Model metrics"),
    html.Div(id="metrics-display"),
    dcc.Slider(id="threshold-slider", min=0, max=1, step=0.01, value=0.5, marks={0: "0", .5: "0.5", 1: "1"}),
    html.H4("Probabilities across recent results"),
    dcc.Graph(id="prob-bar"),
    html.H4("Recent ledger entries"),
    html.Div(id="ledger-list")
])

@APP.callback(Output("metrics-display","children"), Input("threshold-slider","value"))
def show_metrics(threshold):
    # read last_run_summary.json
    try:
        with open(ROOT/"last_run_summary.json","r") as f:
            s = json.load(f)
            m = s.get("metrics", {})
            # if threshold changed we can recompute locally (optional)
            return html.Div([
                html.P(f"Precision: {m.get('precision',0):.3f}"),
                html.P(f"Recall: {m.get('recall',0):.3f}"),
                html.P(f"F1: {m.get('f1',0):.3f}"),
                html.P(f"AUC: {m.get('auc',0):.3f}"),
            ])
    except Exception:
        return html.Div("No metrics available. Run the agent to generate summary.")

