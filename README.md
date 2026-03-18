# Prediccion de Alquileres en Ecuador

Solucion para el proceso de seleccion del **Tecnico de Investigacion** —
Laboratorio ADA, Escuela Politecnica Nacional.

## Estructura del repositorio

```
alquileres-ecuador/
├── notebooks/
│   ├── 01_analisis_datos.ipynb     <- EDA y procesamiento
│   └── 02_modelado_ml.ipynb        <- Modelado, evaluacion y serializacion
├── api/
│   ├── main.py                     <- FastAPI application
│   └── requirements.txt
├── model/
│   └── modelo_alquileres.joblib    <- Generado corriendo el notebook 2
├── data/
│   └── alquileres_ecuador.csv      <- Dataset original
├── figs/                           <- Generadas por los notebooks
├── Dockerfile
├── render.yaml
└── README.md
```

## Pasos para reproducir

### 1. Clonar el repositorio
```bash
git clone https://github.com/<usuario>/alquileres-ecuador.git
cd alquileres-ecuador
```

### 2. Ejecutar los notebooks (Google Colab recomendado)
Abrir en Colab en orden:
1. `notebooks/01_analisis_datos.ipynb`  — genera `data/alquileres_clean.csv`
2. `notebooks/02_modelado_ml.ipynb`     — genera `model/modelo_alquileres.joblib`

### 3. Correr la API localmente
```bash
pip install -r api/requirements.txt
uvicorn api.main:app --reload
# Abrir http://localhost:8000/docs
```

### 4. Con Docker
```bash
docker build -t alquileres-api .
docker run -p 8000:8000 alquileres-api
```

## Uso de la API

### POST /predict

**Request**
```json
{
  "provincia": "Pichincha",
  "lugar": "Quito",
  "num_dormitorios": 3,
  "num_banos": 2,
  "area": 120,
  "num_garages": 1
}
```

**Response**
```json
{ "prediction": 750.0 }
```

**curl**
```bash
curl -X POST https://<servicio>.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{"provincia":"Pichincha","lugar":"Quito","num_dormitorios":3,"num_banos":2,"area":120,"num_garages":1}'
```

**Python**
```python
import requests
r = requests.post(
    "https://<servicio>.onrender.com/predict",
    json={"provincia":"Pichincha","lugar":"Quito",
          "num_dormitorios":3,"num_banos":2,"area":120,"num_garages":1}
)
print(r.json())
```

### GET /health
```json
{
  "status": "ok",
  "modelo": "LightGBM",
  "metricas": {"MAE": 95.4, "RMSE": 148.2, "R2": 0.87, "MAPE": 14.3}
}
```

## Despliegue en Render.com

Ver seccion [Configuracion de Render](#configuracion-de-render) abajo.

El archivo `render.yaml` automatiza todo el proceso.
URL publica formato: `https://alquileres-ecuador-api.onrender.com`

## Descripcion de la solucion

### Procesamiento (`01_analisis_datos.ipynb`)
- Carga robusta con deteccion de encoding (UTF-8 / latin-1 / cp1252)
- Reparacion de artefactos de doble-codificacion
- Parser jerarquico de columna Lugar: extrae ciudad y sector
- Imputacion contextual (mediana por provincia+ciudad)
- Clasificacion de precio: Economico / Medio / Lujo por cuartiles dentro de cada ciudad

### Modelo (`02_modelado_ml.ipynb`)
- Seis candidatos evaluados en validacion cruzada 5-Fold
- Seleccion automatica del menor RMSE
- Target log-transformado: log(1+precio) con recuperacion via expm1()
- Features derivadas: ratio banos/dormitorios, area/dormitorios, log(area)
- Serializacion con joblib incluyendo metadata completa
