import streamlit as st
import io
import random
import numpy as np
from scipy.io import wavfile
from datetime import datetime, timedelta
from gtts import gTTS

# --- BEZPIECZNA KONFIGURACJA STRONY ---
st.set_page_config(page_title="HauTłumacz PRO v9.0", page_icon="🐕", layout="centered")

# --- INICJALIZACJA PAMIĘCI ---
if "ostatnie_uzycie" not in st.session_state:
    st.session_state.ostatnie_uzycie = datetime.now()

# --- PRAWDZIWY AKUSTYCZNY ANALIZATOR AUDIO (FFT) ---
def analizuj_czestotliwosc(audio_bytes):
    try:
        # Odczytujemy plik wav przesłany przez st.audio_input
        sample_rate, data = wavfile.read(io.BytesIO(audio_bytes))
        
        # Jeśli audio jest stereo, bierzemy tylko jeden kanał
        if len(data.shape) > 1:
            data = data[:, 0]
            
        # Wykonujemy Szybką Transformatę Fouriera (FFT)
        fft_spectrum = np.fft.rfft(data)
        freq = np.fft.rfftfreq(len(data), d=1.0/sample_rate)
        
        # Znajdujemy częstotliwość, która ma największą głośność (szczyt)
        szczytowa_indeks = np.argmax(np.abs(fft_spectrum))
        glowna_czestotliwosc = freq[szczytowa_indeks]
        
        return glowna_czestotliwosc
    except Exception as e:
        # W razie błędu odczytu (np. cisza) zwracamy losowy ton średni
        return 600.0

# --- BAZY TEKSTÓW DOPASOWANE DO RASY I EMOCJI ---

TEKSTY_NISKIE_OWCZAREK = [
    "Uwaga, mówi potężny Owczarek! Szacunek musi być. Dawaj parówkę albo sam będę musiał ją sobie wziąć!",
    "Słyszę, że szukasz guza człowieku. Zrób jeszcze jeden krok, a sam zaczniesz warczeć!",
    "To mój teren! Weź ty się ogarnij i nie podchodź bez pozwolenia."
]

TEKSTY_WYSOKIE_JAMNIK = [
    "Może i jestem mały jak parówka, ale gniew mam wielki! Cofnij się!",
    "Jestem małym, wściekłym demonem! Nie ignoruj mojego piskliwego majestatu!",
    "Właśnie się dowiedziałem, że sąsiad chodzi na lewiznę, a ty mnie tu denerwujesz!"
]

TEKSTY_PORANNE = [
    "Pospiesz się, bo się posikam!",
    "Szybko, bo za chwilę będzie śmierdząca niespodzianka na dywanie!",
    "Sikać mi się chce, no ile można leżeć!"
]

TEKSTY_WIECZORNE = [
    "Ludzie, jestem sam! Niech ktoś pomoże!",
    "Zaraz narobię ci na twój ładny dywanik, jak się nie pospieszysz i nie przyjdziesz przytulić."
]

DODATKOWE_ZDANIA = [
    "No i co ty na to człowiek? Przemyśl to sobie.",
    "A teraz masuj mnie za uchem, bo się obrażę.",
    "Zrozumiano, czy mam szczeknąć to jeszcze raz?"
]

# --- STYLE CSS DLA ZIELONEGO INTERFEJSU ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f5; }
    h1 { color: #1e4620 !important; text-align: center; margin-top: 10px; }
    .stAudioInput { border: 2px dashed #81c784 !important; border-radius: 12px; padding: 10px; background-color: #e8f5e9; }
    .logo-container { display: flex; justify-content: center; margin-bottom: 10px; }
    .logo-img { border-radius: 24px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# --- WYŚWIETLANIE LOGO (Zmień link na bezpośredni do pliku graficznego!) ---
LINK_DO_TWOJEGO_ZDJECIA = "https://ibb.co" 

st.markdown(f"""
    <div class="logo-container">
        <img src="{LINK_DO_TWOJEGO_ZDJECIA}" width="180" class="logo-img">
    </div>
""", unsafe_allow_html=True)

st.title("🐕 HauTłumacz PRO v9.0")
st.write("---")

# ==================== SEKCJA NAGRYWANIA ====================
st.markdown("### 🎙️ Sekcja nagrywania i przetwarzania")
st.caption("Uruchom nagrywanie, gdy pies wydaje dźwięki. Prawdziwa analiza częstotliwości audio (FFT).")

audio_nagrane = st.audio_input("Nagraj psa")

if audio_nagrane is not None:
    # Pobieramy bajty z nagrania
    audio_bytes = audio_nagrane.read()
    
    # Mierzymy herce (Hz) przy użyciu transformaty Fouriera
    wykryte_hz = analizuj_czestotliwosc(audio_bytes)
    
    teraz = datetime.now()
    godzina_teraz = teraz.hour
    pelny_tekst = ""
    
    st.sidebar.metric(label="Wykryta częstotliwość dominująca", value=f"{int(wykryte_hz)} Hz")

    # --- LOGIKA DECYZYJNA NA BAZIE CZĘSTOTLIWOŚCI (FIZYKA) ---
    
    # 1. WYKRYTO BARDZO NISKI TON (Poniżej 300 Hz) -> Owczarek / Duży pies warczy
    if wykryte_hz < 300:
        st.sidebar.success("🎯 Klasyfikacja: Niski ton (Duży pies / Warczenie)")
        wylosowany = random.choice(TEKSTY_NISKIE_OWCZAREK)
        pelny_tekst = f"[{int(wykryte_hz)} Hz - Owczarkowy bas]: {wylosowany} {random.choice(DODATKOWE_ZDANIA)}"
        
    # 2. WYKRYTO BARDZO WYSOKI TON (Powyżej 1200 Hz) -> Jamnik / Pisk / Skomlenie
    elif wykryte_hz > 1200:
        st.sidebar.warning("🎯 Klasyfikacja: Wysoki ton (Mały pies / Pisk)")
        wylosowany = random.choice(TEKSTY_WYSOKIE_JAMNIK)
        pelny_tekst = f"[{int(wykryte_hz)} Hz - Jamnikowy pisk]: {wylosowany} {random.choice(DODATKOWE_ZDANIA)}"
        
    # 3. TON ŚREDNI -> Sprawdzamy czas systemowy (Tradycyjne tłumaczenie godzinowe)
    else:
        st.sidebar.info("🎯 Klasyfikacja: Ton średni (Klasyczny szczek)")
        if 5 <= godzina_teraz < 12:
            wylosowany = random.choice(TEKSTY_PORANNE)
        elif 20 <= godzina_teraz or godzina_teraz < 5:
            wylosowany = random.choice(TEKSTY_WIECZORNE)
        else:
            wylosowany = "Rzuć piłkę! No dajesz! Albo chociaż daj parówkę!"
            
        pelny_tekst = f"[Szczek średni]: {wylosowany} {random.choice(DODATKOWE_ZDANIA)}"

    # --- GENEROWANIE AUDIO PRZEZ LEKTORA ---
    tts = gTTS(text=pelny_tekst, lang='pl')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    
    # ==================== WYNIK DETEKCJI ====================
    st.write("---")
    st.markdown("### 📊 Wynik analizy akustyczno-humorystycznej")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("🔊 **Odtwórz głosowo:**")
        st.audio(fp, format="audio/mp3", autoplay=True)
    with col2:
        st.write("💬 **Tłumaczenie tekstowe:**")
        st.success(pelny_tekst)

# ==================== STOPKA Z PEŁNYM REGULAMINEM ====================
st.write("---")
col_foot1, col_foot2 = st.columns(2)
with col_foot1:
    st.caption("HauTłumacz PRO v9.0 - Stabilna wersja chmurowa z FFT.")
with col_foot2:
    if st.button("📝 Regulamin strony"):
        st.info("""
        **Regulamin i informacje o serwisie hauhau.online**
        
        Drogi użytkowniku.
        Jest mi bardzo miło gościć Ciebie na stronie „hauhau.online” i liczę na to, że efekt mojej pracy sprawi Ci wiele przyjemności w trakcie użytkowania tłumacza oraz przyczyni się do pogłębienia relacji między psiakiem a człowiekiem. 
        
        - Na stronie hauhau.online nie są gromadzone żadne dane oraz dźwięki wydobywane przez zwierzęta, które nagrasz w celu przetłumaczenia. 
        - Na stronie hauhau.online nie są gromadzone żadne tłumaczenia, a każdy kolejny proces nagrywania kasuje nagranie poprzednie tak samo jak opuszczenie strony. Więc jeśli chcesz zachować tekst, utrwal go samodzielnie.
        
        Cały proces tłumaczenia odbywa się na bieżąco i jest on wynikiem klasyfikacji przez algorytm i dobierania słów zapisanych w bazie danych, która z każdym dniem powiększa się o kolejne zwroty i słowa. 
        
        W celu przetłumaczenia bardziej skomplikowanych dźwięków zapraszam do kontaktu drogą elektroniczną pod adresem: hauhau.kontakt@gmail.com w celu ustalenia warunków tłumaczenia przysięgłego – (zastrzegając, że czas odpowiedzi może być dłuższy). Dołożę wszelkich starań, aby tłumaczenie spełniało najwyższe standardy. 
        
        Życzę wszystkim wiele radości z użytkowania tłumacza!
        """)
