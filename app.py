import streamlit as st
import numpy as np
import wave
import io
import random
from datetime import datetime, timedelta
from gtts import gTTS

st.set_page_config(page_title="HauTłumacz v7.0 - Troska i Zazdrość", page_icon="🐕", layout="centered")

# Initialize session state for tracking time gaps between uses
if "ostatnie_uzycie" not in st.session_state:
    st.session_state.ostatnie_uzycie = datetime.now()

# --- NOWOŚĆ: BAZA DODATKOWYCH SAMOCZYNNYCH ZDAŃ ---
DODATKOWE_ZDANIA = [
    "No i co ty na to człowiek? Przemyśl to sobie.",
    "A teraz masuj mnie za uchem, bo się obrażę.",
    "I pamiętaj, widzę wszystko co tam jesz w kuchni!",
    "Czas ucieka, a miska sama się nie napełni.",
    "Zrozumiano, czy mam szczeknąć to jeszcze raz?",
    "I nie patrz tak na mnie, tylko wyciągaj smaczki!",
    "Dobra, koniec gadania, bierzmy się za konkrety."
]

# --- ROZBUDOWANA BAZA TEKSTÓW Z NOWYMI FUNKCJAMI ---
BAZA_TŁUMACZEŃ = {
    "LUDZKIE_MARUDZENIE": {
        "status": "🙄 WYKRYTO: CZŁOWIEK MARUDZI",
        "kolor": "warning",
        "teksty": [
            "I co jeszcze? Może piesek ma ugotować i pozmywać po tobie? To nie ten etap!!! Już nad tym pracują i niedługo komunikacja będzie obustronna, ale na razie jedynie możesz nagrywać pieska i słuchać co chodzi mu po głowie i reagować na to. Więc nagraj, gdy szczeka lub warczy. I nie zapomnij dać mu jego smakołyk by chciał do Ciebie mówić"
        ]
    },
    "INTENSYWNE_NIUCHANIE": {
        "status": "🕵️‍♂️ STATUS: ZAZDROŚĆ I DOCHODZENIE (Węch śledczy)",
        "kolor": "error",
        "teksty": [
            "A gdzie to się bywało? Wyczuwam tutaj jakąś zdzirę i mam nadzieję, że się wytłumaczysz?! Żądamy racjonalnego wyjaśnienia i przeprosin – najlepiej wykwintnego obiadu!"
        ]
    },
    "ALARM_SIKU": {
        "status": "🚨 PILNY ALERT: POTRZEBA FIZJOLOGICZNA!",
        "kolor": "error",
        "teksty": [
            "Hej! Ignorujesz mnie już od ponad 4 godzin! Ta żywiołowa reakcja, piszczenie i obwąchiwanie to nie zabawa – natychmiast zbieraj się i wyjdź ze mną na siku lub kupkę, bo zaraz będzie katastrofa na dywanie!"
        ]
    },
    "PORANNE_SKANOWANIE": {
        "status": "🌅 PORANNE WYMUSZANIE (Pilne!)",
        "kolor": "error",
        "teksty": ["Sikać mi się chce, szybko!", "Zaraz narobię ci na twój ładny dywanik, jak się nie pospieszysz."]
    },
    "WYCIE_SAMOTNOSC": {
        "status": "🏠 WYCIE W SAMOTNOŚCI",
        "kolor": "warning",
        "teksty": ["W co ja się wpakowałem...", "Ludzie, jestem sam!", "Ludzie, tutaj gwałcą, pomóżcie!"]
    },
    "EKSCYTACJA_SPACER": {
        "status": "🔥 SKANOWANIE Z EKSCYTACJI",
        "kolor": "info",
        "teksty": ["Może znów spotkamy tę rudą? Niezła foczka!", "Już nie mogę się doczekać, jak wykopię dołek!"]
    },
    "WARCZENIE_AGRESJA": {
        "status": "🔴 STATUS: AGRESJA OSTRZEGAWCZA",
        "kolor": "error",
        "teksty": ["Zrobisz jeszcze jeden krok, a sam zaczniesz warczeć!", "To mój teren! Zostaw mnie w spokoju!"]
    },
    "ZABAWA_NORMALNA": {
        "status": "🟢 STATUS: ZABAWA / RADOŚĆ",
        "kolor": "success",
        "teksty": ["Teraz czas na parówkę! No dajesz!", "Rzuć piłkę! No rzuć!"]
    }
}

st.title("🐕 HauTłumacz v7.0")
st.subheader("Edycja: Opieka nad psem + Wykrywanie zazdrości")

st.write("---")
tryb = st.radio(
    "👇 Co teraz robi pies lub człowiek?", 
    [
        "🐕 PIES (Szczekanie / Warczenie / Piszczenie)", 
        "👃 INTENSYWNE OBWĘCHIWANIE (Niuchanie przy ubraniu)",
        "👨 CZŁOWIEK (Wydawanie rozkazów)"
    ]
)
st.write("---")

st.write("### 🎤 Kliknij ikonę mikrofonu poniżej i nagraj dźwięk:")
audio_nagrane = st.audio_input("Nagraj dźwięk")

if audio_nagrane is not None:
    raw_audio_bytes = audio_nagrane.read()
    
    # Obliczanie przerwy od ostatniego kliknięcia
    teraz = datetime.now()
    roznica_czasu = teraz - st.session_state.ostatnie_uzycie
    st.session_state.ostatnie_uzycie = teraz  # Zapisujemy obecny czas jako ostatni
    
    with st.spinner('Przetwarzanie i generowanie głosu...'):
        try:
            # 1. WYBÓR: Tryb Człowieka
            if "CZŁOWIEK" in tryb:
                wynik = BAZA_TŁUMACZEŃ["LUDZKIE_MARUDZENIE"]
                
            # 2. WYBÓR: Tryb Intensywnego Niuchania
            elif "OBWĘCHIWANIE" in tryb:
                wynik = BAZA_TŁUMACZEŃ["INTENSYWNE_NIUCHANIE"]
                
            # 3. WYBÓR: Tryb Psa (z filtrem 4-godzinnym)
            else:
                if roznica_czasu > timedelta(hours=4):
                    wynik = BAZA_TŁUMACZEŃ["ALARM_SIKU"]
                else:
                    with wave.open(io.BytesIO(raw_audio_bytes), "rb") as wf:
                        sampwidth = wf.getsampwidth()
                        n_frames = wf.getnframes()
                        data = wf.readframes(n_frames)
                        
                        if sampwidth == 2:
                            audio_data = np.frombuffer(data, dtype=np.int16)
                        else:
                            audio_data = np.frombuffer(data, dtype=np.uint8).astype(np.int16) - 128
                    
                    amplituda = np.abs(audio_data)
                    maksimum = np.max(amplituda) if len(amplituda) > 0 else 0
                    
                    if maksimum < 50:
                        st.error("Cisza... Nagraj się głośniej.")
                        st.stop()
                    
                    prog = maksimum * 0.15
                    glosne_momenty = np.sum(amplituda > prog)
                    procent_czasu = (glosne_momenty / len(amplituda)) * 100
                    godzina_teraz = datetime.now().hour
                    
                    if procent_czasu < 8.0:
                        wynik = BAZA_TŁUMACZEŃ["WARCZENIE_AGRESJA"]
                    else:
                        if 5 <= godzina_teraz <= 10:
                            wynik = BAZA_TŁUMACZEŃ["PORANNE_SKANOWANIE"]
                        elif procent_czasu > 18.0:
                            wynik = BAZA_TŁUMACZEŃ["EKSCYTACJA_SPACER"]
                        else:
                            wynik = BAZA_TŁUMACZEŃ["ZABAWA_NORMALNA"]
            
            # Losowanie podstawowego tekstu
            wylosowany_tekst = random.choice(wynik["teksty"])
            
            # --- MODYFIKACJA: Samoczynne generowanie dodatkowego zdania ---
            dodatkowe_zdanie = random.choice(DODATKOWE_ZDANIA)
            pelny_tekst = f"{wylosowany_tekst} {dodatkowe_zdanie}"
            
            st.write("---")
            if wynik["kolor"] == "success": st.success(wynik["status"])
            elif wynik["kolor"] == "warning": st.warning(wynik["status"])
            elif wynik["kolor"] == "error": st.error(wynik["status"])
            else: st.info(wynik["status"])
            
            st.markdown(f"### 💬 Przemyślenia:")
            st.subheader(f"*\"{pelny_tekst}\"*")
            
            # --- GENEROWANIE AUDIO (Z pełnym połączonym tekstem) ---
            tts = gTTS(text=pelny_tekst, lang='pl')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            st.write("### 🔊 Posłuchaj odpowiedzi:")
            st.audio(fp, format="audio/mp3", autoplay=True)
            
        except Exception as e:
            st.error(f"Wystąpił problem: {e}")

st.write("---")
st.caption("HauTłumacz v7.0 - Bo dobro pieska jest na pierwszym miejscu.")
