from pathlib import Path

import pandas as pd
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from src.access.rbac import get_current_user, require_permission
from src.pii.anonymizer import MedVietAnonymizer

app = FastAPI(title="MedViet Data API", version="1.0.0")
anonymizer = MedVietAnonymizer()
DATA_PATH = Path("data/raw/patients_raw.csv")


@app.get("/api/patients/raw")
@require_permission(resource="patient_data", action="read")
async def get_raw_patients(current_user: dict = Depends(get_current_user)):
    df = pd.read_csv(DATA_PATH)
    return JSONResponse(content=df.head(10).to_dict(orient="records"))


@app.get("/api/patients/anonymized")
@require_permission(resource="training_data", action="read")
async def get_anonymized_patients(current_user: dict = Depends(get_current_user)):
    df = pd.read_csv(DATA_PATH)
    df_anon = anonymizer.anonymize_dataframe(df)
    return JSONResponse(content=df_anon.head(10).to_dict(orient="records"))


@app.get("/api/metrics/aggregated")
@require_permission(resource="aggregated_metrics", action="read")
async def get_aggregated_metrics(current_user: dict = Depends(get_current_user)):
    df = pd.read_csv(DATA_PATH)
    metrics = df.groupby("benh", dropna=False).size().reset_index(name="count")
    return {
        "total_patients": int(len(df)),
        "by_condition": metrics.to_dict(orient="records"),
    }


@app.delete("/api/patients/{patient_id}")
@require_permission(resource="patient_data", action="delete")
async def delete_patient(patient_id: str, current_user: dict = Depends(get_current_user)):
    return {
        "status": "deleted",
        "patient_id": patient_id,
        "performed_by": current_user["username"],
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "MedViet Data API"}
