# src/api/app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
from src.ledger import sql_ledger as ledger
from src.ml_detector import detect_transit_with_model
import uvicorn

app = FastAPI()

class PredictReq(BaseModel):
    time: list
    flux: list
    target: str = "remote"

@app.post("/predict")
def predict(req: PredictReq):
    try:
        res = detect_transit_with_model(req.time, req.flux)
        # append to ledger
        h = ledger.append_entry("inference", {"target": req.target, "prediction": res})
        return {"result": res, "ledger_hash": h}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ledger")
def get_ledger(limit: int = 50):
    return ledger.list_entries(limit)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
