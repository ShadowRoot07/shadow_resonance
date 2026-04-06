FROM python:3.10-slim

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    libasound2-dev \
    libjack-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Configuración de usuario
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

# Instalar requisitos antes para aprovechar caché de Docker
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY --chown=user . .

# Permisos para las carpetas de datos
RUN mkdir -p data/raw/references data/processed && chown -R user:user /home/user/app

USER user
ENV PATH="/home/user/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]

