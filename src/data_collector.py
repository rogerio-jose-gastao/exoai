"""
DataCollector
-------------
Tenta baixar curvas de luz via Lightkurve. 
Se falhar (ou se for alvo SIMULADO, ex.: "SIM-1"), gera curvas sintéticas de trânsito.

np.savez


Salva arquivos em data/{target}.npz com arrays 'time' e 'flux'.
Retorna lista de metadados: [{target, file, collected_at}, ...]
"""

import os
import numpy as np
from datetime import datetime
import warnings

# Diretório onde os dados serão salvos
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_DIR = os.path.abspath(DATA_DIR)
os.makedirs(DATA_DIR, exist_ok=True)

# Ignora avisos opcionais do Lightkurve (oktopus, etc.)
warnings.filterwarnings("ignore", message=".*tpfmodel submodule.*")
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ----------------------------------------------------------
# Função auxiliar para gerar curvas simuladas de exoplanetas
# ----------------------------------------------------------
def _simulate_lightcurve(duration_days=27, cadence_min=0.02083, transit_depth=0.0025, transit_period=3.5, inject=True):
    n = int(duration_days / cadence_min)
    t = np.linspace(0, duration_days, n)
    flux = 1.0 + 0.0005 * np.sin(2 * np.pi * t / 10.0) + np.random.normal(0, 0.0005, size=t.shape)
    label = 0
    if inject:
        duration = 0.1  # dias
        phase = np.random.rand() * transit_period
        for center in np.arange(phase, duration_days, transit_period):
            mask = (t >= center - duration / 2) & (t <= center + duration / 2)
            flux[mask] -= transit_depth
        label = 1
    return t, flux, label


# ----------------------------------------------------------
# Função principal: coleta (ou simula) curvas de luz
# ----------------------------------------------------------
def fetch_light_curves(targets=None, limit=3, mission="TESS"):
    """
    Tenta buscar curvas de luz reais com o Lightkurve.
    Se não encontrar, ou se o alvo começar com "SIM-", gera curvas simuladas.
    """
    results = []
    targets = targets or ["SIM-1", "SIM-2", "SIM-3"]
    targets = targets[:limit]

    try:
        from lightkurve import search_lightcurve  # versão moderna (sem warnings)
    except ImportError:
        search_lightcurve = None

    for t in targets:
        try:
            # Se o nome começar com "SIM-", gera curva simulada
            if str(t).startswith("SIM-") or not search_lightcurve:
                raise ValueError("Simulated target or Lightkurve unavailable")

            search_result = search_lightcurve(t, mission=mission)
            if search_result is None or search_result.empty:
                raise ValueError("No lightcurve found")

            lc = search_result.download()
            if lc is None:
                raise ValueError("Download failed")

            lc = lc.remove_nans().normalize()
            time = lc.time.value
            flux = lc.flux.value

        except Exception:
            # Gera curva simulada se qualquer parte falhar
            time, flux, label = _simulate_lightcurve()

        # Salva os dados
        fname = os.path.join(DATA_DIR, f"{t.replace(' ', '_')}.npz")
        np.savez(fname, time=time, flux=flux, label=int(label))

        results.append({
            "target": t,
            "file": fname,
            "collected_at": datetime.utcnow().isoformat(),
        })

    return results
