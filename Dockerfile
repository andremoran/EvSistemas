FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias primero (capa cacheada)
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar codigo y modelo
COPY api/main.py .
COPY model/ model/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
