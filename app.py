import streamlit as st
import io
import random
from datetime import datetime, timedelta
from gtts import gTTS

# Czysta, bezpieczna konfiguracja bez wymuszania procesów w tle
st.set_page_config(page_title="HauTłumacz v8.0", page_icon="🐕", layout="centered")

# Inicjalizacja czasu ostatniego użycia
if "ostatnie_uzycie" not in st.session_state:
    st.session_state.ostatnie_uzycie = datetime.now()

# Twoja baza tekstów
WSZYSTKIE_TEKSTY = [
    "I co jeszcze? Może piesek ma ugotować i pozmywać po tobie? To nie ten etap!!!",
    "A gdzie to się bywało? Wyczuwam tutaj jakąś zdzirę i mam nadzieję, że się wytłumaczysz?!",
    "Sikać mi się chce, szybko!",
    "Zaraz narobię ci na twój ładny dywanik, jak się nie pospieszysz.",
    "W co ja się wpakowałem...",
    "Ludzie, jestem sam!",
    "Może znów spotkamy tę rudą? Niezła foczka!",
    "Już nie mogę się doczekać, jak wykopię dołek!",
    "Zrobisz jeszcze jeden krok, a sam zaczniesz warczeć!",
    "To mój teren! Zostaw mnie w spokoju!",
    "Teraz czas na parówkę! No dajesz!",
    "Rzuć piłkę! No rzuć!"
]

DODATKOWE_ZDANIA = [
    "No i co ty na to człowiek? Przemyśl to sobie.",
    "A teraz masuj mnie za uchem, bo się obrażę.",
    "I pamiętaj, widzę wszystko co tam jesz w kuchni!",
    "Czas ucieka, a miska sama się nie napełni.",
    "Zrozumiano, czy mam szczeknąć to jeszcze raz?",
    "I nie patrz tak na mnie, tylko wyciągaj smaczki!",
    "Dobra, koniec gadania, bierzmy się za konkrety."
]

# Style CSS wprowadzające Twój wymarzony zielony szablon
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f5; }
    h1 { color: #1e4620 !important; text-align: center; }
    .stAudioInput { border: 2px dashed #81c784 !important; border-radius: 12px; padding: 10px; background-color: #e8f5e9; }
    </style>
""", unsafe_allow_html=True)

st.title("🐕 HauTłumacz v8.0")
st.write("---")

# ==================== SEKCJA GÓRNA: NAGRYWANIE ====================
st.markdown("### 🎙️ Sekcja nagrywania i przetwarzania")

col_rec, col_status = st.columns([1, 1])

with col_rec:
    audio_nagrane = st.audio_input("Nagraj")

with col_status:
    if audio_nagrane is not None:
        st.success("✅ Przetworzono pomyślnie!")
    else:
        st.info("◀ Kliknij kropkę, aby nagrać.")

# ==================== SEKCJA DOLNA: WYNIK ====================
if audio_nagrane is not None:
    teraz = datetime.now()
    roznica_czasu = teraz - st.session_state.ostatnie_uzycie
    st.session_state.ostatnie_uzycie = teraz
    
    # Wybór wypowiedzi
    if roznica_czasu > timedelta(hours=4):
        wylosowany_tekst = "Hej! Ignorujesz mnie już od ponad 4 godzin! Ta żywiołowa reakcja, piszczenie i obwąchiwanie to nie zabawa – natychmiast zbieraj się i wyjdź ze mną na siku lub kupkę!"
    else:
        wylosowany_tekst = random.choice(WSZYSTKIE_TEKSTY)
    
    pelny_tekst = f"{wylosowany_tekst} {random.choice(DODATKOWE_ZDANIA)}"
    
    # Generowanie głosu lektora
    tts = gTTS(text=pelny_tekst, lang='pl')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    
    st.write("---")
    st.markdown("### 📊 Wynik analizy")
    
    # Układ kolumn: głośnik po lewej, tekst po prawej
    col_glosnik, col_tekst = st.columns([1, 2])
    
    with col_glosnik:
        st.write("🔊 **Odtwórz:**")
        st.audio(fp, format="audio/mp3", autoplay=True)
        
    with col_tekst:
        st.write("💬 **Tłumaczenie:**")
        st.success(pelny_tekst)

st.write("---")
st.caption("HauTłumacz v8.0 - Stabilna wersja chmurowa.")
