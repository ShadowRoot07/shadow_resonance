from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.services.composer import ShadowComposer
import os
import shutil
import uuid

app = FastAPI(title="Shadow Resonance API")

# Ruta absoluta basada en la estructura detectada por el log
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
    if os.path.exists(MODEL_PATH):
        try:
            # Si el archivo es el real (>10MB), esto funcionará
            composer = ShadowComposer(MODEL_PATH)
            print("✅ Shadow_Resonance: IA Cargada y lista para componer.")
        except Exception as e:
            print(f"❌ Error al cargar el modelo: {e}")
    else:
        print(f"⚠️ Archivo no encontrado en {MODEL_PATH}")

def translate_prompt_to_style(prompt: str) -> str:
    p = prompt.lower()
    if any(w in p for w in ["game over", "triste", "derrota", "lento", "ambient"]):
        return "chiptune_ambient"
    if any(w in p for w in ["acción", "batalla", "rápido", "épico", "nivel"]):
        return "chiptune_action"
    if any(w in p for w in ["piano", "relajante", "clásico"]):
        return "acoustic_piano"
    if any(w in p for w in ["rock", "metal", "guitarra", "eléctrica"]):
        return "electric_rock"
    return "chiptune_action"

@app.get("/")
def home():
    return {
        "status": "Online",
        "model_loaded": composer is not None,
        "version": "1.0.0"
    }

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
    if composer is None:
        raise HTTPException(status_code=503, detail="IA no lista. El modelo no se cargó correctamente.")

    style = translate_prompt_to_style(prompt)
    ref_path = None
    if reference_id:
        for f in os.listdir(UPLOAD_DIR):
            if f.startswith(reference_id):
                ref_path = os.path.join(UPLOAD_DIR, f)
                break

    try:
        file_path = composer.generate_music(style, reference_path=ref_path)
        filename = os.path.basename(file_path)
        return {
            "style_detected": style,
            "download_url": f"/download/{filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(GENERATED_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename, media_type='audio/midi')
    raise HTTPException(status_code=404, detail="Archivo no encontrado.")

