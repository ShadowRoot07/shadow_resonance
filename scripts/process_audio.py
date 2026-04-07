import os
import subprocess
from pathlib import Path

# Configuración de rutas
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
    print("🚀 Iniciando procesamiento inteligente de audio a MIDI...")

    for folder, style in STYLE_MAP.items():
        audio_folder = INPUT_DIR / folder
        output_folder = OUTPUT_BASE / style

        if not audio_folder.exists():
            continue

        audio_files = list(audio_folder.glob("*.mp3"))
        if not audio_files:
            continue

        # Asegurar que la carpeta de destino exista
        output_folder.mkdir(parents=True, exist_ok=True)

        print(f"📂 Revisando carpeta: {folder} ({len(audio_files)} archivos)")

        for audio_file in audio_files:
            # Basic-pitch genera archivos con el sufijo "_basic_pitch.mid"
            # O simplemente ".mid" dependiendo de la versión. 
            # Aquí verificamos ambos para estar seguros.
            midi_name_standard = audio_file.stem + ".mid"
            midi_name_bp = audio_file.stem + "_basic_pitch.mid"
            
            target_midi_1 = output_folder / midi_name_standard
            target_midi_2 = output_folder / midi_name_bp

            # FILTRO: Si ya existe el MIDI, saltamos la conversión
            if target_midi_1.exists() or target_midi_2.exists():
                print(f"⏭️  Saltando: {audio_file.name} (Ya convertido)")
                continue

            print(f"🎵 Convirtiendo: {audio_file.name}...")
            
            try:
                # Ejecutamos basic-pitch solo para este archivo específico
                subprocess.run(
                    ["basic-pitch", str(output_folder), str(audio_file)],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError as e:
                print(f"❌ Error en {audio_file.name}: {e.stderr}")
            except Exception as e:
                print(f"❌ Error inesperado en {audio_file.name}: {e}")

if __name__ == "__main__":
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    convert_audio_to_midi()
    print("🏁 Proceso de conversión finalizado.")

