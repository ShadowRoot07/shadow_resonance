import tensorflow as tf
import numpy as np
import pretty_midi
import os
from app.services.music_processor import MidiProcessor

class ShadowComposer:
    def __init__(self, model_path, seq_length=50):
        self.model = tf.keras.models.load_model(model_path)
        self.seq_length = seq_length
        self.style_map = {
            "chiptune_action": 0,
            "chiptune_ambient": 1,
            "acoustic_piano": 2,
            "electric_rock": 3
        }

    def generate_music(self, style_name, num_notes=100, reference_path=None):
        style_id = self.style_map.get(style_name, 0)
        
        # 1. Semilla de notas: Si hay referencia, la leemos; si no, azar.
        if reference_path and os.path.exists(reference_path):
            processor = MidiProcessor(seq_length=self.seq_length)
            ref_notes = processor.midi_to_notes(reference_path)
            if len(ref_notes) >= self.seq_length:
                # Tomamos las últimas notas de la referencia para continuar la melodía
                current_sequence = ref_notes[-self.seq_length:]
            else:
                # Si es muy corta, rellenamos con azar hasta llegar al seq_length
                padding = np.random.randint(0, 128, size=(self.seq_length - len(ref_notes)))
                current_sequence = np.concatenate([padding, ref_notes])
        else:
            current_sequence = np.random.randint(0, 128, size=(self.seq_length))

        generated_notes = list(current_sequence)
        text_input = np.full((1, 10), style_id)

        print(f"🎼 Componiendo en estilo: {style_name}...")

        for _ in range(num_notes):
            # Formatear la secuencia musical para la LSTM (1, 50, 1)
            music_input = current_sequence[-self.seq_length:].reshape(1, self.seq_length, 1)

            # PREDICCIÓN
            prediction = self.model.predict([text_input, music_input], verbose=0)
            next_note = np.argmax(prediction)

            # Guardar nota y actualizar secuencia para la siguiente iteración
            generated_notes.append(next_note)
            current_sequence = np.append(current_sequence, next_note)

        return self.notes_to_midi(generated_notes, style_name)

    def notes_to_midi(self, notes, style_name):
        pm = pretty_midi.PrettyMIDI()
        
        # Selección de instrumento inteligente según estilo
        program = 80 # Chiptune Square por defecto
        if "piano" in style_name: program = 0
        if "ambient" in style_name: program = 81 # Sawtooth
        if "violin" in style_name: program = 40
        if "rock" in style_name: program = 30 # Distortion Guitar

        instrument = pretty_midi.Instrument(program=program)
        time = 0
        for pitch in notes:
            # Duración de 0.25s por nota
            note = pretty_midi.Note(velocity=100, pitch=int(pitch), start=time, end=time+0.25)
            instrument.notes.append(note)
            time += 0.25

        pm.instruments.append(instrument)
        output_name = f"generated_{style_name}_{np.random.randint(1000, 9999)}.mid"
        output_path = os.path.join("data/processed", output_name)
        pm.write(output_path)
        return output_path

