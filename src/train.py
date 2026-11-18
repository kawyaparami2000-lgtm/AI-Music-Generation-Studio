import numpy as np
import tensorflow as tf
from pathlib import Path

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding, Dropout
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping


# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "notes.npy"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


# Training settings
SEQUENCE_LENGTH = 50
EPOCHS = 10
BATCH_SIZE = 128
VOCAB_SIZE = 128
MAX_NOTES = 300_000


def train_model():

    print("Loading processed MIDI notes...")

    notes = np.load(DATA_FILE)

    print(f"Total notes available: {len(notes)}")

    # Use a smaller portion to reduce RAM usage
    notes = notes[:MAX_NOTES].astype(np.int32)

    print(f"Notes selected for training: {len(notes)}")

    # Create TensorFlow dataset without storing all sequences in RAM
    print("Preparing training dataset...")

    dataset = tf.data.Dataset.from_tensor_slices(notes)

    dataset = dataset.window(
        SEQUENCE_LENGTH + 1,
        shift=1,
        drop_remainder=True
    )

    dataset = dataset.flat_map(
        lambda window: window.batch(SEQUENCE_LENGTH + 1)
    )

    dataset = dataset.map(
        lambda sequence: (
            sequence[:-1],
            sequence[-1]
        ),
        num_parallel_calls=tf.data.AUTOTUNE
    )

    dataset = dataset.batch(BATCH_SIZE).prefetch(
        tf.data.AUTOTUNE
    )

    # Build LSTM model
    print("Building LSTM model...")

    model = Sequential([
        Embedding(VOCAB_SIZE, 64),
        LSTM(128, return_sequences=True),
        Dropout(0.2),
        LSTM(128),
        Dropout(0.2),
        Dense(VOCAB_SIZE, activation="softmax")
    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    model.summary()

    # Save the best model
    checkpoint = ModelCheckpoint(
        filepath=str(MODEL_DIR / "best_music_model.keras"),
        monitor="loss",
        save_best_only=True
    )

    early_stopping = EarlyStopping(
        monitor="loss",
        patience=3,
        restore_best_weights=True
    )

    # Start training
    print("\nStarting LSTM model training...")

    model.fit(
        dataset,
        epochs=EPOCHS,
        callbacks=[checkpoint, early_stopping],
        verbose=1
    )

    # Save final model
    model.save(MODEL_DIR / "music_generation_model.keras")

    print("\nTraining completed successfully!")
    print(f"Model saved in: {MODEL_DIR}")


if __name__ == "__main__":
    train_model()