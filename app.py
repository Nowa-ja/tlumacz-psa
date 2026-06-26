import streamlit as st
import numpy as np
import wave
import io
import random
from datetime import datetime, timedelta
from gtts import gTTS

# Konfiguracja strony
st.set_page_config(page_title="HauTłumacz v8.0", page_icon="🐕", layout="centered")

# Inicjalizacja czasu ostatniego użycia
if "ostatnie_uzycie" not in st.session_state:
    st.session_state.ostatnie_uzycie = datetime.now()

# Połączona baza tekstów (aplikacja losuje z całej puli automatycznie)
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

st.title("🐕 HauTłumacz v8.0")
st.write("---")

# ==================== SEKCJA GÓRNA: NAGRYWANIE ====================
st.markdown("### 🎙️ Sekcja nagrywania i przetwarzania")

# Dzielimy górny pasek na obszar przycisku i statusu postępu
col_rec, col_status = st.columns([1, 3])

with col_rec:
    # Komponent nagrywania jako minimalistyczny przycisk z czerwoną kropką
    audio_nagrane = st.audio_input("Nagraj")

with col_status:
    if audio_nagrane is not None:
        st.info("🔄 Przetwarzanie dźwięku... Trwa generowanie tłumaczenia.")
    else:
        st.write("◀ Kliknij ikonę, aby rozpocząć rejestrację dźwięku.")

# ==================== LOGIKA I PRZETWARZANIE ====================
if audio_nagrane is not None:
    raw_audio_bytes = audio_nagrane.read()
    
    teraz = datetime.now()
    roznica_czasu = teraz - st.session_state.ostatnie_uzycie
    st.session_state.ostatnie_uzycie = teraz
    
    try:
        # Decyzja o tekście (Główny filtr czasowy + automatyczny wybór)
        if roznica_czasu > timedelta(hours=4):
            wylosowany_tekst = "Hej! Ignorujesz mnie już od ponad 4 godzin! Ta żywiołowa reakcja, piszczenie i obwąchiwanie to nie zabawa – natychmiast zbieraj się i wyjdź ze mną na siku lub kupkę, bo zaraz będzie katastrofa na dywanie!"
        else:
            wylosowany_tekst = random.choice(WSZYSTKIE_TEKSTY)
        
        # Doklejanie automatycznego drugiego zdania
        dodatkowe_zdanie = random.choice(DODATKOWE_ZDANIA)
        pelny_tekst = f"{wylosowany_tekst} {dodatkowe_zdanie}"
        
        # Generowanie dźwięku przez gTTS
        tts = gTTS(text=pelny_tekst, lang='pl')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # ==================== SEKCJA DOLNA: WYNIK ====================
        st.write("---")
        st.markdown("### 📊 Wynik analizy")
        
        # Tworzymy układ dolny: głośnik po lewej, tekst po prawej
        col_glosnik, col_tekst = st.columns([1, 2])
        
        with col_glosnik:
            st.write("🔊 **Odtwórz:**")
            st.audio(fp, format="audio/mp3", autoplay=True)
            
        with col_tekst:
            st.write("💬 **Tłumaczenie tekstowe:**")
            st.subheader(f"*\"{pelny_tekst}\"*")
            
    except Exception as e:
        st.error(f"Wystąpił błąd podczas przetwarzania: {e}")

st.write("---")
st.caption("HauTłumacz v8.0 - Przejrzysty i minimalistyczny interfejs.")
