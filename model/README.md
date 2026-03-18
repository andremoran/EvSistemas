# model/

Esta carpeta contiene el modelo serializado.

## Generar el modelo

Ejecutar `notebooks/02_modelado_ml.ipynb` en orden.
Al finalizar se crea `modelo_alquileres.joblib` en esta carpeta.

## Contenido del archivo .joblib

```python
{
    "pipeline"     : <sklearn Pipeline>,   # preprocessor + estimador
    "features"     : [...],                # lista de features en orden
    "target"       : "precio",
    "log_transform": True,                 # el target fue log(1+precio)
    "modelo_nombre": "LightGBM",           # nombre del mejor candidato
    "metricas_test": {"MAE":..., "RMSE":..., "R2":..., "MAPE":...},
    "categorias"   : {"provincia":[...], "lugar":[...]}
}
```

> El archivo `.joblib` NO se incluye en el repositorio por su tamano.
> Generarlo ejecutando el notebook 2.
