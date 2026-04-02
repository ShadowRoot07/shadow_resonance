import pretty_midi
import numpy as np

class MidiProcessor:
    def __init__(self, seq_length=50):
        self.seq_length = seq_length

    def midi_to_notes(self, midi_file):
        """Convierte un archivo MIDI en una secuencia de notas plana"""
        pm = pretty_midi.PrettyMIDI(midi_file)
        
        # Seleccionamos el primer instrumento disponible
        if not pm.instruments:
            return np.array([])
            
        instrument = pm.instruments[0]
        notes = []

        # Ordenamos las notas por tiempo de inicio para mantener la melodía
        sorted_notes = sorted(instrument.notes, key=lambda x: x.start)

        for note in sorted_notes:
            notes.append(note.pitch)
            
        return np.array(notes)

    def prepare_sequences(self, notes, vocab_size):
        """Crea ventanas de tiempo (X) y la nota objetivo (y)"""
        X = []
        y = []

        for i in range(len(notes) - self.seq_length):
            # La ventana de entrada (ej: notas 0 a 49)
            X.append(notes[i : i + self.seq_length])
            # La nota que la IA debe aprender a predecir (ej: nota 50)
            y.append(notes[i + self.seq_length])

        X = np.array(X)
        y = np.array(y)

        # AJUSTE CRÍTICO: La LSTM espera (muestras, pasos_de_tiempo, características)
        # Como solo enviamos la nota, la característica es 1.
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))

        return X, y

