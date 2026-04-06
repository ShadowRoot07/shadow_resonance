import os
from huggingface_hub import HfApi

TOKEN = os.getenv("HF_TOKEN")
REPO_ID = "ShadowRoot07/Shadow-Resonance-API"
LOCAL_FILE = "app/models/saved/shadow_composer.keras"

if not TOKEN:
    print("❌ Error: HF_TOKEN no encontrado")
    exit(1)

api = HfApi()

print(f"🚀 Forzando subida binaria de {LOCAL_FILE}...")

try:
    # Subimos el archivo individualmente forzando que NO use LFS del lado de la API
    api.upload_file(
        path_or_fileobj=LOCAL_FILE,
        path_in_repo="app/models/saved/shadow_composer.keras",
        repo_id=REPO_ID,
        repo_type="space",
        token=TOKEN,
        identical_ok=False # Fuerza la sobreescritura aunque crea que es igual
    )
    
    # Subimos el resto del código
    api.upload_folder(
        folder_path=".",
        repo_id=REPO_ID,
        repo_type="space",
        token=TOKEN,
        ignore_patterns=[".git*", "app/models/saved/shadow_composer.keras"] # Evitamos subirlo doble
    )
    print("✅ ¡Sincronización total completada!")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

