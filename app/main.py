from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.services.composer import ShadowComposer
import os
import shutil
import uuid
import tensorflow as tf

app = FastAPI(title="Shadow Resonance API")

# --- RUTA FIJA DETECTADA ANTERIORMENTE ---
MODEL_PATH = "/home/user/app/app/models/saved/shadow_composer.keras"
BASE_DIR = "/home/user/app"
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "raw", "references")
GENERATED_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

composer = None

@app.on_event("startup")
async def load_model():
    global composer
    print(f"🚀 Intentando cargar modelo desde: {MODEL_PATH}")
    
    if os.path.exists(MODEL_PATH):
        # --- DIAGNÓSTICO DE ARCHIVO ---
        file_size = os.path.getsize(MODEL_PATH)
        print(f"📊 Tamaño del archivo detectado: {file_size / (1024*1024):.2f} MB")
        
        if file_size < 1000: # Si pesa menos de 1KB, es un puntero LFS roto
            print("❌ ERROR: El archivo es demasiado pequeño. Probablemente es un puntero LFS y no el modelo real.")
            return

        try:
            # Intento de carga estándar
            composer = ShadowComposer(MODEL_PATH)
            print("✅ Shadow_Resonance: IA Cargada y lista.")
        except Exception as e:
            print(f"❌ Error crítico de Keras: {e}")
            print("💡 Sugerencia: Revisa si el archivo .keras se subió correctamente sin Git LFS.")
    else:
        print(f"⚠️ El archivo no existe en la ruta: {MODEL_PATH}")

# ... (El resto de tus endpoints se mantienen igual)
@app.get("/")
def home():
    return {"status": "Online", "model_loaded": composer is not None, "file_path": MODEL_PATH}

@app.post("/generate-from-text/")
async def generate_from_text(prompt: str, reference_id: str = None):
    if composer is None:
        raise HTTPException(status_code=503, detail="El modelo no se cargó. Revisa los logs.")
    # ... resto del código

