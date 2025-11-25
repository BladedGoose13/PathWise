FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements de ambos módulos
COPY Clases/requirements.txt requirements.txt
COPY Oportunidades/requirements.txt requirements_1.txt

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements_1.txt
# Copiar todo el proyecto
COPY . .

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

# Ejecutar main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]