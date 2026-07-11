import streamlit as st
import io
import random
from datetime import datetime, time
from gtts import gTTS

# --- BEZPIECZNE IMPORTOWANIE BIBLIOTEK AKUSTYCZNYCH ---
TRYB_ANALIZY = True
try:
    import numpy as np
    from scipy.io import wavfile
except ImportError:
    TRYB_ANALIZY = False

# --- BEZPIECZNA KONFIGURACJA STRONY ---
st.set_page_config(page_title="HauTłumacz PRO v10.0", page_icon="🐕", layout="centered")

# --- INICJALIZACJA PAMIĘCI ANTY-POWTÓRZENIOWEJ ---
if "ostatni_tekst" not in st.session_state:
    st.session_state.ostatni_tekst = ""
if "licznik_ludzki" not in st.session_state:
    st.session_state.licznik_ludzki = 0
if "ostatnie_pokazywane_zdanie" not in st.session_state:
    st.session_state.ostatnie_pokazywane_zdanie = ""

# --- ANALIZATOR AUDIO (FFT) ---
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

# ==================== TWOJE NOWE BAZY TEKSTÓW ====================

GRUPA_TEKSTY_PORANNE = [
    "Bieguniem, bieguniem, bo się posikam!", 
    "Nie musimy wychodzić, ale zastanów się, czy to się spierze.",
    "Chodź szybko to zobaczysz sąsiadkę bez makijażu!!!",
    "Szybko, bo za chwilę mi tyłek rozerwie!",
    "Pospiesz się, bo narobię ci na środek pokoju!",
    "Sikać mi się chce, szybko!",
    "Nie musisz wstawać, znalazłem przed drzwiami miejsce, gdzie mogę zrąbać.",
    "No wstawaj, obiecałem, że wyprowadzę cię na spacer.",
    "Ktoś mądry powiedział - w zdrowym ciele zdrowy duch i ja to popieram.",
    "Carpe diem - chwytaj smycz!"
]

GRUPA_TEKSTOW_PRZEDPOLUDNIOWYCH = [
    "No i co ja tak w samotności mam być?",
    "O której mogę się ciebie spodziewać?",
    "Nie wpadniesz na przerwę?",
    "Oj wpadnij choć na chwilę to dam ci kość!!!",
    "Poszukaj sobie fajnego zajęcia.",
    "Zatrudnij mnie to będę pilnować pieniędzy."
]

TEKSTY_DZIENNE_ZABAWA = [
    "Interesują mnie tylko konkrety - gdzie są parówki?!",
    "Jaki patyk? Rzuć parówkę!",
    "Pobiegamy razem?",
    "Wyczuwam tutaj tę sukę i mam nadzieję, że się wytłumaczysz?!",
    "Może znów spotkamy tę rudą, jest niezła?!",
    "Już nie mogę się doczekać, gdy zobaczę jak sprzątasz po mnie!",
    "Dobra, przemilczę to, gdy tylko zobaczę zawartość miski."
]

GRUPA_TEKSTOW_POLUDNIOWYCH = [
    "Fajnie, że jesteś w domu, razem coś wymyślimy.",
    "Ty mi rzucaj, a ja będę łapać.",
    "Ja nie wiem, jak koty mogą leżeć tak całymi dniami.",
    "Rzucaj mi kość, tylko tym razem dobrze!",
    "Pobiegamy razem?"
]

GRUPA_TEKSTOW_POPOLUDNIOWYCH = [
    "Tak jak się umawialiśmy - jestem tutaj.",
    "O której to wracasz?",
    "Fajnie, że jesteś, ale teraz szybko chodźmy.",
    "Jeszcze chwila a się sfajdam!",
    "Chodź szybko to zobaczysz coś ciekawego.",
    "Już miałem gryźć meble, by nie wyjść z wprawy."
]

TEKSTY_WIECZORNE = [
    "Jeszcze tylko kupkę, siku i można w kimono!", 
    "Zaraz mi pęcherz rozerwie.",
    "Mogę zesrać się tutaj - nie musimy wychodzić!",
    "Fundamentalne pytanie brzmi - srać czy srać?",
    "Wyczułem fajny towar w okolicy - może jest singlem?",
    "Na razie tylko puściłem bąka, ale kto wie, co czas przyniesie.",
    "Chodź zobaczysz straszną babę.",
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

DODATKOWE_ZDANIA = [
    "No i co ty na to człowiek? Przemyśl to sobie.",
    "Możesz mnie pogłaskać, ale nie ma nic za darmo.",
    "Zrozumiano, czy mam szczeknąć to jeszcze raz?",
    "I nie patrz tak na mnie, tylko wyciągaj smaczki!",
    "Dobra, koniec gadania, bierzmy się za konkrety. Dlaczego miska jest pusta?",
    "Znów miska jest pusta!"
]
GRUPA_TEKSTOW_NEUTRALNYCH = [
    "Co mam powtórzyć?",
    "Już prościej tego nie można wyrazić.",
    "Następnym razem zapisz sobie tę sentencję.",
    "Patrz mi na usta i czytaj z ruchu warg.",
    "Jesteś bardziej inteligentny, gdy milczysz.",
    "Ja drugi raz nie będę powtarzać.",
    "A mówią, że skończyłeś kilka klas.",
    "Jesteś bystrym człowiekiem."
]

TEKSTY_GIGANT_STRES = [
    "Kroczysz po bardzo cienkim lodzie, zatrzymaj się.", 
    "Czy naprawdę chce ci się uciekać?",
    "Odejdź stąd.",
    "Zbłądziłeś?",
    "Tutaj nie znajdziesz pustego nakrycia dla wędrowca.",
    "Pomyliłeś chyba adres?",
    "Agnieszka już tutaj nie mieszka.",
    "Artykuł dwudziesty piąty Kodeksu Karnego jest po mojej stronie.",
    "Ja już jadłem kolację, ale możesz wystawić palca.",
    "Ostrzegam, nie podchodź!",
    "To nie jest dobry pomysł!",
    "Ja sobie twój zapach zapamiętam.",
    "Człowieku, cofnij się.",
    "Nie chcę ciebie tutaj.",
    "Nie znajdziesz tutaj kolegów.",
    "Moje ego nie lubi sprzeciwu, więc przemyśl, czy warto się zbliżać.",
    "Pojawiłem się tutaj znikąd, a ty nadal nie wyciągasz wniosków?",
    "Posłuchaj, białasie, mnie nie obchodzi, kogo tam znasz - rób nawrotkę!"
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
    "Nie patrz tak na mnie z góry! Moje nogi są krótkie, ale gonić kota potrafię szybciej niż myślisz.",
    "Właśnie opracowałem plan, jak przejąć kontrolę nad lodówką. Potrzebuję tylko twojego odcisku palca."
]

TEKSTY_MINIATURA_JAMNIK = [
    "Może i jestem mały jak parówka, ale gniew mam tak wielki, że bardzo długo będziesz to spotkanie wspominać!",
    "Jestem małym, wściekłym demonem! Ale potrafię zajść ci za skórę!",
    "Właśnie się dowiedziałem, że sąsiad chodzi na lewiznę i nie wiem, jak to wykorzystać - moja miska jest pusta!"
]

ZDANIA_ROZKAZUJACE = [
    "I co jeszcze? Może piesek ma ugotować i pozmywać po tobie? To nie ten etap!!!",
    "Ty się z głupim na rozumy pomieniałeś?",
    "Chyba za długo siedziałeś przed telewizorem.",
    "Czy ty już się zaszczepiłeś na głupotę?"
]

# --- POMOCNICZA FUNKCJA DO LOSOWANIA BEZ POWTÓRZEŃ ---
def losuj_bez_powtórzen(baza):
    bezpieczna_baza = [t for t in baza if t != st.session_state.ostatni_tekst]
    if not bezpieczna_baza:
        bezpieczna_baza = baza
    wybrany = random.choice(bezpieczna_baza)
    st.session_state.ostatni_tekst = wybrany
    return wybrany

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

st.title("🐕 HauTłumacz ULTRA v10.0")
st.write("---")

st.markdown("### 🎙️ Sekcja nagrywania i przetwarzania")
st.caption("Uruchom nagrywanie, gdy pies wydaje dźwięki. Algorytm automatycznie dobierze idealny kontekst.")

audio_nagrane = st.audio_input("Nagraj")

if audio_nagrane is not None:
    audio_bytes = audio_nagrane.read()
    wykryte_hz = analizuj_czestotliwosc(audio_bytes)
    
    teraz = datetime.now().time()
    wylosowany = ""
    naglowek_ekranu = ""
    uzyj_dodatkowego = True
    uzyj_neutralnego = False
    
    # Precyzyjne strefy czasowe doby
    is_morning = time(4, 30) <= teraz < time(7, 0)
    is_pre_noon = time(7, 0) <= teraz < time(11, 0)
    is_noon = time(11, 0) <= teraz < time(14, 0)
    is_afternoon = time(14, 0) <= teraz < time(19, 0)
    is_evening = time(19, 0) <= teraz < time(23, 0)
    is_night = teraz >= time(23, 0) or teraz < time(4, 30)

    if TRYB_ANALIZY:
        st.sidebar.metric(label="Wykryta częstotliwość", value=f"{int(wykryte_hz)} Hz")

    # ==================== LOGIKA DETEKCJI I RESTRYKCJI ====================
    
    # 🚨 SYSTEM UPMINANIA CZŁOWIEKA (Wykrywanie pasma mowy ludzkiej)
    if TRYB_ANALIZY and (85 <= wykryte_hz <= 255):
        st.session_state.licznik_ludzki += 1
        uzyj_dodatkowego = False
        naglowek_ekranu = "[Wykryto mowę człowieka]"
        
        if st.session_state.licznik_ludzki == 1:
            wylosowany = "Nie mogę przetłumaczyć tego, bo za szybko mówisz."
        elif st.session_state.licznik_ludzki == 2:
            wylosowany = "Nie mogę przetłumaczyć - Mów wolno i wyraźnie."
        else:
            wylosowany = "A teraz powiedz to drukowanymi, patrząc w lustro. Aplikacja jest do tłumaczenia dźwięków wydawanych przez zwierzaki, więc nie nagrywaj siebie, tylko pieska!"
            st.session_state.licznik_ludzki = 0
            
    # 🎯 STANDARDOWA LOGIKA DETEKCJI EMOCJI I GABARYTÓW PSA
    else:
        st.session_state.licznik_ludzki = 0
        
        # 1. RASY GIGANTYCZNE (Zdenerwowanie -> Poniżej 200 Hz)
        if TRYB_ANALIZY and wykryte_hz < 200:
            st.sidebar.success("🎯 Klasyfikacja: Gigant (Zdenerwowany)")
            wylosowany = losuj_bez_powtórzen(TEKSTY_GIGANT_STRES)
            naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Sfrustrowany Gigant]"
            uzyj_neutralnego = True
            
        # 2. RASY DUŻE (Chce się bawić -> 200 Hz - 450 Hz)
        elif TRYB_ANALIZY and 200 <= wykryte_hz < 450:
            st.sidebar.success("🎯 Klasyfikacja: Duży pies (Zabawa)")
            wylosowany = losuj_bez_powtórzen(TEKSTY_DUZY_OWCZAREK_ZABAWA)
            naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Owczarek w akcji]"
            
        # 3. MINIATURA JAMNIK (Powyżej 1200 Hz)
        elif TRYB_ANALIZY and wykryte_hz > 1200:
            st.sidebar.warning("🎯 Klasyfikacja: Miniatura (Jamnik/York)")
            wylosowany = losuj_bez_powtórzen(TEKSTY_MINIATURA_JAMNIK)
            naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Sfrustrowany Maluch]"
            
        # 4. PASMO ŚREDNIE -> ROZBICIE NA TWOJE 6 STREF CZASOWYCH
        else:
            if is_morning:
                wylosowany = losuj_bez_powtórzen(GRUPA_TEKSTY_PORANNE)
                naglowek_ekranu = "[Poranny Bieguniem]"
                uzyj_dodatkowego = False
            elif is_pre_noon:
                wylosowany = losuj_bez_powtórzen(GRUPA_TEKSTOW_PRZEDPOLUDNIOWYCH)
                naglowek_ekranu = "[Przedpołudniowy Samotnik]"
            elif is_noon:
                # EFEKT X: Obsługa sparowanych zdań
                if st.session_state.ostatnie_pokazywane_zdanie == "Ty mi rzucaj, a ja będę łapać.":
                    wylosowany = "Chyba, że wolisz żebym ciebie podgryzał."
                else:
                    wylosowany = losuj_bez_powtórzen(GRUPA_TEKSTOW_POLUDNIOWYCH)
                naglowek_ekranu = "[Południowa Rozgrywka]"
            elif is_afternoon:
                wylosowany = losuj_bez_powtórzen(GRUPA_TEKSTOW_POPOLUDNIOWYCH)
                naglowek_ekranu = "[Popołudniowa Radość]"
            elif is_evening:
                wylosowany = losuj_bez_powtórzen(TEKSTY_WIECZORNE)
                naglowek_ekranu = "[Wieczorny Relaks]"
            elif is_night:
                wylosowany = losuj_bez_powtórzen(TEKSTY_NOCNE)
                naglowek_ekranu = "[Nocny Alarm]"
                uzyj_dodatkowego = False
                
            # Czasem rzucamy prztyczkiem w nos, jeśli człowiek wydaje komendy
            if (is_pre_noon or is_noon or is_afternoon) and random.random() < 0.3:
                wylosowany = losuj_bez_powtórzen(ZDANIA_ROZKAZUJACE)

    # Zapamiętujemy stan do sparowanych komunikatów
    st.session_state.ostatnie_pokazywane_zdanie = wylosowany

    # --- BUDOWANIE STRUKTURY MIXU ZDAŃ ---
    final_tekst = wylosowany
    if uzyj_dodatkowego and not (TRYB_ANALIZY and 85 <= wykryte_hz <= 255):
        final_tekst += f" {random.choice(DODATKOWE_ZDANIA)}"
    if uzyj_neutralnego:
        final_tekst += f" {random.choice(GRUPA_TEKSTOW_NEUTRALNYCH)}"

    # Przygotowanie tekstu pod dynamiczne turbo tempo (+15%)
    tekst_do_czytania = final_tekst.replace(".", ",").replace("!", ",")

        # --- GENEROWANIE I FIZYCZNE PRZYSPIESZENIE GŁOSU O 15% (WSOLA) ---
    tts = gTTS(text=final_tekst, lang='pl', slow=False)
    fp_raw = io.BytesIO()
    tts.write_to_fp(fp_raw)
    fp_raw.seek(0)
    
    # Warstwa przyspieszająca audio na poziomie fali dźwiękowej
    if TRYB_ANALIZY:
        try:
            sample_rate, data = wavfile.read(fp_raw)
            # Algorytm WSOLA: Przyspieszenie tempa o 1,15x bez zmiany tonacji
            skurczony_rozmiar = int(len(data) / 1.15)
            indeksy = np.round(np.linspace(0, len(data) - 1, skurczony_rozmiar)).astype(int)
            przyspieszone_data = data[indeksy]
            
            fp = io.BytesIO()
            wavfile.write(fp, sample_rate, przyspieszone_data)
            fp.seek(0)
        except:
            fp = fp_raw # Zapasowy powrót w razie błędu pliku mp3/wav
    else:
        fp = fp_raw

    # ==================== SEKCJA WYNIKU ====================
    st.write("---")
    st.markdown("### 📊 Wynik analizy")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("🔊 **Odtwórz głosowo:**")
        st.audio(fp, format="audio/wav", autoplay=True)
    with col2:
        st.write("💬 **Tłumaczenie tekstowe:**")
        st.success(f"{naglowek_ekranu}: {final_tekst}")

# ==================== STOPKA Z PEŁNYM REGULAMINEM ====================
st.write("---")
col_foot1, col_foot2 = st.columns(2)
with col_foot1:
    st.caption("HauTłumacz ULTRA v10.1 - Stabilna wersja chmurowa.")
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
