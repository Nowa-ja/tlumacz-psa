import streamlit as st
import random
from gtts import gTTS
import io

# --- 1. FUNKCJA OCHRONNA (CYFROWY OCHRONIARZ) ---
def sprawdz_haslo():
    """Zwraca True, jeśli użytkownik wpisał poprawne hasło."""
    if "zalogowany" not in st.session_state:
        st.session_state["zalogowany"] = False

    if not st.session_state["zalogowany"]:
        # Ekran blokady przed botami i nieproszonymi gośćmi
        st.subheader("🔒 Dostęp zablokowany")
        haslo = st.text_input("Wprowadź tajne hasło, aby uruchomić HauTłumacza:", type="password")
        if st.button("Zaloguj"):
            # TUTAJ MOŻESZ ZMIENIĆ SWOJE HASŁO (zostaw cudzysłów)
            if haslo == "HauHau-2026":  
                st.session_state["zalogowany"] = True
                st.rerun()
            else:
                st.error("❌ Niepoprawne hasło!")
        return False
    return True

# Ustawienie konfiguracji strony (musi być wywołane na samym początku)
st.set_page_config(page_title="HauTłumacz v7.0", page_icon="🐕")

# --- 2. URUCHOMIENIE BLOKADY I TWOJEGO KODU ---
if sprawdz_haslo():
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
        
        # Generowanie głosu audio w pamięci (zamiast zapisywania pliku na dysku)
        tts = gTTS(text=wylosowany_tekst, lang='pl')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        st.write("### 🔊 Posłuchaj odpowiedzi:")
        st.audio(fp, format="audio/mp3", autoplay=True)

    st.write("---")
    st.caption("Bo dobro pieska jest na pierwszym miejscu.")
