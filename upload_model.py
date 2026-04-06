import os
from huggingface_hub import HfApi

# El Token viene del Secret de GitHub
TOKEN = os.getenv("HF_TOKEN")
REPO_ID = "ShadowRoot07/Shadow-Resonance-API"

if not TOKEN:
    print("❌ Error: No se encontró la variable de entorno HF_TOKEN")
    exit(1)

api = HfApi()

print(f"🚀 Sincronizando repositorio con Hugging Face Spaces...")

try:
    # upload_folder sube TODO el contenido actual al Space
    api.upload_folder(
        folder_path=".", # Sube el directorio actual
        repo_id=REPO_ID,
        repo_type="space",
        token=TOKEN,
        # Opcional: ignorar carpetas de git o temporales de python
        ignore_patterns=[".git*", "__pycache__*", "venv*"]
    )
    print("✅ ¡Space actualizado con éxito! README, Dockerfile y Modelo sincronizados.")
except Exception as e:
    print(f"❌ Error durante la sincronización: {e}")
    exit(1)

