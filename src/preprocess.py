import pretty_midi
import numpy as np
from pathlib import Path

# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
MIDI_DIR = BASE_DIR / "data" / "maestro"
OUTPUT_FILE = BASE_DIR / "data" / "notes.npy"


def extract_notes():

    all_notes = []

    midi_files = sorted(
        list(MIDI_DIR.rglob("*.midi")) +
        list(MIDI_DIR.rglob("*.mid"))
    )

    print(f"Found {len(midi_files)} MIDI files.")

    successful = 0
    failed = 0

    for index, midi_file in enumerate(midi_files, start=1):

        try:
            midi_data = pretty_midi.PrettyMIDI(str(midi_file))

            notes = []

            for instrument in midi_data.instruments:

                if instrument.is_drum:
                    continue

                for note in instrument.notes:
                    notes.append((note.start, note.pitch))

            notes.sort(key=lambda x: (x[0], x[1]))

            for start_time, pitch in notes:
                all_notes.append(pitch)

            successful += 1

        except Exception as error:
            failed += 1
            print(f"Error processing {midi_file.name}: {error}")

        if index % 100 == 0:
            print(f"Processed {index}/{len(midi_files)} files")

    if not all_notes:
        print("No notes extracted. Please check the MIDI dataset.")
        return

    notes_array = np.array(all_notes, dtype=np.int16)

    np.save(OUTPUT_FILE, notes_array)

    print("\nPreprocessing completed!")
    print(f"Successful files: {successful}")
    print(f"Failed files: {failed}")
    print(f"Total notes extracted: {len(notes_array)}")
    print(f"Unique pitches: {len(np.unique(notes_array))}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    extract_notes()
