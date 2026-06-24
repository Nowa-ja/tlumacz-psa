import streamlit as st
import random
from gtts import gTTS
import io

st.set_page_config(page_title="HauTłumacz v7.0", page_icon="🐕")

st.title("🐕 HauTłumacz v7.0")
st.subheader("Edycja: Opieka nad psem")

TEKSTY = [
    "Teraz czas na parówkę! No dajesz!",
    "Rzuć piłkę! No rzuć!",
    "Sikać mi się chce, szybko!",
    "To mój teren! Zostaw mnie w spokoju!",
    "No co jest, zauważ moje potrzeby."
]

tryb = st.radio(
    "👇 Co teraz robi pies?", 
    ["🐕 Szczeka", "👃 Niucha", "👨 Człowiek marudzi"]
)

st.write("### 🎤 Nagraj dźwięk poniżej:")
audio_nagrane = st.audio_input("Nagraj psa")

if audio_nagrane is not None:
    wylosowany_tekst = random.choice(TEKSTY)
    
    st.success("🟢 STATUS: PRZETŁUMACZONO")
    st.markdown(f"### 💬 Przemyślenia:")
    st.subheader(f"*\"{wylosowany_tekst}\"*")
    
    tts = gTTS(text=wylosowany_tekst, lang='pl')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    
    st.write("### 🔊 Posłuchaj odpowiedzi:")
    st.audio(fp, format="audio/mp3", autoplay=True)

st.write("---")
st.caption("Bo dobro pieska jest na pierwszym miejscu.")

