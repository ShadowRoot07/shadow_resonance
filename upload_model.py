import os
from huggingface_hub import HfApi

TOKEN = os.getenv("HF_TOKEN")
REPO_ID = "ShadowRoot07/Shadow-Resonance-API"

if not TOKEN:
    print("❌ Error: No se encontró el token HF_TOKEN")
    exit(1)

api = HfApi()

print(f"🚀 Sincronizando archivos reales (Sin LFS) a {REPO_ID}...")

try:
    # Subimos la carpeta completa. Al haber hecho el 'untrack', 
    # el archivo .keras ahora se subirá con sus 11MB reales.
    api.upload_folder(
        folder_path=".",
        repo_id=REPO_ID,
        repo_type="space",
        token=TOKEN,
        ignore_patterns=[".git*", "__pycache__*", "venv*"]
    )
    print("✅ Sincronización completa. El modelo real debería estar en el Space.")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

