"""
API REST  -  Prediccion de precio de alquiler en Ecuador
Escuela Politecnica Nacional - Laboratorio ADA
"""
from __future__ import annotations

import os
import numpy as np
import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ── Carga del modelo al iniciar el proceso ────────────────────
MODEL_PATH = os.environ.get("MODEL_PATH", "model/modelo_alquileres.joblib")

try:
    MODEL_INFO    = joblib.load(MODEL_PATH)
    PIPELINE      = MODEL_INFO["pipeline"]
    LOG_TRANSFORM = MODEL_INFO.get("log_transform", True)
    print(f"[OK] Modelo cargado: {MODEL_INFO.get('modelo_nombre')}")
except Exception as exc:
    print(f"[ERROR] No se pudo cargar el modelo: {exc}")
    MODEL_INFO = None
    PIPELINE   = None

# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title="API Alquileres Ecuador",
    description=(
        "Predice el precio de alquiler mensual (USD) a partir de "
        "caracteristicas del inmueble. Laboratorio ADA - EPN."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────
class PredictRequest(BaseModel):
    provincia      : str   = Field(..., example="Pichincha")
    lugar          : str   = Field(..., example="Quito")
    num_dormitorios: float = Field(..., ge=0, le=20,   example=3)
    num_banos      : float = Field(..., ge=0, le=20,   example=2)
    area           : float = Field(..., gt=0, le=5000, example=120)
    num_garages    : float = Field(..., ge=0, le=10,   example=1)


class PredictResponse(BaseModel):
    prediction: float


class HealthResponse(BaseModel):
    status : str
    modelo : str | None
    metricas: dict | None


# ── Endpoints ─────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return {"message": "API Alquileres Ecuador  — ver /docs"}


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health():
    return {
        "status" : "ok" if PIPELINE is not None else "sin modelo",
        "modelo" : MODEL_INFO.get("modelo_nombre") if MODEL_INFO else None,
        "metricas": MODEL_INFO.get("metricas_test") if MODEL_INFO else None,
    }


@app.post("/predict", response_model=PredictResponse, tags=["prediccion"])
def predict(body: PredictRequest):
    if PIPELINE is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")

    row = {
        "provincia"      : body.provincia,
        "lugar"          : body.lugar,
        "num_dormitorios": body.num_dormitorios,
        "num_banos"      : body.num_banos,
        "area"           : body.area,
        "num_garages"    : body.num_garages,
        # features derivadas (deben coincidir con el pipeline de entrenamiento)
        "banos_por_dorm" : body.num_banos    / (body.num_dormitorios + 1),
        "area_por_dorm"  : body.area         / (body.num_dormitorios + 1),
        "tiene_garaje"   : int(body.num_garages > 0),
        "log_area"       : float(np.log1p(body.area)),
    }
    X_in = pd.DataFrame([row])

    try:
        pred       = PIPELINE.predict(X_in)[0]
        precio_usd = float(np.expm1(pred)) if LOG_TRANSFORM else float(pred)
        precio_usd = max(0.0, round(precio_usd, 2))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error de prediccion: {exc}")

    return {"prediction": precio_usd}
