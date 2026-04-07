import os
from huggingface_hub import HfApi

TOKEN = os.getenv("HF_TOKEN")
REPO_ID = "ShadowRoot07/Shadow-Resonance-API"
LOCAL_FILE = "app/models/saved/shadow_composer.keras"

if not TOKEN:
    print("❌ Error: HF_TOKEN no encontrado en las variables de entorno")
    exit(1)

api = HfApi()

try:
    # 1. Subida del archivo del modelo específicamente
    if os.path.exists(LOCAL_FILE):
        print(f"🚀 Subiendo modelo actualizado: {LOCAL_FILE}...")
        api.upload_file(
            path_or_fileobj=LOCAL_FILE,
            path_in_repo="app/models/saved/shadow_composer.keras",
            repo_id=REPO_ID,
            repo_type="space",
            token=TOKEN
        )
    else:
        print(f"⚠️ Advertencia: {LOCAL_FILE} no encontrado. Saltando subida de modelo.")

    # 2. Sincronización del resto del código y archivos MIDI
    print("📂 Sincronizando código y archivos MIDI...")
    api.upload_folder(
        folder_path=".",
        repo_id=REPO_ID,
        repo_type="space",
        token=TOKEN,
        ignore_patterns=[
            ".git*", 
            "data/raw/audio_input/*", # No subir los MP3 pesados
            "__pycache__/*",
            "venv/*",
            ".github/*",
            "app/models/saved/shadow_composer.keras" # Ya lo subimos arriba
        ]
    )
    print("✅ ¡Sincronización con Hugging Face completada con éxito!")
except Exception as e:
    print(f"❌ Error durante la subida: {e}")
    exit(1)

