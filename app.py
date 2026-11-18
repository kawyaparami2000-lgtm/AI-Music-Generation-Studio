import streamlit as st
import subprocess
import sys
import json

from pathlib import Path


# ==========================================
# PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
GENERATION_SCRIPT = BASE_DIR / "src" / "generate.py"

OUTPUT_DIR.mkdir(exist_ok=True)


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Music Generation Studio",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

/* Main application background */

.stApp {
    background:
        radial-gradient(circle at top left, #e9d5ff 0%, transparent 35%),
        radial-gradient(circle at top right, #bfdbfe 0%, transparent 35%),
        linear-gradient(135deg, #f5f3ff 0%, #eff6ff 50%, #fdf2f8 100%);
    color: #252044;
}

/* Main content width */

.block-container {
    padding-block-start: 2rem;
    padding-block-end: 3rem;
    max-inline-size: 1250px;
}

/* Main heading */

.main-title {
    font-size: 43px;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg, #7c3aed, #2563eb, #db2777);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-block-end: 5px;
}

/* Subtitle */

.subtitle {
    text-align: center;
    color: #625b83;
    font-size: 17px;
    margin-block-end: 25px;
}

/* Section headings */

.section-title {
    color: #5425a8;
    font-size: 25px;
    font-weight: 800;
    margin-block-start: 15px;
    margin-block-end: 15px;
}

/* Cards */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid rgba(139, 92, 246, 0.18);
    border-radius: 18px;
    padding: 15px;
    box-shadow: 0 5px 20px rgba(91, 33, 182, 0.07);
}

/* Buttons */

.stButton > button {
    background: linear-gradient(90deg, #7c3aed, #2563eb);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 20px;
    font-size: 16px;
    font-weight: 750;
    transition: all 0.25s ease;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #6d28d9, #1d4ed8);
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(99, 102, 241, 0.3);
}

/* Download buttons */

.stDownloadButton > button {
    background: linear-gradient(90deg, #db2777, #9333ea);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 700;
}

.stDownloadButton > button:hover {
    color: white;
    border: none;
}

/* Select boxes */

div[data-baseweb="select"] > div {
    background-color: white;
    border-radius: 10px;
    border: 1px solid #c4b5fd;
}

/* Text */

p, label, li {
    color: #373151;
}

/* Success message */

div[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ede9fe, #dbeafe);
}

/* Dividers */

hr {
    border-color: #c4b5fd;
}

/* Metric cards */

.metric-card {
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    color: white;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 5px 15px rgba(91, 33, 182, 0.15);
}

.metric-number {
    font-size: 28px;
    font-weight: 900;
}

.metric-label {
    font-size: 14px;
    color: #ede9fe;
}

/* Footer */

.footer {
    text-align: center;
    color: #77708f;
    font-size: 13px;
    padding: 20px;
}

/* Selected instruments success message */

div[data-testid="stAlert"] p {
    color: #ffffff !important;
    font-size: 17px !important;
    font-weight: 800 !important;
}

div[data-testid="stAlert"] {
    background: linear-gradient(90deg, #7c3aed, #2563eb) !important;
    border: none !important;
    border-radius: 12px !important;
}

/* Make selected instrument text clearer */

div[data-testid="stAlert"] svg {
    fill: white !important;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# HEADER
# ==========================================

st.markdown(
    '<div class="main-title">🎵 AI Music Generation Studio</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Create beautiful music with Artificial Intelligence.
        Customize instruments, moods, styles and tempo.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("## 🎧 Music Studio")

    st.markdown("---")

    st.markdown("### ✨ Features")

    st.markdown("""
    - 🎹 AI Melody Generation
    - 🎻 Multi-Instrument Music
    - 🎭 Mood Customization
    - 🎼 Music Style Selection
    - 🎚️ Volume Control
    - 🎧 Audio Playback
    - ⬇️ MIDI & WAV Downloads
    """)

    st.markdown("---")

    st.markdown("### 🤖 AI Technology")

    st.info("""
    **Model:** LSTM Neural Network

    **Dataset:** MAESTRO MIDI

    **Framework:** TensorFlow
    """)

    st.markdown("---")

    st.caption("CodeAlpha Internship Project")


# ==========================================
# CONSTANTS
# ==========================================

INSTRUMENTS = [
    "Piano",
    "Guitar",
    "Violin",
    "Cello",
    "Bass",
    "Flute",
    "Synthesizer",
    "Drums"
]

MOODS = [
    "Happy",
    "Sad",
    "Calm",
    "Energetic",
    "Romantic",
    "Epic"
]

STYLES = [
    "Classical",
    "Relaxing",
    "Game Music",
    "Cinematic",
    "Background Music"
]

TEMPOS = [
    "Slow",
    "Medium",
    "Fast"
]


# ==========================================
# MUSIC CONFIGURATION
# ==========================================

st.markdown(
    '<div class="section-title">🎼 Music Configuration</div>',
    unsafe_allow_html=True
)

with st.container(border=True):

    mode = st.radio(
        "Choose Generation Mode",
        ["Single Instrument", "Full Track"],
        horizontal=True
    )

    st.markdown("### 🎹 Instrument Selection")

    if mode == "Single Instrument":

        selected_instrument = st.selectbox(
            "Select an Instrument",
            INSTRUMENTS
        )

        selected_instruments = [selected_instrument]

    else:

        selected_instruments = st.multiselect(
            "Select Multiple Instruments",
            INSTRUMENTS,
            default=[
                "Piano",
                "Violin",
                "Bass",
                "Drums"
            ],
            help="Select at least two instruments."
        )

    if selected_instruments:

        st.success(
            "🎵 Selected: " + ", ".join(selected_instruments)
        )


# ==========================================
# MUSIC CUSTOMIZATION
# ==========================================

st.markdown(
    '<div class="section-title">🎭 Customize Your Music</div>',
    unsafe_allow_html=True
)

with st.container(border=True):

    col1, col2, col3 = st.columns(3)

    with col1:

        mood = st.selectbox(
            "🎭 Music Mood",
            MOODS
        )

    with col2:

        music_style = st.selectbox(
            "🎼 Music Style",
            STYLES
        )

    with col3:

        tempo = st.selectbox(
            "⚡ Tempo",
            TEMPOS,
            index=1
        )

    st.markdown("---")

    col4, col5 = st.columns(2)

    with col4:

        duration = st.selectbox(
            "⏱️ Music Duration",
            [30, 60, 120],
            format_func=lambda x: (
                "30 Seconds" if x == 30
                else "1 Minute" if x == 60
                else "2 Minutes"
            )
        )

    with col5:

        track_count = st.selectbox(
            "🎵 Number of Music Versions",
            [1, 2, 3, 4, 5]
        )


# ==========================================
# INSTRUMENT VOLUME CONTROL
# ==========================================

st.markdown(
    '<div class="section-title">🎚️ Instrument Volume Control</div>',
    unsafe_allow_html=True
)

volumes = {}

with st.container(border=True):

    if selected_instruments:

        volume_columns = st.columns(
            min(len(selected_instruments), 4)
        )

        for index, instrument in enumerate(
            selected_instruments
        ):

            with volume_columns[
                index % len(volume_columns)
            ]:

                volumes[instrument] = st.slider(
                    f"🔊 {instrument}",
                    min_value=0,
                    max_value=100,
                    value=80 if instrument != "Drums" else 70,
                    key=f"volume_{instrument}"
                )


# ==========================================
# GENERATION SUMMARY
# ==========================================

st.markdown(
    '<div class="section-title">📋 Generation Summary</div>',
    unsafe_allow_html=True
)

with st.container(border=True):

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">🎹</div>
                <div class="metric-label">Mode</div>
                <b>{mode}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    with summary_col2:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">🎭</div>
                <div class="metric-label">Mood</div>
                <b>{mood}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    with summary_col3:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">⚡</div>
                <div class="metric-label">Tempo</div>
                <b>{tempo}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.write(
        "**Instruments:**",
        ", ".join(selected_instruments) if selected_instruments else "None"
    )

    st.write("**Music Style:**", music_style)

    st.write("**Duration:**", f"{duration} seconds")

    st.write("**Number of Versions:**", track_count)


# ==========================================
# GENERATE MUSIC
# ==========================================

st.markdown(
    '<div class="section-title">🚀 Create Your Music</div>',
    unsafe_allow_html=True
)

if st.button(
    "🎵 GENERATE MUSIC",
    use_container_width=True,
    type="primary"
):

    if not selected_instruments:

        st.error("Please select at least one instrument.")

    elif mode == "Full Track" and len(selected_instruments) < 2:

        st.error(
            "Please select at least two instruments for Full Track mode."
        )

    else:

        try:

            # Remove previous outputs

            for i in range(1, track_count + 1):

                old_midi = OUTPUT_DIR / f"generated_music_{i}.mid"
                old_wav = OUTPUT_DIR / f"generated_music_{i}.wav"

                if old_midi.exists():
                    old_midi.unlink()

                if old_wav.exists():
                    old_wav.unlink()

            # Prepare command

            command = [
                sys.executable,
                str(GENERATION_SCRIPT),

                "--mode", mode,
                "--duration", str(duration),
                "--count", str(track_count),
                "--mood", mood,
                "--style", music_style,
                "--tempo", tempo,
                "--volumes", json.dumps(volumes)
            ]

            if mode == "Single Instrument":

                command.extend([
                    "--instrument",
                    selected_instruments[0]
                ])

            else:

                command.extend([
                    "--instruments",
                    ",".join(selected_instruments)
                ])

            # Run generation

            progress = st.progress(0)

            status = st.empty()

            status.info("🎼 Initializing AI Music Generation...")

            with st.spinner(
                "🎵 AI is composing your music. Please wait..."
            ):

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    cwd=str(BASE_DIR)
                )

            progress.progress(100)

            # Check result

            if result.returncode == 0:

                st.success(
                    "🎉 Your music has been generated successfully!"
                )

                st.balloons()

                status.success("Music generation completed!")

                st.markdown("---")

                st.markdown(
                    '<div class="section-title">🎧 Your Generated Music</div>',
                    unsafe_allow_html=True
                )

                generated_count = 0

                for track_number in range(
                    1,
                    track_count + 1
                ):

                    midi_file = (
                        OUTPUT_DIR
                        / f"generated_music_{track_number}.mid"
                    )

                    wav_file = (
                        OUTPUT_DIR
                        / f"generated_music_{track_number}.wav"
                    )

                    if not midi_file.exists() or not wav_file.exists():

                        st.warning(
                            f"Track {track_number} files are missing."
                        )

                        continue

                    generated_count += 1

                    with st.container(border=True):

                        st.markdown(
                            f"### 🎼 Music Version {track_number}"
                        )

                        st.audio(
                            str(wav_file),
                            format="audio/wav"
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            with open(wav_file, "rb") as file:

                                st.download_button(
                                    "⬇️ Download WAV",
                                    data=file.read(),
                                    file_name=wav_file.name,
                                    mime="audio/wav",
                                    key=f"wav_{track_number}",
                                    use_container_width=True
                                )

                        with col2:

                            with open(midi_file, "rb") as file:

                                st.download_button(
                                    "⬇️ Download MIDI",
                                    data=file.read(),
                                    file_name=midi_file.name,
                                    mime="audio/midi",
                                    key=f"midi_{track_number}",
                                    use_container_width=True
                                )

                if generated_count > 0:

                    st.success(
                        f"Successfully generated {generated_count} music version(s)!"
                    )

                # Generation details

                with st.expander("🔍 View Generation Details"):

                    st.write("**AI Model:** LSTM Neural Network")

                    st.write("**Dataset:** MAESTRO MIDI Dataset")

                    st.write("**Mode:**", mode)

                    st.write(
                        "**Instruments:**",
                        ", ".join(selected_instruments)
                    )

                    st.write("**Mood:**", mood)

                    st.write("**Music Style:**", music_style)

                    st.write("**Tempo:**", tempo)

                    st.write("**Duration:**", f"{duration} seconds")

                    st.write("**Versions:**", track_count)

                    st.write("**Instrument Volumes:**")

                    st.json(volumes)

                    st.write("**Generation Log:**")

                    st.code(result.stdout or "No additional logs.")

            else:

                st.error("Music generation failed.")

                with st.expander("View Error Details"):

                    st.code(
                        result.stderr or result.stdout
                    )

        except Exception as error:

            st.error(f"Unexpected error: {error}")


# ==========================================
# ABOUT SECTION
# ==========================================

st.markdown("---")

st.markdown(
    '<div class="section-title">ℹ️ About This Project</div>',
    unsafe_allow_html=True
)

with st.container(border=True):

    st.markdown("""
    ### 🎵 AI Music Generation Studio

    An AI-powered music creation application developed using
    Python, TensorFlow, LSTM Neural Networks and Streamlit.

    **🛠️ Main Technologies**

    - Python
    - TensorFlow / Keras
    - LSTM Neural Network
    - MAESTRO MIDI Dataset
    - Pretty MIDI
    - FluidSynth
    - Streamlit

    **✨ Generation Capabilities**

    - Single instrument music generation
    - Multi-instrument music composition
    - Mood-based music customization
    - Tempo and duration control
    - Instrument volume adjustment
    - MIDI and WAV export
    """)


# ==========================================
# FOOTER
# ==========================================

st.markdown(
    """
    <div class="footer">
        🎵 AI Music Generation Studio
        <br>
        Developed as a CodeAlpha Internship Project
        <br><br>
        Made with 💜 using Python and Artificial Intelligence
    </div>
    """,
    unsafe_allow_html=True
)