# 🎵 AI Music Generation Studio

An AI-powered music generation application that creates original musical melodies using a Long Short-Term Memory (LSTM) Neural Network and combines them with multiple instrument tracks.

The application allows users to customize music based on mood, style, tempo, duration, and instrument selection through an interactive and colourful Streamlit web interface.

## 🌐 Live Demo

Try the AI Music Generation Studio online:

🔗 **Live Application:** [Click Here to Open AI Music Generation Studio](https://ai-music-generation-studio.streamlit.app/)

Explore AI-powered music generation, customize instruments and music settings, and listen to your generated tracks.

## ✨ Features

- 🎹 AI-powered melody generation using an LSTM model.
- 🎻 Multi-instrument music composition.
- 🎭 Mood-based music customization.
- 🎼 Multiple music styles.
- ⚡ Adjustable music tempo.
- ⏱️ Customizable music duration.
- 🎚️ Individual instrument volume controls.
- 🎧 Audio playback within the application.
- ⬇️ Download generated music in MIDI and WAV formats.
- 🎵 Generate multiple music versions.

## 🛠️ Technologies Used

- Python
- TensorFlow / Keras
- LSTM Neural Network
- NumPy
- Pretty MIDI
- Music21
- FluidSynth
- Streamlit

## 📊 Dataset

This project uses the **MAESTRO MIDI Dataset** for training the LSTM-based music generation model.

The dataset contains piano performances in MIDI format and is used to learn musical patterns and generate new melodies.

## 🧠 AI Model

The project uses a Long Short-Term Memory (LSTM) neural network to learn sequential patterns from MIDI note data.

The model architecture includes:

- Embedding Layer
- LSTM Layer
- Dropout Layer
- LSTM Layer
- Dropout Layer
- Dense Output Layer with Softmax Activation

The trained model predicts subsequent musical notes based on previously learned note sequences.

## 🎼 Music Generation Process

1. Load MIDI files from the MAESTRO dataset.
2. Extract musical notes and preprocess the data.
3. Train the LSTM neural network.
4. Generate new melodies using the trained model.
5. Create supporting instrument tracks using rule-based composition.
6. Combine the instrument tracks into a MIDI file.
7. Convert the generated MIDI file into WAV audio using FluidSynth.
8. Play and download the generated music through the Streamlit application.

## 🎨 Application Capabilities

The Streamlit application provides an interactive interface where users can:

- Select Single Instrument or Full Track generation.
- Choose musical instruments.
- Customize mood and music style.
- Adjust tempo and duration.
- Control individual instrument volumes.
- Generate and listen to music.
- Download MIDI and WAV files.

## 📁 Project Structure

```text
CodeAlpha_MusicGeneration/
│
├── data/
│   ├── maestro/
│   └── notes.npy
│
├── models/
│   ├── best_music_model.keras
│   └── music_generation_model.keras
│
├── outputs/
│
├── soundfonts/
│   └── FluidR3_GM.sf2
│
├── src/
│   ├── preprocess.py
│   ├── train.py
│   └── generate.py
│
├── app.py
├── requirements.txt
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Navigate to the Project Directory

```bash
cd CodeAlpha_MusicGeneration
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure FluidSynth

Install FluidSynth and place a compatible SoundFont file inside the `soundfonts` directory.

Ensure the FluidSynth executable path is correctly configured in the music generation script.

### 7. Run the Application

```bash
streamlit run app.py
```

## 🎧 Output Formats

The application generates:

- **MIDI (.mid):** Musical note and instrument information.
- **WAV (.wav):** Rendered audio output.

## 🚀 Future Improvements

- Improve musical harmony and melody quality.
- Train the model using larger and more diverse MIDI datasets.
- Introduce additional musical instruments.
- Explore advanced deep learning architectures.
- Improve music generation speed and performance.

## 👩‍💻 Internship Project

Developed as part of the **CodeAlpha Artificial Intelligence Internship**.

**Project:** AI Music Generation

**Primary Language:** Python

**Application Framework:** Streamlit

---

⭐ If you find this project interesting, consider giving the repository a star!