import streamlit as st
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
from gtts.lang import tts_langs
import tempfile
import os
import uuid

# Supported language codes for translation and voice
languages = {
    "Telugu": "te",
    "Tamil": "ta",
    "Hindi": "hi",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Japanese": "ja",
    "Russian": "ru"
}

# Get supported gTTS language codes
tts_supported = tts_langs().keys()

# Page setup
st.set_page_config(page_title="🎙️ Voice ↔ Text Translator", layout="centered")
st.title("🎙️ Voice ↔ Text Translator App")

# Mode selection
mode = st.radio("Choose Mode", ["📝 Text → Voice", "🎤 Voice → Text"])

# Language selection
selected_languages = st.multiselect(
    "🌍 Select languages to translate to",
    list(languages.keys()),
    default=["Telugu", "Tamil", "Hindi"]
)

# =============================
# 📝 TEXT → VOICE
# =============================
if mode == "📝 Text → Voice":
    input_text = st.text_area("✏️ Enter English Text")

    if st.button("🔊 Translate & Speak"):
        if not input_text.strip():
            st.warning("Please type something!")
        else:
            for lang in selected_languages:
                code = languages[lang]

                try:
                    translated = GoogleTranslator(source='en', target=code).translate(input_text)

                    if code in tts_supported:
                        tts = gTTS(translated, lang=code)
                        filename = f"{uuid.uuid4().hex}.mp3"
                        tts.save(filename)

                        # Language name as heading
                        st.markdown(f"### {lang}")

                        with open(filename, "rb") as audio_file:
                            st.audio(audio_file.read(), format="audio/mp3")

                        os.remove(filename)
                    else:
                        st.warning(f"⚠ Audio not supported for {lang} ({code})")

                except Exception as e:
                    st.error(f"❌ Error for {lang}: {e}")

# =============================
# 🎤 VOICE → TEXT
# =============================
else:
    duration = st.slider("🎧 Recording Duration (in seconds)", 3, 10, 5)

    if st.button("🎤 Record & Translate"):
        st.info("Recording... Speak now!")

        try:
            fs = 44100
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                write(temp_audio_file.name, fs, recording)
                wav_path = temp_audio_file.name

            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                detected_text = recognizer.recognize_google(audio_data)

            st.success("📝 Detected Speech:")
            st.write(detected_text)

            for lang in selected_languages:
                code = languages[lang]
                translated = GoogleTranslator(source='auto', target=code).translate(detected_text)
                st.markdown(f"### {lang}")
                st.success(translated)

            os.remove(wav_path)

        except sr.UnknownValueError:
            st.error("❌ Could not understand your voice.")
        except sr.RequestError:
            st.error("❌ Google Speech API is unavailable.")
        except Exception as e:
            st.error(f"❌ Error: {e}")
