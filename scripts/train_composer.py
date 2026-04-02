import tensorflow as tf
from tensorflow.keras import layers, Model
import numpy as np
import os
from app.services.music_processor import MidiProcessor

# --- 1. CONFIGURACIÓN ---
VOCAB_SIZE = 500  
SEQ_LENGTH = 50   
NUM_NOTES = 128   
DATA_PATH = "data/raw"
MODEL_SAVE_PATH = 'app/models/saved/shadow_composer.keras'

# --- 2. CARGADOR DE DATOS ---
def load_training_data():
    processor = MidiProcessor(seq_length=SEQ_LENGTH)
    all_X_music = []
    all_y_music = []
    all_X_text = []

    # Mapeo de carpetas a IDs (Esto alimenta el brazo de texto)
    style_map = {
        "chiptune_action": 0,
        "chiptune_ambient": 1,
        "acoustic_piano": 2,
        "electric_rock": 3
    }

    print("🎹 Iniciando procesamiento de archivos MIDI...")
    
    found_files = False
    for folder, label_id in style_map.items():
        folder_path = os.path.join(DATA_PATH, folder)
        if not os.path.exists(folder_path):
            continue
        
        files = [f for f in os.listdir(folder_path) if f.endswith(('.mid', '.midi'))]
        if files:
            found_files = True
            print(f"📁 Procesando {len(files)} archivos en: {folder}")
            
        for file in files:
            try:
                notes = processor.midi_to_notes(os.path.join(folder_path, file))
                if len(notes) > SEQ_LENGTH:
                    X, y = processor.prepare_sequences(notes, vocab_size=NUM_NOTES)
                    all_X_music.append(X)
                    all_y_music.append(y)
                    # El texto se repite para cada ventana de esa canción
                    # Creamos un array de forma (N, 10) relleno con el ID del estilo
                    text_input_data = np.full((len(X), 10), label_id)
                    all_X_text.append(text_input_data)
            except Exception as e:
                print(f"⚠️ Error procesando {file}: {e}")

    if not found_files:
        raise ValueError(f"❌ No se encontraron archivos MIDI en {DATA_PATH}. Revisa las carpetas.")

    return (np.vstack(all_X_text), np.vstack(all_X_music)), np.concatenate(all_y_music)

# --- 3. DEFINICIÓN DEL MODELO ---
def build_shadow_composer(vocab_size, seq_length, num_notes):
    # Brazo de Texto
    text_input = layers.Input(shape=(10,), name="text_query")
    embedding = layers.Embedding(input_dim=vocab_size, output_dim=64)(text_input)
    text_features = layers.GlobalAveragePooling1D()(embedding)
    text_context = layers.RepeatVector(seq_length)(text_features)

    # Brazo Musical
    music_input = layers.Input(shape=(seq_length, 1), name="music_sequence")

    # Combinación Funcional
    combined = layers.Concatenate()([music_input, text_context])

    # Núcleo Recurrente
    x = layers.LSTM(256, return_sequences=True)(combined)
    x = layers.Dropout(0.3)(x)
    x = layers.LSTM(256)(x)
    x = layers.Dense(128, activation='relu')(x)

    output = layers.Dense(num_notes, activation='softmax', name="note_output")(x)

    model = Model(inputs=[text_input, music_input], outputs=output)
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# --- 4. EJECUCIÓN ---
if __name__ == "__main__":
    # Crear directorios de salida si no existen
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)

    try:
        # Cargar datos
        (X_text, X_music), y = load_training_data()
        
        # Construir modelo
        shadow_model = build_shadow_composer(VOCAB_SIZE, SEQ_LENGTH, NUM_NOTES)
        shadow_model.summary()

        # Entrenamiento
        print("\n🚀 Iniciando entrenamiento en la nube...")
        shadow_model.fit(
            [X_text, X_music], 
            y, 
            epochs=50, 
            batch_size=64,
            verbose=1
        )

        # Guardar resultados
        shadow_model.save(MODEL_SAVE_PATH)
        print(f"✅ ¡Éxito! Modelo guardado en: {MODEL_SAVE_PATH}")

    except Exception as e:
        print(f"💥 Error crítico: {e}")
        exit(1)

