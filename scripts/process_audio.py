import os
import subprocess
from pathlib import Path

# Configuración de rutas según tu estructura de directorios
INPUT_DIR = Path("data/raw/audio_input")
OUTPUT_BASE = Path("data/raw")

# Mapeo de carpetas de origen a etiquetas de entrenamiento
STYLE_MAP = {
    "megaman_zero": "chiptune_action",
    "undertale": "chiptune_ambient",
    "deltarune": "chiptune_action",
    "zelda": "chiptune_ambient"
}

def convert_audio_to_midi():
    print("🚀 Iniciando procesamiento de audio a MIDI...")
    
    for folder, style in STYLE_MAP.items():
        audio_folder = INPUT_DIR / folder
        output_folder = OUTPUT_BASE / style
        
        # 1. Verificar si la carpeta de audio existe y tiene archivos
        if not audio_folder.exists():
            print(f"⚠️ Saltando {folder}: El directorio no existe.")
            continue
            
        audio_files = list(audio_folder.glob("*.mp3"))
        if not audio_files:
            print(f"📁 La carpeta {folder} está vacía. Saltando...")
            continue

        # 2. Asegurar que la carpeta de destino (chiptune_action/ambient) exista
        output_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"🎵 Procesando {len(audio_files)} archivos de {folder} -> {style}...")
        
        # 3. Ejecutar la conversión
        # Usamos basic-pitch directamente sobre la carpeta para mayor velocidad
        try:
            # Comando: basic-pitch [output_dir] [input_dir]
            result = subprocess.run(
                ["basic-pitch", str(output_folder), str(audio_folder)],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✅ Éxito en {folder}: MIDIs generados en {style}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error convirtiendo {folder}: {e.stderr}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    # Aseguramos que la base de datos de salida exista
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    convert_audio_to_midi()
    print("🏁 Proceso de conversión finalizado.")

