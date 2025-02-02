import mido
from mido import Message, MidiFile, MidiTrack
import subprocess

def note_to_midi(note):
    """
    Convert a note string (e.g., 'C4', 'D#4', 'Bb3') to a MIDI note number.
    MIDI note numbers: C4 is 60.
    """
    note = note.strip()
    if len(note) < 2:
        raise ValueError("Invalid note: " + note)
    
    letter = note[0].upper()
    accidental = ""
    octave_str = ""
    
    if len(note) >= 3 and note[1] in ['#', 'b']:
        accidental = note[1]
        octave_str = note[2:]
    else:
        octave_str = note[1:]
    
    try:
        octave = int(octave_str)
    except ValueError:
        raise ValueError("Invalid octave in note: " + note)
    
    # Define base note numbers (C = 0, C# = 1, etc.)
    note_base = {
        'C': 0,
        'C#': 1,
        'D': 2,
        'D#': 3,
        'E': 4,
        'F': 5,
        'F#': 6,
        'G': 7,
        'G#': 8,
        'A': 9,
        'A#': 10,
        'B': 11
    }
    
    # Handle flats by converting to the equivalent sharp
    if accidental == 'b':
        # For example, Db is equivalent to C#
        # Subtract one semitone from the natural note.
        natural_value = note_base.get(letter)
        if natural_value is None:
            raise ValueError("Invalid note letter: " + note)
        base_value = (natural_value - 1) % 12
    else:
        key = letter + accidental  # accidental will be empty if none
        base_value = note_base.get(key)
        if base_value is None:
            raise ValueError("Invalid note: " + note)
    
    # MIDI note number calculation:
    # C4 is 60, and MIDI numbers increase by one per semitone.
    midi_number = 12 * (octave + 1) + base_value
    return midi_number

def create_midi(chords, chord_duration, output_file="progression.mid", tempo=500000):
    """
    Creates a MIDI file from a chord progression.
    
    chords: list of chords, where each chord is a list of note strings.
    chord_duration: duration of each chord in seconds.
    tempo: microseconds per beat (default 500000, corresponding to 120 BPM).
    """
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Set tempo
    track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
    
    # Get ticks per beat from the MIDI file (default is usually 480)
    ticks_per_beat = mid.ticks_per_beat
    # Calculate chord duration in ticks:
    # Seconds per beat = tempo / 1e6, so beats per chord = chord_duration / (tempo/1e6)
    beats_per_chord = chord_duration / (tempo / 1e6)
    ticks_per_chord = int(beats_per_chord * ticks_per_beat)
    
    for chord in chords:
        # Turn notes on (all at the same time)
        for note in chord:
            midi_note = note_to_midi(note)
            track.append(Message('note_on', note=midi_note, velocity=64, time=0))
        # Wait for the duration of the chord
        track.append(Message('note_off', note=0, velocity=0, time=ticks_per_chord))
        # Turn notes off
        for note in chord:
            midi_note = note_to_midi(note)
            track.append(Message('note_off', note=midi_note, velocity=64, time=0))
    
    mid.save(output_file)
    print("MIDI file saved as:", output_file)

def main():
    print("=== Piano Chord Progression Creator ===")
    print("Enter your chord progression one chord per line.")
    print("Each chord should be a list of note names with octave numbers (e.g., 'C4 E4 G4').")
    print("Type 'done' when finished.\n")
    
    chords = []
    chord_number = 1
    while True:
        line = input(f"Chord {chord_number}: ").strip()
        if line.lower() == "done":
            break
        if line:
            chord = line.split()
            chords.append(chord)
            chord_number += 1
    
    if not chords:
        print("No chords entered. Exiting.")
        return
    
    chord_duration = 2.0  
    midi_filename = "progression.mid"
    create_midi(chords, chord_duration, output_file=midi_filename)
    
    soundfont = "FluidR3_GM.sf2"
    wav_filename = "progression.wav"
    
    # Build the FluidSynth command.
    command = [
        r"./path",
        "-ni",
        soundfont,
        midi_filename,
        "-F",
        wav_filename,
        "-r",
        "44100"
    ]
    
    print("Converting MIDI to WAV using FluidSynth...")
    result = subprocess.run(command)
    if result.returncode == 0:
        print("WAV file saved as:", wav_filename)
    else:
        print("An error occurred while rendering the WAV file. Please ensure FluidSynth is installed and the SoundFont path is correct.")

if __name__ == "__main__":
    main()
