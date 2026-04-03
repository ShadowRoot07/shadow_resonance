# Usamos una imagen ligera de Python
FROM python:3.10-slim

# Instalamos dependencias del sistema para audio y MIDI
RUN apt-get update && apt-get install -y \
    libasound2-dev \
    libjack-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Creamos un usuario no-root (Hugging Face lo prefiere por seguridad)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"

WORKDIR /app

# Copiamos los requisitos e instalamos
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY --chown=user . .

# Exponemos el puerto 7860 (Puerto estándar de HF Spaces)
EXPOSE 7860

# Comando para arrancar la API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]

