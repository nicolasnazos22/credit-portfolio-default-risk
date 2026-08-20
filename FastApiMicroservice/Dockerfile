# Imagen slim de Python. No hace falta la imagen especial de Lambda
# si el objetivo es solo correr la API como container normal.
FROM python:3.12-slim

WORKDIR /app

# Copiamos requirements primero para aprovechar el cache de Docker:
# si el código cambia pero no las dependencias, este paso no se re-ejecuta.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código de la app y artefactos del modelo.
# BASE_DIR en factory_scoring_service.py es Path("model") relativo al cwd,
# así que "model" tiene que quedar en /app/model, al mismo nivel que /app/app.
COPY app ./app
COPY model ./model

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
