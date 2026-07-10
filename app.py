import streamlit as st
import io
import random
from datetime import datetime, timedelta
from gtts import gTTS

# --- BEZPIECZNA KONFIGURACJA STRONY ---
st.set_page_config(page_title="HauTłumacz v8.0", page_icon="🐕", layout="centered")

# --- INICJALIZACJA LICZNIKÓW I PAMIĘCI ---
if "ostatnie_uzycie" not in st.session_state:
    st.session_state.ostatnie_uzycie = datetime.now()
if "licznik_prob_ludzkich" not in st.session_state:
    st.session_state.licznik_prob_ludzkich = 0

# --- BAZY TEKSTÓW DOPASOWANE AUTOMATYCZNIE DO PORY DNIA ---

# Wywoływane rano (5:00 - 11:59) - gdy człowiek leży, a pies popiskuje, bo chce na pole
TEKSTY_PORANNE = [
    "Pospiesz się, bo się posikam!",
    "Szybko, bo za chwilę będzie śmierdząca niespodzianka!",
    "Pospiesz się, bo narobię ci na ten nowy dywanik!",
    "Sikać mi się chce, szybko!"
]

# Wywoływane wieczorem i w nocy (20:00 - 4:59) - symulacja wycia psa za ścianą
TEKSTY_WIECZORNE_WYCIE = [
    "Ludzie, jestem sam!",
    "Niech ktoś pomoże!",
    "Jest tam kto?",
    "Pomocy tutaj nawaliłem i strasznie śmierdzi!",
    "W co ja się wpakowałem...",
    "Zaraz narobię ci na twój ładny dywanik, jak się nie pospieszysz."
]

# Wywoływane w ciągu dnia (12:00 - 19:59) - normalne szczekanie, radość, żarty
TEKSTY_DZIENNE = [
    "Teraz czas na parówkę! No dajesz!",
    "Rzuć piłkę! No rzuć!",
    "Może znów spotkamy tę rudą? Niezła foczka!",
    "Już nie mogę się doczekać, jak wykopię dołek!",
    "Właśnie się dowiedziałem, że nasz sąsiad chodzi na lewiznę!",
    "I co jeszcze? Może piesek ma ugotować i pozmywać po tobie? To nie ten etap!!!",
    "A gdzie to się bywało? Wyczuwam tutaj jakąś zdzirę i mam nadzieję, że się wytłumaczysz?!",
    "To mój teren! Zostaw mnie w spokoju!",
    "Zrobisz jeszcze jeden krok, a sam zaczniesz warczeć!"
]

DODATKOWE_ZDANIA = [
    "No i co ty na to człowiek? Przemyśl to sobie.",
    "A teraz masuj mnie za uchem, bo się obrażę.",
    "Zrozumiano, czy mam szczeknąć to jeszcze raz?",
    "I nie patrz tak na mnie, tylko wyciągaj smaczki!",
    "Dobra, koniec gadania, bierzmy się za konkrety."
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

# --- WYŚWIETLANIE LOGO Z IMGBB ---
LINK_DO_TWOJEGO_ZDJECIA = "https://ibb.co" 

st.markdown(f"""
    <div class="logo-container">
        <img src="{LINK_DO_TWOJEGO_ZDJECIA}" width="180" class="logo-img">
    </div>
""", unsafe_allow_html=True)

st.title("🐕 HauTłumacz v8.0")
st.write("---")

# ==================== SEKCJA NAGRYWANIA ====================
st.markdown("### 🎙️ Sekcja nagrywania i przetwarzania")
st.caption("Uruchom nagrywanie, gdy pies wydaje dźwięki. Inteligentny algorytm automatycznie dopasuje kontekst.")

col_rec, col_status = st.columns(2)

with col_rec:
    audio_nagrane = st.audio_input("Nagraj")

with col_status:
    if audio_nagrane is not None:
        st.success("✅ Wykryto sygnał audio!")
    else:
        st.info("◀ Kliknij kropkę, aby zarejestrować dźwięk.")

# ==================== LOGIKA DETEKCJI I INTELIGENCJI ALGORYTMU ====================
if audio_nagrane is not None:
    teraz = datetime.now()
    roznica_czasu = teraz - st.session_state.ostatnie_uzycie
    st.session_state.ostatnie_uzycie = teraz
    
    pelny_tekst = ""
    
    # Symulujemy losowe wykrywanie typu mowy ludzkiej w tle (Instrukcja I, II, III)
    typ_glosu = random.choice(["pies", "meski_rozkaz", "zenski_rozkaz", "stado", "pozytywne_emocje"])
    
    # Zwiększamy licznik, jeśli nagrania następują szybko po sobie
    st.session_state.licznik_prob_ludzkich += 1
    
    # 1. INSTRUKCJA I: Głos Męski + Tryb rozkazujący
    if typ_glosu == "meski_rozkaz":
        if st.session_state.licznik_prob_ludzkich == 1:
            pelny_tekst = "Niestety nie mogę przetłumaczyć nagrania, bo w tle słyszę barana. Pamiętaj, że abym mógł przetłumaczyć dźwięki pieska, to w tle nie może być żadnych zakłóceń. Proszę nagraj swojego pupila."
        elif st.session_state.licznik_prob_ludzkich == 2:
            pelny_tekst = "Niestety nie mogę przetłumaczyć nagrania, bo słyszę osła. Przypominam, że jakość tłumaczenia zależna jest od czystego dźwięku zwierzaka bez żadnych zakłóceń w tle baranów, osłów i innych ulungów. Proszę nagraj swojego pupila."
        else:
            pelny_tekst = "Przypominam, że jakość tłumaczenia zależna jest od czystego dźwięku zwierzaka bez żadnych zakłóceń w tle baranów, osłów i innych ulungów. Proszę nagraj swojego pupila."

    # 2. INSTRUKCJA II: Głos Żeński + Tryb rozkazujący
    elif typ_glosu == "zenski_rozkaz":
        if st.session_state.licznik_prob_ludzkich == 1:
            pelny_tekst = "Niestety nie mogę przetłumaczyć nagrania, bo w tle słyszę barana. Pamiętaj, że abym mógł przetłumaczyć dźwięki pieska, to w tle nie może być żadnych zakłóceń. Proszę nagraj swojego pupila."
        elif st.session_state.licznik_prob_ludzkich == 2:
            pelny_tekst = "Niestety nie mogę przetłumaczyć nagrania, bo słyszę jakąś suczkę. Przypominam, że jakość tłumaczenia zależna jest od czystego dźwięku zwierzaka bez żadnych zakłóceń w tle baranów, osłów i innych ulungów. Proszę nagraj swojego pupila."
        else:
            pelny_tekst = "Przypominam, że jakość tłumaczenia zależna jest od czystego dźwięku zwierzaka bez żadnych zakłóceń w tle foczek, suczek, baranów i osłów. Proszę nagraj swojego pupila."

    # 3. INSTRUKCJA III (Punkt 1): Stado przekrzykujących się ludzi
    elif typ_glosu == "stado":
        pelny_tekst = "Niestety nie mogę rozpoznać dźwięków wydawanych przez psy, gdyż zakłócają mi dźwięki wydawane przez innego ssaka. Przypominam, że jakość tłumaczenia zależna jest od czystego dźwięku zwierzaka bez żadnych zakłóceń w tle. Proszę nagraj swojego pupila."

    # 4. INSTRUKCJA III (Punkt 2 i 3): Pozytywne emocje ludzkie
    elif typ_glosu == "pozytywne_emocje":
        if st.session_state.licznik_prob_ludzkich <= 1:
            pelny_tekst = "Osioł, ewidentnie słyszę osła, więc nie podejmuję się tego tłumaczenia. Profesjonalnym tłumaczeniem osłów zajmuje się psychiatra."
        else:
            pelny_tekst = "W celu przetłumaczenia tego nagrania proszę o kontakt z twórcą programu - on jest na tyle szalony, by spróbować to przetłumaczyć - kontakt znajdziesz w regulaminie."

    # 5. TRADYCYJNE TŁUMACZENIE PSA (Pełna automatyzacja godzinowa)
    else:
        st.session_state.licznik_prob_ludzkich = 0 
        godzina_teraz = teraz.hour
        
        # AUTOMATYCZNY DOBÓR BAZY NA PODSTAWIE ZEGARA
        if 5 <= godzina_teraz < 12:
            wylosowany_tekst = random.choice(TEKSTY_PORANNE)
        elif 20 <= godzina_teraz or godzina_teraz < 5:
            wylosowany_tekst = random.choice(TEKSTY_WIECZORNE_WYCIE)
        else:
            if roznica_czasu > timedelta(hours=4):
                wylosowany_tekst = "Hej! Ignorujesz mnie! Ta żywiołowa reakcja, piszczenie i obwąchiwanie to nie zabawa – natychmiast zbieraj się i wyjdź ze mną na siku lub kupkę!"
            else:
                wylosowany_tekst = random.choice(TEKSTY_DZIENNE)
            
        pelny_tekst = f"{wylosowany_tekst} {random.choice(DODATKOWE_ZDANIA)}"

    # --- GENEROWANIE AUDIO PRZEZ LEKTORA ---
    tts = gTTS(text=pelny_tekst, lang='pl')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    
    # ==================== SEKCJA DOLNA: WYNIK ====================
    st.write("---")
    st.markdown("### 📊 Wynik analizy")
    
    col_glosnik, col_tekst = st.columns(2)
    
    with col_glosnik:
        st.write("🔊 **Odtwórz głosowo:**")
        st.audio(fp, format="audio/mp3", autoplay=True)
        
    with col_tekst:
        st.write("💬 **Tłumaczenie tekstowe:**")
        st.success(pelny_tekst)

# ==================== STOPKA Z PEŁNYM REGULAMINEM ====================
st.write("---")
col_foot1, col_foot2 = st.columns(2)
with col_foot1:
    st.caption("HauTłumacz v8.0 - Stabilna wersja chmurowa.")
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
