import streamlit as st
import io
import random
from datetime import datetime, time
from scipy.io import wavfile
import numpy as np
from gtts import gTTS

# --- BEZPIECZNA KONFIGURACJA STRONY ---
st.set_page_config(page_title="HauTłumacz PRO v10.4", page_icon="🐕", layout="centered")

# --- INICJALIZACJA PAMIĘCI SYSTEMU ---
if "ostatni_tekst" not in st.session_state:
    st.session_state.ostatni_tekst = ""
if "wykorzystane_teksty" not in st.session_state:
    st.session_state.wykorzystane_teksty = set()

# --- STABILNA ANALIZA HZ ORAZ DETEKCJA WARCZENIA ---
def analizuj_audio(audio_bytes):
    """Zwraca krotkę: (wykryte_hz, czy_warczenie)"""
    try:
        sample_rate, data = wavfile.read(io.BytesIO(audio_bytes))
        if len(data.shape) > 1:
            data = data.mean(axis=1)
        if len(data) == 0:
            return 600.0, False
            
        fft_spectrum = np.fft.rfft(data)
        freq = np.fft.rfftfreq(len(data), d=1.0/sample_rate)
        
        # Znajdowanie dominującej częstotliwości
        szczytowa_indeks = np.argmax(np.abs(fft_spectrum))
        wykryte = freq[szczytowa_indeks]
        
        # NOWY, ROZSZERZONY DETEKTOR WARCZENIA (Uwzględnia ostre warczenie przy 710 Hz)
        czy_warczenie = False
        calkowita_energia = np.sum(np.abs(fft_spectrum))
        
        if calkowita_energia > 0:
            # 1. Sprawdzamy głębokie, basowe warczenie (60-140 Hz)
            niskie_pasmo = (freq >= 60) & (freq <= 140)
            energia_basu = np.sum(np.abs(fft_spectrum[niskie_pasmo]))
            
            # 2. Sprawdzamy ostre, wibrujące warczenie w wyższych rejestrach (450-950 Hz)
            ostre_pasmo = (freq >= 450) & (freq <= 950)
            energia_ostra = np.sum(np.abs(fft_spectrum[ostre_pasmo]))
            
            # Warunek aktywacji alarmu
            if 60 <= wykryte <= 140 and (energia_basu / calkowita_energia) > 0.35:
                czy_warczenie = True
            elif 450 <= wykryte <= 950 and (energia_ostra / calkowita_energia) > 0.30:
                # Jeśli dominujący ton leży w paśmie ostrym i ma dużą koncentrację energii - to warczenie!
                czy_warczenie = True
        
        if wykryte < 50 or wykryte > 3000:
            return 600.0, False
            
        return float(wykryte), czy_warczenie
    except:
        return 600.0, False

# ==================== NOWA BAZA: STRASZNE WARCZENIE ====================
TEKSTY_WARCZENIE_ALARM = [
    "Zatrzymaj się. Natychmiast. Nie testuj mojej cierpliwości.",
    "Nie podchodź. To nie są żarty, ani zabawa.",
    "Odsuń się powoli. Widzę twój każdy ruch i jestem w pełnej godowości do ataku.",
    "Zostaw mnie w spokoju. Ostrzegam cię ostatni raz, zanim stracę nad sobą kontrolę.",
    "Odejdź stąd natychmiast, bo pożałujesz tej pewności siebie.",
    "Cofnij się, nie żartuję. To moje ostatnie ostrzeżenie.",
    "Ani kroku dalej. To nie jest żart. Koniec zabawy."
]


# ==================== BAZY TEKSTÓW GODZINOWYCH ====================
GRUPA_TEKSTY_PORANNE = [
    "Bieguniem, bieguniem, bo się posikam!", 
    "Nie musimy wychodzić, ale zastanów się, czy to się spierze.",
    "Chodź szybko to zobaczysz sąsiadkę bez makijażu!",
    "Szybko, bo za chwilę mi tyłek rozerwie!",
    "Pospiesz się, bo narobię ci na środek pokoju!",
    "Sikać mi się chce, szybko!",
    "Nie musisz wstawać, wiem gdzie mogę się zrąbać.",
    "No wstawaj, obiecałem, że wyprowadzę cię na spacer.",
    "W zdrowym ciele zdrowy duch i ja to popieram.",
    "Carpe diem - chwytaj smycz!"
]

GRUPA_TEKSTOW_PRZEDPOLUDNIOWYCH = [
    "No i co ja tak w samotności mam być przez resztę dnia?",
    "O której mogę się ciebie spodziewać?",
    "Nie wpadniesz na przerwę?",
    "Będzie fajna kość, wpadnij na chwilę.",
    "Weź sobie godzinkę wolnego w pracy.",
    "Oj wpadnij choć na chwilę to dam ci kość!",
    "Nie idź do pracy, pokopmy dołki.",
    "Weź mnie ze sobą, będę pilnować pieniędzy."
]
TEKSTY_DZIENNE_ZABAWA = [
    "Interesują mnie tylko konkrety - gdzie są parówki?!",
    "Konkrety to smakołyki.",
    "Jaki patyk? Rzuć mi parówkę!",
    "Pobiegamy razem?",
    "Wyczuwam tutaj tę sukę i mam nadzieję, że się wytłumaczysz?!",
    "Może znów spotkamy tę rudą, jest niezła?!",
    "Już nie mogę się doczekać, gdy zobaczę jak sprzątasz po mnie!",
    "Dobra, przemilczę to, gdy tylko zobaczę zawartość miski."
]

GRUPA_TEKSTOW_POLUDNIOWYCH = [
    "Fajnie, że jesteś w domu, razem coś wymyślimy.",
    "Ty mi rzucaj smakołyk, a ja będę łapać.",
    "Jestem gotowy, rzucaj kość.", 
    "Ja nie wiem, jak koty mogą leżeć tak całymi dniiami.",
    "Rzucaj tę kość, tylko tym razem dobrze!",
    "Pobiegamy razem?"
]

GRUPA_TEKSTOW_POPOLUDNIOWYCH = [
    "Tak jak się umawialiśmy - jestem tutaj.",
    "O której to wracasz?",
    "Fajnie, że jesteś, ale teraz szybko chodźmy.",
    "Jeszcze chwila a się sfajdam!",
    "Chodź szybko na spacer to zobaczysz coś ciekawego.",
    "Już miałem gryźć meble, by nie wyjść z wprawy."
]

TEKSTY_WIECZORNE = [
    "Jeszcze tylko kupkę, śiku i można w kimono!", 
    "Zaraz mi pęcherz rozerwie.",
    "Mogę sfajdać się tutaj - nie musimy wychodzić!",
    "Fundamentalne pytanie brzmi - gdzie mam narobić?",
    "Wyczułem fajny towar w okolicy - może jest singlem?",
    "Na razie tylko puściłem bąka, ale kto wie, co czas przyniesie.",
    "Chodź pokażę ci straszną babę.",
    "A wiesz, że sąsiadka ma coś na sumieniu?",
    "Cisza nocna jest od dwudziestej czwartej?"
]

TEKSTY_NOCNE = [
    "Ludzie! Ludzie! Ludziska!!!", 
    "Ja tutaj strasznie cierpię.",
    "Ludzie, ja tutaj jestem sam!",
    "Ludzie, oni mnie straszyli, że będą gwałcić!",
    "Ludzie, właściciel tego mieszkania ma skitrany gdzieś towar!",
    "Niech ktoś zadzwoni do opieki nad zwierzętami!",
    "Ludzie, dajcie mi tutaj kogoś do zabawy.",
    "Niech mi ktoś pomoże!!!",
    "Jest tam kto?",
    "Pomocy! Ludzie, tutaj jakiś szalony pies nawalił i strasznie śmierdzi!!!",
    "W co ja się wpakowałem...!!!"
]

TEKSTY_DUZY_OWCZAREK_ZABAWA = [
    "Dawaj parówkę albo sam sobie wezmę kawał mięcha!",
    "Widziałem, jak grdyka ci skacze. Jadłeś i się nie podzieliłeś człowieku?",
    "Wolisz rzucać mi patyk czy uciekać przed moimi zębami - wybieraj!",
    "A teraz rzuć swojską!"
]

TEKSTY_SREDNI_BEAGLE = [
    "Wykryto ton rasy średniej (Beagle/Spaniel/Border)! Mam idealne proporcje sprytu i energii.",
    "Może i nie jestem gigantem, ale za to potrafię wywęszyć każdą parówkę w promieniu kilometra!",
    "Zaraz zrobię ci tutaj małe przemeblowanie, jeśli natychmiast nie pójdziemy pobiegać!"
]

TEKSTY_MALUCH = [
    "Wykryto małego spryciarza (Mops/Buldog/Jack Russell)! Mały ciałem, ale potężny duchem!",
    "Nie patrz tak na mnie z góry! Moje nogi są krótkie, ale gonić kota potrafię szybciej niż myślisz."
]

TEKSTY_MINIATURA_JAMNIK = [
    "Może i jestem mały jak parówka, ale gniew mam tak wielki, że bardzo długo będziesz to spotkanie wspominać!",
    "Jestem małym, wściekłym demonem! But potrafię zajść ci za skórę!"
]

FONETYCZNY_BARAN = "Bęęęęęęęęęęęęęęę!"
FONETYCHNA_KROWA = "Móóóóóóóóóóóóóóóó!"

# --- FUNKCJA LOSUJĄCA JEDNO ZDANIE ---
def pobierz_tekst_kontekstowy(baza):
    dostepne = [t for t in baza if t not in st.session_state.wykorzystane_teksty]
    if not dostepne:
        for t in baza:
            st.session_state.wykorzystane_teksty.discard(t)
        dostepne = baza
    bezpieczne = [t for t in dostepne if t != st.session_state.ostatni_tekst]
    if not bezpieczne:
        bezpieczne = dostepne
    wybrany = random.choice(bezpieczne)
    st.session_state.wykorzystane_teksty.add(wybrany)
    st.session_state.ostatni_tekst = wybrany
    return wybrany

# --- STYLE CSS (Z DODANYM PULSUJĄCYM CZERWONYM ALARMEM DLA WARCZENIA) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f5; }
    h1 { color: #1e4620 !important; text-align: center; margin-top: 10px; }
    .stAudioInput { border: 2px dashed #81c784 !important; border-radius: 12px; padding: 10px; background-color: #e8f5e9; }
    
    /* Animacja migającego, czerwonego tła dla niebezpieczeństwa */
    @keyframes pulse-red {
        0% { background-color: rgba(211, 47, 47, 0.1); }
        50% { background-color: rgba(211, 47, 47, 0.3); }
        100% { background-color: rgba(211, 47, 47, 0.1); }
    }
    .red-alert-box {
        animation: pulse-red 2s infinite;
        border: 3px solid #d32f2f !important;
        border-radius: 10px;
        padding: 15px;
        color: #b71c1c !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🐕 HauTłumacz FARMA v10.4")
st.write("---")

audio_nagrane = st.audio_input("Nagraj dźwięk:")
if audio_nagrane is not None:
    audio_bytes = audio_nagrane.read()
    wykryte_hz, czy_warczenie = analizuj_audio(audio_bytes)
    
    teraz = datetime.now().time()
    final_tekst = ""
    naglowek_ekranu = ""
    tryb_alarmu = False
    
    # Warunki czasowe
    is_morning = time(4, 30) <= teraz < time(7, 0)
    is_pre_noon = time(7, 0) <= teraz < time(11, 0)
    is_noon = time(11, 0) <= teraz < time(14, 0)
    is_afternoon = time(14, 0) <= teraz < time(19, 0)
    is_evening = time(19, 0) <= teraz < time(23, 0)
    is_night = teraz >= time(23, 0) or teraz < time(4, 30)

    st.sidebar.metric(label="Wykryta częstotliwość", value=f"{int(wykryte_hz)} Hz")

    # ==================== LOGIKA FILTROWANIA DŹWIĘKU ====================

    # PRIORYTET 1: DETEKCJA EMOCJI - GROŹNE WARCZENIE (Czerwony Alarm)
    if czy_warczenie:
        final_tekst = pobierz_tekst_kontekstowy(TEKSTY_WARCZENIE_ALARM)
        naglowek_ekranu = "[🚨 KRTYTYCZNE OSTRZEŻENIE - EMOCJA: AGRESJA/STRACH]"
        tryb_alarmu = True

    # PRIORYTET 2: DETEKTOR LUDZKIEGO GŁOSU (85 Hz - 450 Hz) - działa tylko gdy nie ma warczenia
    elif 85 <= wykryte_hz <= 450:
        if wykryte_hz < 220:
            zwierze = FONETYCZNY_BARAN
            komentarz = "Wykryto głos z Twojego rodzinnego stada! Posłuchaj kumpla z pastwiska, nie pyskuj i nagraj psa!"
            naglowek_ekranu = "[Wykryto Samca - Tryb Barana]"
        else:
            zwierze = FONETYCHNA_KROWA
            komentarz = "Wykryto dźwięki z zagrody! Posłuchaj koleżanki z łąki, przestań wydawać rozkazy i daj psu dojść do głosu!"
            naglowek_ekranu = "[Wykryto Samicę - Tryb Krowy]"
            
        final_tekst = f"{zwierze} Nie mogę przetłumaczyć tego dźwięku, bo zamiast psa wyraźnie słyszę człowieka! {komentarz}"

    # PRIORYTET 3: ZAKŁÓCENIA OTOCZENIA
    elif wykryte_hz < 85 or wykryte_hz > 3000:
        final_tekst = "Słyszę tylko szum tła, odgłosy ulicy lub samochód. Poczekaj na ciszę i pozwól zaszczekać psu!"
        naglowek_ekranu = "[⚠️ Zakłócenia Otoczenia]"

    # PRIORYTET 4: STANDARDOWY TRYB PSA (Częstotliwości powyżej 450 Hz)
    else:
        # Niskie szczeknięcie dużego psa (np. 450-550 Hz), o ile to nie pora spania/spaceru
        if 450 < wykryte_hz < 550 and not (is_morning or is_evening or is_night):
            final_tekst = pobierz_tekst_kontekstowy(TEKSTY_DUZY_OWCZAREK_ZABAWA)
            naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Duży Owczarek]"
        
        # 1. ŚCISŁE PORY DNIA
        elif is_morning:
            final_tekst = pobierz_tekst_kontekstowy(GRUPA_TEKSTY_PORANNE)
            naglowek_ekranu = "[Poranny Bieguniem]"
        elif is_pre_noon:
            final_tekst = pobierz_tekst_kontekstowy(GRUPA_TEKSTOW_PRZEDPOLUDNIOWYCH)
            naglowek_ekranu = "[Przedpołudniowy Samotnik]"
        elif is_noon:
            final_tekst = pobierz_tekst_kontekstowy(GRUPA_TEKSTOW_POLUDNIOWYCH)
            naglowek_ekranu = "[Południowa Rozgrywka]"
        elif is_afternoon:
            final_tekst = pobierz_tekst_kontekstowy(GRUPA_TEKSTOW_POPOLUDNIOWYCH)
            naglowek_ekranu = "[Popołudniowa Radość]"
        elif is_evening:
            final_tekst = pobierz_tekst_kontekstowy(TEKSTY_WIECZORNE)
            naglowek_ekranu = "[Wieczorny Relaks]"
        elif is_night:
            final_tekst = pobierz_tekst_kontekstowy(TEKSTY_NOCNE)
            naglowek_ekranu = "[Nocny Alarm]"
            
        # 2. PODZIAŁ NA RASY (Zapasowy filtr)
        else:
            if 550 <= wykryte_hz < 800:
                final_tekst = pobierz_tekst_kontekstowy(TEKSTY_SREDNI_BEAGLE)
                naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Średni Spryciarz]"
            elif 800 <= wykryte_hz < 1300:
                final_tekst = pobierz_tekst_kontekstowy(TEKSTY_MALUCH)
                naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Mały Wojownik]"
            elif wykryte_hz >= 1300:
                final_tekst = pobierz_tekst_kontekstowy(TEKSTY_MINIATURA_JAMNIK)
                naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Sfrustrowany Maluch]"

        # ==================== GENERATOR LEKTORA ORAZ MODYFIKACJA AUDIO ====================
    tekst_do_czytania = final_tekst.replace(".", ",").replace("!", ",")
    
    # Tworzenie głosu lektora (zawsze standardowa prędkość bazowa gTTS)
    tts = gTTS(text=tekst_do_czytania, lang='pl', slow=False)
    fp_raw = io.BytesIO()
    tts.write_to_fp(fp_raw)
    fp_raw.seek(0)
    
    try:
        sample_rate, data = wavfile.read(fp_raw)
        
        # Ustalamy mnożnik prędkości: 1.30 dla alarmu (szybciej o 30%), 1.15 dla reszty tekstów
        mnoznik_predkosci = 1.30 if tryb_alarmu else 1.15
        
        skurczony_rozmiar = int(len(data) / mnoznik_predkosci)
        indeksy = np.round(np.linspace(0, len(data) - 1, skurczony_rozmiar)).astype(int)
        przyspieszone_data = data[indeksy]
        
        fp = io.BytesIO()
        wavfile.write(fp, sample_rate, przyspieszone_data)
        fp.seek(0)
    except:
        fp = fp_raw
    
    st.write("---")
    st.markdown("### 📊 Wynik analizy")
    col1, col2 = st.columns(2)
    with col1:
        st.write("🔊 **Odtwórz głosowo:**")
        st.audio(fp, format="audio/wav", autoplay=True)
    with col2:
        st.write("💬 **Tłumaczenie tekstowe:**")
        if tryb_alarmu:
            # Specjalna, pulsująca na czerwono ramka z CSS
            st.markdown(f"<div class='red-alert-box'>{naglowek_ekranu}<br><br>{final_tekst}</div>", unsafe_allow_html=True)
        else:
            st.success(f"{naglowek_ekranu}: {final_tekst}")


# ==================== STOPKA Z PEŁNYM REGULAMINEM ====================
st.write("---")
if st.button("📝 Regulamin strony"):
    st.info("""
    **Regulamin i informacje o serwisie hauhau.online**
    
    Drogi użytkowniku.
    Jest mi bardzo miło gościć Ciebie na stronie „hauhau.online” i liczę na to, że efekt mojej pracy sprawi Ci wiele przyjemności w trakcie użytkowania tłumacza oraz przyczyni się do pogłębienia relacji między psiakiem a człowiekiem. 
    
    - Na stronie hauhau.online nie są gromadzone żadne dane oraz dźwięki wydobywane przez zwierzęta, które nagrasz w celu przetłumaczenia. 
    - Na stronie hauhau.online nie są gromadzone żadne tłumaczenia, a każdy kolejny proces nagrywania kasuje nagranie poprzednie tak samo jak opuszczenie strony. Więc jeśli chcesz zachować tekst, utrwal go samodzielnie.
    
    Cały proces tłumaczenia odbywa się na bieżąco i jest on wynikiem klasyfikacji przez algorytm i dobierania słów zapisanych w bazie danych, która z każdym dniem powiększa się o kolejne zwroty i słowa. 
    
    W celu przetłumaczenia bardziej skomplikowanych dźwięków zapraszam do kontaktu drogą elektroniczną pod adresem: hauhau.kontakt@gmail.com w celu ustalenia warunków tłumaczenia psisięgłego – (zastrzegając, że czas odpowiedzi może być dłuższy). Dołożę wszelkich starań, aby tłumaczenie spełniało najwyższe standardy. 
    
    Życzę wszystkim wiele radości z użytkowania tłumacza!
    """)
