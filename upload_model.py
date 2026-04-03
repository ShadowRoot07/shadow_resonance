import os
from huggingface_hub import HfApi

# GitHub Actions inyectará el token automáticamente en esta variable de entorno
TOKEN = os.getenv("HF_TOKEN")
REPO_ID = "ShadowRoot07/Shadow-Resonance-API"
FILE_PATH = "app/models/saved/shadow_composer.keras"
FILENAME_IN_REPO = "app/models/saved/shadow_composer.keras"

if not TOKEN:
    print("❌ Error: No se encontró la variable de entorno HF_TOKEN")
    exit(1)

api = HfApi()

print(f"🚀 Iniciando subida oficial de {FILE_PATH}...")

try:
    api.upload_file(
        path_or_fileobj=FILE_PATH,
        path_in_repo=FILENAME_IN_REPO,
        repo_id=REPO_ID,
        repo_type="space",
        token=TOKEN
    )
    print("✅ ¡Modelo subido con éxito a Hugging Face!")
except Exception as e:
    print(f"❌ Error durante la subida: {e}")
    exit(1)

