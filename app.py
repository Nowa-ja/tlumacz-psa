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

# --- STABILNA ANALIZA HZ DLA AUTOMATU ---
def analizuj_czestotliwosc(audio_bytes):
    try:
        sample_rate, data = wavfile.read(io.BytesIO(audio_bytes))
        if len(data.shape) > 1:
            data = data[:, 0]
        fft_spectrum = np.fft.rfft(data)
        freq = np.fft.rfftfreq(len(data), d=1.0/sample_rate)
        szczytowa_indeks = np.argmax(np.abs(fft_spectrum))
        wykryte = freq[szczytowa_indeks]
        if wykryte < 50 or wykryte > 3000:
            return 600.0
        return wykryte
    except:
        return 600.0

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
    "Ktoś mądry powiedział - w zdrowym ciele zdrowy duch i ja to popieram.",
    "Carpe diem - chwytaj smycz!"
]

GRUPA_TEKSTOW_PRZEDPOLUDNIOWYCH = [
    "No i co ja tak w samotności mam być przez resztę dnia?",
    "O której mogę się ciebie spodziewać?",
    "Nie wpadniesz na przerwę?",
    "Będzie fajna kość, wpadnij na chwilę.",
    "Weź sobie godzinkę wolnego w pracy.",
    "Oj wpadnij choć na chwilę to dam ci kość!",
    "Po co idziesz do pracy, dołek możesz wykopać tutaj.",
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
    "Jestem gotowy, rzucaj tę kość.", 
    "Ja nie wiem, jak koty mogą leżeć tak całymi dniami.",
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
    "Jeszcze tylko kupkę, siku i można w kimono!", 
    "Zaraz mi pęcherz rozerwie.",
    "Mogę zesrać się tutaj - nie musimy wychodzić!",
    "Fundamentalne pytanie brzmi - srać czy nie srać?",
    "Wyczułem fajny towar w okolicy - może jest singlem?",
    "Na razie tylko puściłem bąka, ale kto wie, co czas przyniesie.",
    "Chodź pokażę ci straszną babę.",
    "A wiesz, że sąsiadka ma souvenir na sumieniu?",
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
    "Jestem małym, wściekłym demonem! Ale potrafię zajść ci za skórę!"
]

FONETYCZNY_BARAN = "Bęęęęęęęęęęęęęęę!"
FONETYCZNA_KROWA = "Móóóóóóóóóóóóóóóó!"

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

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f5; }
    h1 { color: #1e4620 !important; text-align: center; margin-top: 10px; }
    .stAudioInput { border: 2px dashed #81c784 !important; border-radius: 12px; padding: 10px; background-color: #e8f5e9; }
    </style>
""", unsafe_allow_html=True)

st.title("🐕 HauTłumacz FARMA v10.4")
st.write("---")
# --- SUROWY REJESTRATOR (PROSTO I AUTOMATYCZNIE) ---
audio_nagrane = st.audio_input("Nagraj dźwięk:")

if audio_nagrane is not None:
    audio_bytes = audio_nagrane.read()
    wykryte_hz = analizuj_czestotliwosc(audio_bytes)
    
    teraz = datetime.now().time()
    final_tekst = ""
    naglowek_ekranu = ""
    
    is_morning = time(4, 30) <= teraz < time(7, 0)
    is_pre_noon = time(7, 0) <= teraz < time(11, 0)
    is_noon = time(11, 0) <= teraz < time(14, 0)
    is_afternoon = time(14, 0) <= teraz < time(19, 0)
    is_evening = time(19, 0) <= teraz < time(23, 0)
    is_night = teraz >= time(23, 0) or teraz < time(4, 30)

    st.sidebar.metric(label="Wykryta częstotliwość", value=f"{int(wykryte_hz)} Hz")

       # --- AUTOMATYCZNY DETEKTOR LUDZKIEGO GŁOSU (85 Hz - 1050 Hz) ---
    if 85 <= wykryte_hz <= 1050:
        if wykryte_hz < 220:
            zwierze = FONETYCZNY_BARAN
            komentarz = "Wykryto głos z Twojego rodzinnego stada! Posłuchaj kumpla z pastwiska, nie pyskuj i nagraj psa!"
            naglowek_ekranu = "[Wykryto Samca - Tryb Barana]"
        else:
            zwierze = FONETYCZNA_KROWA
            komentarz = "Wykryto dźwięki z zagrody! Posłuchaj koleżanki z łąki, przestań wydawać rozkazy i daj psu dojść do głosu!"
            naglowek_ekranu = "[Wykryto Samicę - Tryb Krowy]"
            
        final_tekst = f"{zwierze} Nie mogę przetłumaczyć tego dźwięku, bo zamiast psa wyraźnie słyszę człowieka! {komentarz}"

    elif wykryte_hz < 85 or wykryte_hz > 3000:
        final_tekst = "Słyszę tylko szum tła, odgłosy ulicy lub samochód. Poczekaj na ciszę i pozwól zaszczekać psu!"
        naglowek_ekranu = "[⚠️ Zakłócenia Otoczenia]"

    # --- TRYB PSA (CZĘSTOTLIWOŚCI POWYŻEJ 1050 Hz) ---
    else:
        if 1050 < wykryte_hz < 1350:

            final_tekst = pobierz_tekst_kontekstowy(TEKSTY_SREDNI_BEAGLE)
            naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Średni Spryciarz]"
        elif 900 <= wykryte_hz < 1400:
            final_tekst = pobierz_tekst_kontekstowy(TEKSTY_MALUCH)
            naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Mały Wojownik]"
        elif wykryte_hz >= 1400:
            final_tekst = pobierz_tekst_kontekstowy(TEKSTY_MINIATURA_JAMNIK)
            naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Sfrustrowany Maluch]"
        else:
            if is_morning:
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

    # Generowanie mowy lektora
    tekst_do_czytania = final_tekst.replace(".", ",").replace("!", ",")
    tts = gTTS(text=tekst_do_czytania, lang='pl', slow=False)
    fp_raw = io.BytesIO()
    tts.write_to_fp(fp_raw)
    fp_raw.seek(0)
    
    try:
        sample_rate, data = wavfile.read(fp_raw)
        skurczony_rozmiar = int(len(data) / 1.15)
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
