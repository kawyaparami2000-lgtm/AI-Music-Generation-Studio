import argparse
import subprocess
import shutil
import os
import numpy as np
import pretty_midi
import tensorflow as tf
import json

from pathlib import Path


# ==========================================
# PROJECT PATHS - WINDOWS + LINUX SUPPORT
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_FILE = BASE_DIR / "models" / "music_generation_model.keras"
DATA_FILE = BASE_DIR / "data" / "notes.npy"

OUTPUT_DIR = BASE_DIR / "outputs"

# SoundFont locations
SOUNDFONT_CANDIDATES = [
    BASE_DIR / "soundfonts" / "FluidR3_GM.sf2",
    Path("/usr/share/sounds/sf2/FluidR3_GM.sf2"),
    Path("/usr/share/soundfonts/FluidR3_GM.sf2"),
]

# Optional custom SoundFont path
custom_soundfont = os.environ.get("SOUNDFONT_PATH")

if custom_soundfont:
    SOUNDFONT_CANDIDATES.insert(
        0,
        Path(custom_soundfont)
    )

SOUNDFONT_FILE = next(
    (
        path for path in SOUNDFONT_CANDIDATES
        if path.exists()
    ),
    SOUNDFONT_CANDIDATES[0]
)

# Find FluidSynth executable
FLUIDSYNTH_EXE = shutil.which("fluidsynth")

# Windows fallback
if FLUIDSYNTH_EXE is None:

    WINDOWS_FLUIDSYNTH = (
        Path.home()
        / "Downloads"
        / "FluidSynth"
        / "fluidsynth-v2.6.2-win10-x64-cpp11"
        / "bin"
        / "fluidsynth.exe"
    )

    if WINDOWS_FLUIDSYNTH.exists():
        FLUIDSYNTH_EXE = str(WINDOWS_FLUIDSYNTH)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================
# SETTINGS
# ==========================================

SEQUENCE_LENGTH = 50
SAMPLE_RATE = 22050

INSTRUMENTS = {
    "Piano": 0,
    "Guitar": 24,
    "Violin": 40,
    "Cello": 42,
    "Bass": 32,
    "Flute": 73,
    "Synthesizer": 80,
    "Drums": 0
}


MOOD_SETTINGS = {
    "Happy": {
        "temperature": 1.0,
        "note_duration": 0.30
    },

    "Sad": {
        "temperature": 0.75,
        "note_duration": 0.45
    },

    "Calm": {
        "temperature": 0.65,
        "note_duration": 0.50
    },

    "Energetic": {
        "temperature": 1.1,
        "note_duration": 0.22
    },

    "Romantic": {
        "temperature": 0.80,
        "note_duration": 0.40
    },

    "Epic": {
        "temperature": 1.0,
        "note_duration": 0.28
    }
}


STYLE_SETTINGS = {
    "Classical": 1.0,
    "Relaxing": 1.1,
    "Game Music": 0.9,
    "Cinematic": 1.0,
    "Background Music": 1.15
}


TEMPO_SETTINGS = {
    "Slow": 75,
    "Medium": 110,
    "Fast": 145
}


# C - G - Am - F progression

CHORD_PROGRESSION = [
    [60, 64, 67],
    [55, 59, 62],
    [57, 60, 64],
    [53, 57, 60]
]

CHORD_ROOTS = [48, 43, 45, 41]

BASS_ROOTS = [36, 31, 33, 29]


# ==========================================
# AI NOTE GENERATION
# ==========================================

def sample_next_note(predictions, temperature):

    predictions = np.asarray(
        predictions
    ).astype("float64")

    temperature = max(
        float(temperature),
        0.01
    )

    predictions = np.log(
        predictions + 1e-8
    ) / temperature

    probabilities = np.exp(
        predictions - np.max(predictions)
    )

    probabilities /= np.sum(probabilities)

    return np.random.choice(
        len(probabilities),
        p=probabilities
    )


def generate_melody(
    model,
    notes,
    duration,
    temperature,
    note_duration
):

    total_notes = max(
        1,
        round(duration / note_duration)
    )

    if len(notes) <= SEQUENCE_LENGTH:

        raise ValueError(
            "Not enough MIDI notes in the dataset."
        )

    start_index = np.random.randint(
        0,
        len(notes) - SEQUENCE_LENGTH
    )

    pattern = notes[
        start_index:start_index + SEQUENCE_LENGTH
    ].tolist()

    generated_notes = []

    for step in range(total_notes):

        input_sequence = np.array(
            [pattern[-SEQUENCE_LENGTH:]],
            dtype=np.int32
        )

        predictions = model.predict(
            input_sequence,
            verbose=0
        )[0]

        next_note = sample_next_note(
            predictions,
            temperature
        )

        generated_notes.append(
            int(next_note)
        )

        pattern.append(
            int(next_note)
        )

        if (step + 1) % 100 == 0:

            print(
                f"Generated {step + 1}/{total_notes} notes"
            )

    return generated_notes


# ==========================================
# DRUM GENERATION
# ==========================================

def create_drum_track(duration, bpm):

    drums = pretty_midi.Instrument(
        program=0,
        is_drum=True,
        name="Drums"
    )

    beat_duration = 60 / bpm

    drum_pattern = [
        (36, 0.0, 100),
        (42, 0.5, 52),
        (38, 1.0, 85),
        (42, 1.5, 55),
        (36, 2.0, 95),
        (42, 2.5, 52),
        (38, 3.0, 82),
        (46, 3.5, 65)
    ]

    current_time = 0.0

    while current_time < duration:

        for pitch, beat, velocity in drum_pattern:

            start = (
                current_time
                + beat * beat_duration
            )

            if start >= duration:
                break

            end = min(
                start + 0.12,
                duration
            )

            drums.notes.append(
                pretty_midi.Note(
                    velocity=velocity,
                    pitch=pitch,
                    start=start,
                    end=end
                )
            )

        current_time += 4 * beat_duration

    return drums


# ==========================================
# CHORD GENERATION
# ==========================================

def create_chord_track(
    instrument_name,
    duration,
    bpm
):

    instrument = pretty_midi.Instrument(
        program=INSTRUMENTS[instrument_name],
        name=instrument_name + " Accompaniment"
    )

    beat = 60 / bpm
    bar = beat * 4

    current_time = 0.0
    chord_index = 0

    while current_time < duration:

        chord = CHORD_PROGRESSION[
            chord_index % len(CHORD_PROGRESSION)
        ]

        if instrument_name == "Piano":

            pattern = [
                chord[0],
                chord[1],
                chord[2],
                chord[1]
            ]

            for index, pitch in enumerate(pattern):

                start = current_time + index * beat

                if start >= duration:
                    break

                end = min(
                    start + beat * 0.85,
                    duration
                )

                velocity = [
                    68, 60, 65, 58
                ][index]

                instrument.notes.append(
                    pretty_midi.Note(
                        velocity=velocity,
                        pitch=pitch,
                        start=start,
                        end=end
                    )
                )

        elif instrument_name == "Guitar":

            for beat_number in [0, 2]:

                strum_time = (
                    current_time
                    + beat_number * beat
                )

                for index, pitch in enumerate(chord):

                    start = (
                        strum_time
                        + index * 0.025
                    )

                    if start >= duration:
                        continue

                    instrument.notes.append(
                        pretty_midi.Note(
                            velocity=65,
                            pitch=pitch + 12,
                            start=start,
                            end=min(
                                start + beat * 0.75,
                                duration
                            )
                        )
                    )

        else:

            for pitch in chord:

                instrument.notes.append(
                    pretty_midi.Note(
                        velocity=48,
                        pitch=pitch + (
                            12 if instrument_name == "Flute"
                            else 0
                        ),
                        start=current_time,
                        end=min(
                            current_time + bar * 0.92,
                            duration
                        )
                    )
                )

        current_time += bar
        chord_index += 1

    return instrument


# ==========================================
# BASS GENERATION
# ==========================================

def create_bass_track(duration, bpm):

    instrument = pretty_midi.Instrument(
        program=INSTRUMENTS["Bass"],
        name="Bass"
    )

    beat = 60 / bpm
    bar = beat * 4

    current_time = 0.0
    index = 0

    while current_time < duration:

        root = BASS_ROOTS[
            index % len(BASS_ROOTS)
        ]

        fifth = root + 7

        bass_pattern = [
            (0, root),
            (2, fifth)
        ]

        for offset, pitch in bass_pattern:

            start = current_time + offset * beat

            if start >= duration:
                continue

            instrument.notes.append(
                pretty_midi.Note(
                    velocity=76,
                    pitch=pitch,
                    start=start,
                    end=min(
                        start + beat * 1.65,
                        duration
                    )
                )
            )

        current_time += bar
        index += 1

    return instrument


# ==========================================
# VIOLIN COUNTER-MELODY
# ==========================================

def create_violin_track(
    generated_notes,
    note_duration,
    duration,
    bpm
):

    instrument = pretty_midi.Instrument(
        program=INSTRUMENTS["Violin"],
        name="Violin Counter Melody"
    )

    beat = 60 / bpm
    bar = beat * 4

    previous_pitch = None

    for index, melody_pitch in enumerate(generated_notes):

        if index % 2 != 0:
            continue

        start = index * note_duration

        if start >= duration:
            break

        chord_index = int(
            start // bar
        ) % len(CHORD_PROGRESSION)

        chord = CHORD_PROGRESSION[chord_index]

        candidates = []

        for octave in range(4, 7):

            for chord_pitch in chord:

                pitch = (
                    chord_pitch % 12
                ) + octave * 12

                if 67 <= pitch <= 88:
                    candidates.append(pitch)

        if not candidates:
            continue

        melody_pitch = int(
            np.clip(
                melody_pitch,
                48,
                90
            )
        )

        target_pitch = melody_pitch + 7

        if previous_pitch is None:

            selected_pitch = min(
                candidates,
                key=lambda pitch: abs(
                    pitch - target_pitch
                )
            )

        else:

            selected_pitch = min(
                candidates,
                key=lambda pitch: (
                    abs(pitch - target_pitch)
                    + 0.8 * abs(pitch - previous_pitch)
                )
            )

        timing_offset = np.random.uniform(
            0.0,
            min(0.015, note_duration * 0.05)
        )

        note_start = start + timing_offset

        note_end = min(
            note_start + note_duration * 1.7,
            duration
        )

        if note_end <= note_start:
            continue

        instrument.notes.append(
            pretty_midi.Note(
                velocity=np.random.randint(62, 73),
                pitch=selected_pitch,
                start=note_start,
                end=note_end
            )
        )

        previous_pitch = selected_pitch

    return instrument


# ==========================================
# CELLO HARMONY
# ==========================================

def create_cello_track(duration, bpm):

    instrument = pretty_midi.Instrument(
        program=INSTRUMENTS["Cello"],
        name="Cello Harmony"
    )

    beat = 60 / bpm
    bar = beat * 4

    current_time = 0.0
    chord_index = 0

    while current_time < duration:

        root = CHORD_ROOTS[
            chord_index % len(CHORD_ROOTS)
        ]

        fifth = root + 7

        cello_pattern = [
            (0, root),
            (2, fifth)
        ]

        for beat_offset, pitch in cello_pattern:

            start = (
                current_time
                + beat_offset * beat
            )

            if start >= duration:
                continue

            end = min(
                start + beat * 1.85,
                duration
            )

            instrument.notes.append(
                pretty_midi.Note(
                    velocity=58,
                    pitch=pitch,
                    start=start,
                    end=end
                )
            )

        current_time += bar
        chord_index += 1

    return instrument


# ==========================================
# MELODY INSTRUMENT
# ==========================================

def create_melody_track(
    instrument_name,
    generated_notes,
    note_duration,
    duration
):

    instrument = pretty_midi.Instrument(
        program=INSTRUMENTS[instrument_name],
        name=instrument_name
    )

    rng = np.random.default_rng()

    for index, pitch in enumerate(generated_notes):

        original_start = index * note_duration

        if original_start >= duration:
            break

        timing_offset = rng.uniform(
            0.0,
            min(0.012, note_duration * 0.04)
        )

        start_time = original_start + timing_offset

        end_time = min(
            original_start + note_duration * 0.88,
            duration
        )

        if end_time <= start_time:
            continue

        velocity = int(
            rng.integers(82, 96)
        )

        instrument.notes.append(
            pretty_midi.Note(
                velocity=velocity,
                pitch=int(pitch),
                start=start_time,
                end=end_time
            )
        )

    return instrument


# ==========================================
# VOLUME CONTROL
# ==========================================

def set_instrument_volume(instrument, volume):

    volume = max(
        0,
        min(100, int(volume))
    )

    midi_volume = int(
        volume * 127 / 100
    )

    instrument.control_changes.append(
        pretty_midi.ControlChange(
            number=7,
            value=midi_volume,
            time=0
        )
    )


# ==========================================
# MUSIC COMPOSITION
# ==========================================

def create_full_track(
    selected_instruments,
    generated_notes,
    duration,
    note_duration,
    bpm,
    volumes
):

    midi = pretty_midi.PrettyMIDI(
        initial_tempo=bpm
    )

    melody_instruments = [
        name for name in selected_instruments
        if name != "Drums"
    ]

    main_instrument = (
        melody_instruments[0]
        if melody_instruments
        else None
    )

    # MAIN AI MELODY

    if main_instrument:

        melody_track = create_melody_track(
            main_instrument,
            generated_notes,
            note_duration,
            duration
        )

        melody_track.name = (
            main_instrument + " Main Melody"
        )

        set_instrument_volume(
            melody_track,
            volumes.get(main_instrument, 80)
        )

        midi.instruments.append(
            melody_track
        )

    # SUPPORTING INSTRUMENTS

    for instrument_name in selected_instruments:

        if instrument_name == main_instrument:
            continue

        if instrument_name == "Drums":

            instrument = create_drum_track(
                duration,
                bpm
            )

        elif instrument_name == "Bass":

            instrument = create_bass_track(
                duration,
                bpm
            )

        elif instrument_name == "Violin":

            instrument = create_violin_track(
                generated_notes,
                note_duration,
                duration,
                bpm
            )

        elif instrument_name == "Cello":

            instrument = create_cello_track(
                duration,
                bpm
            )

        else:

            instrument = create_chord_track(
                instrument_name,
                duration,
                bpm
            )

        set_instrument_volume(
            instrument,
            volumes.get(instrument_name, 65)
        )

        midi.instruments.append(
            instrument
        )

    # PIANO ACCOMPANIMENT

    if (
        main_instrument == "Piano"
        and len(selected_instruments) > 1
    ):

        piano_accompaniment = create_chord_track(
            "Piano",
            duration,
            bpm
        )

        piano_accompaniment.name = (
            "Piano Chord Accompaniment"
        )

        set_instrument_volume(
            piano_accompaniment,
            int(
                volumes.get("Piano", 65) * 0.55
            )
        )

        midi.instruments.append(
            piano_accompaniment
        )

    return midi


# ==========================================
# MIDI TO WAV CONVERSION
# ==========================================

def convert_to_wav(midi_file, wav_file):

    if not FLUIDSYNTH_EXE:

        raise FileNotFoundError(
            "FluidSynth executable not found. "
            "Please install FluidSynth."
        )

    if not SOUNDFONT_FILE.exists():

        raise FileNotFoundError(
            f"SoundFont not found: {SOUNDFONT_FILE}"
        )

    command = [
        str(FLUIDSYNTH_EXE),
        "-ni",
        "-T", "wav",
        "-F", str(wav_file),
        "-r", str(SAMPLE_RATE),
        str(SOUNDFONT_FILE),
        str(midi_file)
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        raise RuntimeError(
            result.stderr or result.stdout
        )

    if not Path(wav_file).exists():

        raise RuntimeError(
            "WAV conversion failed. Output file was not created."
        )


# ==========================================
# MAIN MUSIC GENERATION
# ==========================================

def generate_music(
    duration,
    track_count,
    mode,
    selected_instruments,
    mood,
    music_style,
    tempo,
    volumes
):

    if not selected_instruments:

        raise ValueError(
            "Please select at least one instrument."
        )

    if mode == "Single Instrument" and len(selected_instruments) != 1:

        raise ValueError(
            "Single Instrument mode requires exactly one instrument."
        )

    # Validate audio dependencies

    if not FLUIDSYNTH_EXE:

        raise FileNotFoundError(
            "FluidSynth not found. "
            "Please install FluidSynth."
        )

    if not SOUNDFONT_FILE.exists():

        raise FileNotFoundError(
            f"SoundFont not found: {SOUNDFONT_FILE}"
        )

    bpm = TEMPO_SETTINGS[tempo]

    mood_settings = MOOD_SETTINGS[mood]

    note_duration = (
        mood_settings["note_duration"]
        * STYLE_SETTINGS[music_style]
        * (120 / bpm)
    )

    needs_ai = any(
        name != "Drums"
        for name in selected_instruments
    )

    model = None
    notes = None

    if needs_ai:

        if not MODEL_FILE.exists():

            raise FileNotFoundError(
                f"AI model not found: {MODEL_FILE}"
            )

        if not DATA_FILE.exists():

            raise FileNotFoundError(
                f"Processed dataset not found: {DATA_FILE}"
            )

        print("Loading trained AI model...")

        model = tf.keras.models.load_model(
            MODEL_FILE
        )

        print("Loading MIDI dataset...")

        notes = np.load(DATA_FILE)

    for track_number in range(
        1,
        track_count + 1
    ):

        print(
            f"\nGenerating Music Track {track_number}..."
        )

        generated_notes = []

        if needs_ai:

            generated_notes = generate_melody(
                model,
                notes,
                duration,
                mood_settings["temperature"],
                note_duration
            )

        if mode == "Single Instrument":

            instrument_name = selected_instruments[0]

            midi = pretty_midi.PrettyMIDI(
                initial_tempo=bpm
            )

            if instrument_name == "Drums":

                instrument = create_drum_track(
                    duration,
                    bpm
                )

            else:

                instrument = create_melody_track(
                    instrument_name,
                    generated_notes,
                    note_duration,
                    duration
                )

            set_instrument_volume(
                instrument,
                volumes.get(instrument_name, 80)
            )

            midi.instruments.append(
                instrument
            )

        else:

            midi = create_full_track(
                selected_instruments,
                generated_notes,
                duration,
                note_duration,
                bpm,
                volumes
            )

        midi_file = (
            OUTPUT_DIR
            / f"generated_music_{track_number}.mid"
        )

        wav_file = (
            OUTPUT_DIR
            / f"generated_music_{track_number}.wav"
        )

        midi.write(
            str(midi_file)
        )

        print("Converting MIDI to WAV...")

        convert_to_wav(
            midi_file,
            wav_file
        )

        print(
            f"Track {track_number} completed!"
        )

        print(f"MIDI: {midi_file}")
        print(f"WAV: {wav_file}")

    print(
        "\nAll music tracks generated successfully!"
    )


# ==========================================
# COMMAND LINE ARGUMENTS
# ==========================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Advanced AI Music Generation Studio"
    )

    parser.add_argument(
        "--duration",
        type=int,
        choices=[30, 60, 120],
        default=30
    )

    parser.add_argument(
        "--count",
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=1
    )

    parser.add_argument(
        "--mode",
        choices=[
            "Single Instrument",
            "Full Track"
        ],
        default="Single Instrument"
    )

    parser.add_argument(
        "--instrument",
        choices=list(INSTRUMENTS.keys()),
        default="Piano"
    )

    parser.add_argument(
        "--instruments",
        type=str,
        default=""
    )

    parser.add_argument(
        "--mood",
        choices=list(MOOD_SETTINGS.keys()),
        default="Calm"
    )

    parser.add_argument(
        "--style",
        choices=list(STYLE_SETTINGS.keys()),
        default="Relaxing"
    )

    parser.add_argument(
        "--tempo",
        choices=list(TEMPO_SETTINGS.keys()),
        default="Medium"
    )

    parser.add_argument(
        "--volumes",
        type=str,
        default="{}"
    )

    args = parser.parse_args()

    if args.mode == "Single Instrument":

        selected_instruments = [
            args.instrument
        ]

    else:

        selected_instruments = [
            item.strip()
            for item in args.instruments.split(",")
            if item.strip()
        ]

        if not selected_instruments:

            parser.error(
                "Full Track mode requires --instruments."
            )

        invalid = [
            item for item in selected_instruments
            if item not in INSTRUMENTS
        ]

        if invalid:

            parser.error(
                f"Invalid instruments: {invalid}"
            )

    try:

        volumes = json.loads(
            args.volumes
        )

        if not isinstance(volumes, dict):

            raise ValueError(
                "Volumes must be a JSON object."
            )

    except (json.JSONDecodeError, ValueError) as error:

        parser.error(
            f"Invalid volume settings: {error}"
        )

    generate_music(
        duration=args.duration,
        track_count=args.count,
        mode=args.mode,
        selected_instruments=selected_instruments,
        mood=args.mood,
        music_style=args.style,
        tempo=args.tempo,
        volumes=volumes
    )