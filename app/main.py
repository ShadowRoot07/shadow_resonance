from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.services.composer import ShadowComposer
import os
import shutil
import uuid

app = FastAPI(title="Shadow Resonance API")

# --- CONFIGURACIÓN DE RUTAS DINÁMICAS ---
# 'CURRENT_DIR' será la carpeta 'app' donde reside este archivo main.py
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# El modelo está dentro de la carpeta actual: app/models/saved/...
MODEL_PATH = os.path.join(CURRENT_DIR, "models", "saved", "shadow_composer.keras")

# Para los datos, subimos un nivel para que queden en la raíz del proyecto (/home/user/app/data)
BASE_DIR = os.path.dirname(CURRENT_DIR)
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "raw", "references")
GENERATED_DIR = os.path.join(BASE_DIR, "data", "processed")

# Asegurar que existan los directorios de trabajo
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

composer = None

@app.on_event("startup")
async def load_model():
    global composer
    # Este log nos confirmará en la consola de HF la ruta exacta que está usando
    print(f"🔍 Buscando modelo en ruta anclada: {MODEL_PATH}")
    
    if os.path.exists(MODEL_PATH):
        try:
            # Inicializamos el compositor con la ruta verificada
            composer = ShadowComposer(MODEL_PATH)
            print("✅ IA Cargada y lista para componer.")
        except Exception as e:
            print(f"❌ Error crítico al inicializar ShadowComposer: {e}")
    else:
        print(f"⚠️ MODELO NO ENCONTRADO. Verificando contenido de {os.path.dirname(MODEL_PATH)}:")
        # Esto nos ayuda a debuggear viendo qué archivos hay realmente ahí
        try:
            print(f"Contenido detectado: {os.listdir(os.path.dirname(MODEL_PATH))}")
        except:
            print("No se pudo leer la carpeta de modelos.")

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
        "project": "Shadow_Resonance",
        "model_loaded": composer is not None,
        "path_debug": MODEL_PATH
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
        raise HTTPException(status_code=503, detail="IA no lista. Revisa los logs del servidor.")

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
        raise HTTPException(status_code=500, detail=f"Error en generación: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(GENERATED_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename, media_type='audio/midi')
    raise HTTPException(status_code=404, detail="Archivo no encontrado.")

