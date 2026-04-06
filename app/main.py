from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.services.composer import ShadowComposer
import os
import shutil
import uuid

app = FastAPI(title="Shadow Resonance API")

# --- BUSCADOR DE RUTA DINÁMICO ---
def get_model_path():
    # Intentamos las dos rutas posibles en el contenedor
    paths = [
        "/home/user/app/app/models/saved/shadow_composer.keras",
        "/home/user/app/models/saved/shadow_composer.keras"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

MODEL_PATH = get_model_path()
BASE_DIR = "/home/user/app"
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "raw", "references")
GENERATED_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

composer = None

@app.on_event("startup")
async def load_model():
    global composer
    if MODEL_PATH:
        try:
            print(f"🚀 Cargando modelo desde: {MODEL_PATH}")
            composer = ShadowComposer(MODEL_PATH)
            print("✅ Shadow_Resonance: IA Cargada con éxito.")
        except Exception as e:
            print(f"❌ Error de Keras: {e}")
    else:
        print("⚠️ Crítico: No se encontró el archivo .keras en ninguna ruta conocida.")

def translate_prompt_to_style(prompt: str) -> str:
    p = prompt.lower()
    if any(w in p for w in ["triste", "lento", "ambient"]): return "chiptune_ambient"
    if any(w in p for w in ["acción", "batalla", "épico"]): return "chiptune_action"
    if any(w in p for w in ["piano", "relajante"]): return "acoustic_piano"
    if any(w in p for w in ["rock", "metal"]): return "electric_rock"
    return "chiptune_action"

@app.get("/")
def home():
    return {"status": "Online", "model_ready": composer is not None, "path": MODEL_PATH}

@app.post("/upload-reference/")
async def upload_reference(file: UploadFile = File(...)):
    if not file.filename.endswith(('.mid', '.midi')):
        raise HTTPException(status_code=400, detail="Solo archivos MIDI.")
    file_id = str(uuid.uuid4())[:8]
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "Referencia guardada", "file_id": file_id}

@app.post("/generate-from-text/")
async def generate_from_text(prompt: str, reference_id: str = None):
    if not composer:
        raise HTTPException(status_code=503, detail="IA no cargada.")
    style = translate_prompt_to_style(prompt)
    ref_path = None
    if reference_id:
        for f in os.listdir(UPLOAD_DIR):
            if f.startswith(reference_id):
                ref_path = os.path.join(UPLOAD_DIR, f)
                break
    try:
        file_path = composer.generate_music(style, reference_path=ref_path)
        return {"style": style, "download_url": f"/download/{os.path.basename(file_path)}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(GENERATED_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename, media_type='audio/midi')
    raise HTTPException(status_code=404, detail="No encontrado.")

