import streamlit as st
import io
import random
from datetime import datetime, timedelta
from gtts import gTTS

# --- BEZPIECZNE IMPORTOWANIE BIBLIOTEK AKUSTYCZNYCH ---
TRYB_ANALIZY = True
try:
    import numpy as np
    from scipy.io import wavfile
except ImportError:
    TRYB_ANALIZY = False

# --- BEZPIECZNA KONFIGURACJA STRONY ---
st.set_page_config(page_title="HauTłumacz PRO v9.5", page_icon="🐕", layout="centered")

if "ostatnie_uzycie" not in st.session_state:
    st.session_state.ostatnie_uzycie = datetime.now()

# --- ANALIZATOR AUDIO ---
def analizuj_czestotliwosc(audio_bytes):
    if not TRYB_ANALIZY:
        return 600.0
    try:
        sample_rate, data = wavfile.read(io.BytesIO(audio_bytes))
        if len(data.shape) > 1:
            data = data[:, 0]
        fft_spectrum = np.fft.rfft(data)
        freq = np.fft.rfftfreq(len(data), d=1.0/sample_rate)
        szczytowa_indeks = np.argmax(np.abs(fft_spectrum))
        return freq[szczytowa_indeks]
    except:
        return 600.0

# ==================== BAZY TEKSTÓW ====================
TEKSTY_GIGANT = [
    "Słyszę potężny bas! Mówi do ciebie rasa olbrzymia (Mastif/Dog). Ziemia drży, a ty nadal nie wyciągasz smaczków?",
    "Z moją masą nie ma żartów człowieku. Jeden mój krok to trzęsienie ziemi, więc ruszaj się szybciej z tą miską!",
    "Uwaga, nadchodzi król kanapy! Ustąp miejsca gabarytom, bo zaraz się na tobie położę."
]

TEKSTY_DUZY_OWCZAREK = [
    "Uwaga, mówi potężny Owczarek/Labrador! Szacunek musi być. Dawaj parówkę albo sam ją sobie wezmę!",
    "Słyszę, że szukasz guza człowieku. Zrób jeszcze jeden krok, a sam zaczniesz warczeć!",
    "To mój teren! Weź ty się ogarnij i nie podchodź bez pozwolenia, dopóki nie masz meldunku."
]

TEKSTY_SREDNI_BEAGLE = [
    "Wykryto ton rasy średniej (Beagle/Spaniel/Border)! Mam idealne proporcje sprytu i energii.",
    "Może i nie jestem gigantem, ale za to potrafię wywęszyć każdą parówkę w promieniu kilometra!",
    "Zaraz zrobię ci tutaj małe przemeblowanie, jeśli natychmiast nie pójdziemy pobiegać!"
]

TEKSTY_MALUCH = [
    "Wykryto małego spryciarza (Mops/Buldog/Jack Russell)! Mały ciałem, ale potężny duchem!",
    "Nie patrz tak na mnie z góry! Moje nogi są krótkie, ale gonić kota potrafię szybciej niż myślisz.",
    "Właśnie opracowałem plan, jak przejąć kontrolę nad lodówką. Potrzebuję tylko twojego odcisku palca."
]

TEKSTY_MINIATURA_JAMNIK = [
    "Może i jestem mały jak parówka, ale gniew mam wielki! Cofnij się!",
    "Jestem małym, wściekłym demonem! Nie ignoruj mojego piskliwego majestatu, bo ugryzę w kostkę!",
    "Właśnie się dowiedziałem, że sąsiad chodzi na lewiznę, a ty mnie tu denerwujesz!"
]

TEKSTY_PORANNE = [
    "Pospiesz się, bo się posikam!",
    "Szybko, bo za chwilę będzie śmierdząca niespodzianka!",
    "Pospiesz się, bo narobię ci na ten nowy dywanik!",
    "Sikać mi się chce, szybko!"
]

TEKSTY_WIECZORNE = [
    "Ludzie, jestem sam!",
    "Niech ktoś pomoże!",
    "Jest tam kto?",
    "Pomocy tutaj nawaliłem i strasznie śmierdzi!",
    "W co ja się wpakowałem...",
    "Zaraz narobię ci na twój ładny dywanik, jak się nie pospieszysz."
]

TEKSTY_DZIENNE = [
    "Teraz czas na parówkę! No dajesz!",
    "Rzuć piłkę! No rzuć!",
    "Może znów spotkamy tę rudą? Niezła foczka!",
    "Już nie mogę się doczekać, jak wykopię dołek!",
    "I co jeszcze? Może piesek ma ugotować i pozmywać po tobie? To nie ten etap!!!",
    "A gdzie to się bywało? Wyczuwam tutaj jakąś zdzirę i mam nadzieję, że się wytłumaczysz?!",
    "To mój teren! Zostaw mnie w spokoju!"
]

DODATKOWE_ZDANIA = [
    "No i co ty na to człowiek? Przemyśl to sobie.",
    "A teraz masuj mnie za uchem, bo się obrażę.",
    "Zrozumiano, czy mam szczeknąć to jeszcze raz?",
    "I nie patrz tak na mnie, tylko wyciągaj smaczki!",
    "Dobra, koniec gadania, bierzmy się za konkrety."
]

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f5; }
    h1 { color: #1e4620 !important; text-align: center; margin-top: 10px; }
    .stAudioInput { border: 2px dashed #81c784 !important; border-radius: 12px; padding: 10px; background-color: #e8f5e9; }
    .logo-container { display: flex; justify-content: center; margin-bottom: 10px; }
    .logo-img { border-radius: 24px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

LINK_DO_TWOJEGO_ZDJECIA = "https://ibb.co" 

st.markdown(f"""
    <div class="logo-container">
        <img src="{LINK_DO_TWOJEGO_ZDJECIA}" width="180" class="logo-img">
    </div>
""", unsafe_allow_html=True)

st.title("🐕 HauTłumacz TURBO v9.5")
st.write("---")

st.markdown("### 🎙️ Sekcja nagrywania i przetwarzania")
st.caption("Uruchom nagrywanie, gdy pies wydaje dźwięki. Przyspieszony lektor automatycznie odtworzy czyste tłumaczenie.")

audio_nagrane = st.audio_input("Nagraj")

if audio_nagrane is not None:
    audio_bytes = audio_nagrane.read()
    wykryte_hz = analizuj_czestotliwosc(audio_bytes)
    
    teraz = datetime.now()
    godzina_teraz = teraz.hour
    
    wylosowany = ""
    naglowek_ekranu = ""
    
    # --- NOWA LOGIKA SELEKCJI TEKSTU DO CZYTANIA (BEZ SŁOWA SZCZEK) ---
    if TRYB_ANALIZY:
        st.sidebar.metric(label="Wykryta częstotliwość", value=f"{int(wykryte_hz)} Hz")
        
        if wykryte_hz < 200:
            st.sidebar.success("🎯 Klasyfikacja: Rasa Olbrzymia (Bas)")
            wylosowany = random.choice(TEKSTY_GIGANT)
            naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Bas Giganta]"
        elif 200 <= wykryte_hz < 450:
            st.sidebar.success("🎯 Klasyfikacja: Rasa Duża (Owczarek/Labrador)")
            wylosowany = random.choice(TEKSTY_DUZY_OWCZAREK)
            naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Owczarkowy ton]"
        elif 450 <= wykryte_hz < 800:
            st.sidebar.info("🎯 Klasyfikacja: Rasa Średnia (Beagle/Border)")
            wylosowany = random.choice(TEKSTY_SREDNI_BEAGLE)
            naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Średni szczek]"
        elif 800 <= wykryte_hz < 1200:
            st.sidebar.warning("🎯 Klasyfikacja: Rasa Mała (Mops/Jack Russell)")
            wylosowany = random.choice(TEKSTY_MALUCH)
            naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Żwawy szczek]"
        else:
            st.sidebar.warning("🎯 Klasyfikacja: Rasa Miniaturowa (Jamnik/York)")
            wylosowany = random.choice(TEKSTY_MINIATURA_JAMNIK)
            naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Jamnikowy pisk]"
    else:
        if 5 <= godzina_teraz < 12:
            wylosowany = random.choice(TEKSTY_PORANNE)
        elif 20 <= godzina_teraz or godzina_teraz < 5:
            wylosowany = random.choice(TEKSTY_WIECZORNE)
        else:
            wylosowany = random.choice(TEKSTY_DZIENNE)
        naglowek_ekranu = "[Tłumaczenie]"

    # Tekst, który pojawi się na ekranie komputera
    tekst_do_wyswietlenia = f"{naglowek_ekranu}: {wylosowany} {random.choice(DODATKOWE_ZDANIA)}"
    
    # CZYSTY tekst wysyłany do lektora (wykasowane znaczniki techniczne i kropki blokujące tempo)
    tekst_do_czytania = f"{wylosowany} {random.choice(DODATKOWE_ZDANIA)}".replace(".", ",").replace("!", ",")

    # --- GENEROWANIE I DODATKOWE PRZYSPIESZENIE GŁOSU O 15% ---
    tts = gTTS(text=tekst_do_czytania, lang='pl', slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    
    # ==================== SEKCJA WYNIKU ====================
    st.write("---")
    st.markdown("### 📊 Wynik analizy")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("🔊 **Odtwórz głosowo:**")
        st.audio(fp, format="audio/mp3", autoplay=True)
    with col2:
        st.write("💬 **Tłumaczenie tekstowe:**")
        st.success(tekst_do_wyswietlenia)

# ==================== STOPKA Z PEŁNYM REGULAMINEM ====================
st.write("---")
col_foot1, col_foot2 = st.columns(2)
with col_foot1:
    st.caption("HauTłumacz TURBO v9.5 - Stabilna wersja chmurowa.")
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
