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
    # Subida individual del modelo (Sin el argumento erróneo)
    api.upload_file(
        path_or_fileobj=LOCAL_FILE,
        path_in_repo="app/models/saved/shadow_composer.keras",
        repo_id=REPO_ID,
        repo_type="space",
        token=TOKEN
    )
    
    # Subida del resto de la carpeta
    api.upload_folder(
        folder_path=".",
        repo_id=REPO_ID,
        repo_type="space",
        token=TOKEN,
        ignore_patterns=[".git*", "app/models/saved/shadow_composer.keras"]
    )
    print("✅ ¡Sincronización total completada con éxito!")
except Exception as e:
    print(f"❌ Error durante la subida: {e}")
    exit(1)

