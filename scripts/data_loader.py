import os
import numpy as np
from app.services.music_processor import MidiProcessor

def load_all_data(base_path, seq_length=50):
    processor = MidiProcessor(seq_length=seq_length)
    all_sequences = []
    all_targets = []
    all_labels = [] # Para el brazo de texto

    # Mapeo de carpetas a IDs numéricos
    label_map = {
        "chiptune_action": 0,
        "chiptune_ambient": 1,
        "acoustic_piano": 2,
        "electric_rock": 3
    }

    for folder, label_id in label_map.items():
        folder_path = os.path.join(base_path, folder)
        if not os.path.exists(folder_path): continue
        
        print(f"📁 Procesando: {folder}...")
        for file in os.listdir(folder_path):
            if file.endswith(".mid") or file.endswith(".midi"):
                try:
                    notes = processor.midi_to_notes(os.path.join(folder_path, file))
                    if len(notes) > seq_length:
                        X, y = processor.prepare_sequences(notes, vocab_size=128)
                        all_sequences.append(X)
                        all_targets.append(y)
                        # Creamos una etiqueta por cada secuencia generada
                        all_labels.extend([label_id] * len(X))
                except Exception as e:
                    print(f"❌ Error en {file}: {e}")

    return np.vstack(all_sequences), np.array(all_targets), np.array(all_labels)

# Uso:
# X_musica, y_musica, X_texto = load_all_data("data/raw")

