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
st.set_page_config(page_title="HauTłumacz PRO v10.4", page_icon="🐕", layout="centered")

# --- INICJALIZACJA PAMIĘCI SYSTEMU ---
if "ostatni_tekst" not in st.session_state:
    st.session_state.ostatni_tekst = ""
if "licznik_ludzki" not in st.session_state:
    st.session_state.licznik_ludzki = 0
if "ostatnie_pokazywane_zdanie" not in st.session_state:
    st.session_state.ostatnie_pokazywane_zdanie = ""
if "wykorzystane_teksty" not in st.session_state:
    st.session_state.wykorzystane_teksty = set()

# --- INTELIGENTNY DETEKTOR PSIEGO GŁOSU (NOWY FILTR) ---
def analizuj_czestotliwosc(audio_bytes):
    if not TRYB_ANALIZY:
        return 600.0, "pies"
    try:
        sample_rate, data = wavfile.read(io.BytesIO(audio_bytes))
        if len(data.shape) > 1:
            data = data[:, 0]
            
        # 1. Analiza głośności i energii dźwięku
        amplituda_max = np.max(np.abs(data))
        if amplituda_max < 500:  
            return 600.0, "szum"
            
        # 2. Analiza długości impulsu (szczeknięcie psa jest krótkie)
        progowana_energia = np.abs(data) > (amplituda_max * 0.3)
        czas_trwania_sekundy = np.sum(progowana_energia) / sample_rate
        
        # 3. Analiza ZCR (Zero Crossing Rate - chropowatość dźwięku)
        zcr_value = np.sum(np.abs(np.diff(np.sign(data)))) / (2 * len(data))

        # 4. Obliczanie FFT (częstotliwości)
        fft_spectrum = np.fft.rfft(data)
        freq = np.fft.rfftfreq(len(data), d=1.0/sample_rate)
        amplitudy = np.abs(fft_spectrum)
        
        # Zawężamy pasmo szukania szczytu do granic realnych dla psa/człowieka
        maska_pasma = (freq >= 85) & (freq <= 3000)
        if not np.any(maska_pasma):
            return 600.0, "szum"
            
        amplitudy_przefiltrowane = np.where(maska_pasma, amplitudy, 0)
        szczytowy_indeks = np.argmax(amplitudy_przefiltrowane)
        wykryte_hz = freq[szczytowy_indeks]

        # --- LOGIKA ODSEJOWANIA PODRÓBEK ---
        # Jeśli dźwięk trwa za długo lub jest zbyt płynny, melodyjny (niski ZCR) -> to człowiek
        if czas_trwania_sekundy > 0.65 or zcr_value < 0.05:
            return wykryte_hz, "czlowiek"
        
        # Ciągłe, basowe buczenie lub hałas auta
        if wykryte_hz < 130 and czas_trwania_sekundy > 0.5:
            return wykryte_hz, "szum"

        # Dźwięk dynamiczny, krótki i szorstki -> identyfikujemy jako psa
        return wykryte_hz, "pies"
    except:
        return 600.0, "pies"

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
    "Fundamentalne pytanie brzmi - srać czy srać?",
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

DODATKOWE_ZDANIA = [
    "No i co ty na to człowiek? Przemyśl to sobie.",
    "Możesz mnie pogłaskać, ale nie ma nic za darmo.",
    "Zrozumiano, czy mam szczeknąć to jeszcze raz?",
    "I nie patrz tak na mnie, tylko wyciągaj smaczki!",
    "Pytanie brzmi, dlaczego miska wciąż jest pusta?",
    "Sąsiad wyżarł mi wszystko z miski."
]

GRUPA_TEKSTOW_NEUTRALNYCH = [
    "Co mam powtórzyć, czego nie zrozumiałeś - miska jest pusta?",
    "Ja dwa razy powtarzać nie będę.",
    "Następnym razem zapisz sobie tę sentencję.",
    "Patrz mi na usta i czytaj z ruchu warg.",
    "Jesteś bardziej inteligentny, gdy milczysz.",
    "Skup się, teraz zaszczekam drukowanymi!",
    "A mówią, że skończyłeś kilka klas.",
    "Jestem z Ciebie dumny - zrozumiałeś!!!"
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
    "Odejdź.",
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
    "A nytka rzuć swojską!"
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

FONETYCZNY_BARAN = "Bęęęęęęęęęęęęęęę!"
FONETYCZNA_KROWA = "Móóóóóóóóóóóóóóóó!"

# --- POMOCNICZA FUNKCJA DO LOSOWANIA ---
def pobierz_tekst_kontekstowy(baza, nazwa_puli):
    dostepne = [t for t in baza if t not in st.session_state.wykorzystane_teksty]
    if not dostepne:
        for t in baza:
            st.session_state.wykorzystane_teksty.discard(t)
        dostepne = baza
        st.session_state["wyczerpana_" + nazwa_puli] = True
    else:
        st.session_state["wyczerpana_" + nazwa_puli] = False

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

st.title("🐕 HauTłumacz FARMA v10.4")
st.write("---")

audio_nagrane = st.audio_input("Nagraj")
if audio_nagrane is not None:
    audio_bytes = audio_nagrane.read()
    
    # Rozpakowujemy częstotliwość oraz status dźwięku
    wykryte_hz, status_dzwieku = analizuj_czestotliwosc(audio_bytes)
    
    teraz = datetime.now().time()
    wylosowany = ""
    naglowek_ekranu = ""
    uzyj_dodatkowego = True
    uzyj_neutralnego = False
    wymus_komunikat = False
    
    is_morning = time(4, 30) <= teraz < time(7, 0)
    is_pre_noon = time(7, 0) <= teraz < time(11, 0)
    is_noon = time(11, 0) <= teraz < time(14, 0)
    is_afternoon = time(14, 0) <= teraz < time(19, 0)
    is_evening = time(19, 0) <= teraz < time(23, 0)
    is_night = teraz >= time(23, 0) or teraz < time(4, 30)

    if TRYB_ANALIZY:
        st.sidebar.metric(label="Wykryta częstotliwość", value=f"{int(wykryte_hz)} Hz")

    # --- NOWA REAKCJA NA LOCKOUT I FILTROWANIE ---
    if status_dzwieku == "szum":
        wylosowany = "Słyszę tylko szum tła, odgłosy ulicy lub przejeżdżający samochód. Poczekaj, aż zrobi się ciszej i pozwól zaszczekać psu!"
        naglowek_ekranu = "[⚠️ Zakłócenia Otoczenia]"
        uzyj_dodatkowego = False
        uzyj_neutralnego = False
        wymus_komunikat = True
        
    elif status_dzwieku == "czlowiek":
        wylosowany = random.choice([
            "Nie mogę przetłumaczyć tego dźwięku, bo zamiast psa słyszę barana lub osła! 🐑",
            "Marna podróbka! Twój pies właśnie schował głowę pod poduszkę ze wstydu za Twoje szczekanie.",
            "Wykryto człowieka próbującego mówić po psiemu. Twój akcent jest fatalny, spróbuj jeszcze raz!",
            "Słyszę osła! Aplikacja służy do tłumaczenia zwierzaków, więc weź na wstrzymanie!"
        ])
        naglowek_ekranu = "[❌ Wykryto Podrabianie - Tryb Człowieka]"
        uzyj_dodatkowego = False
        uzyj_neutralnego = False
        wymus_komunikat = True

    # --- GLÓWNA LOGIKA DLA PSA (URUCHAMIANA TYLKO GDY WYKRYTO PSA) ---
    if not wymus_komunikat:
        if TRYB_ANALIZY and (85 <= wykryte_hz <= 255):
            st.session_state.licznik_ludzki += 1
            uzyj_dodatkowego = False
            if wykryte_hz < 165:
                zwierze = FONETYCZNY_BARAN
                komentarz = "Wykryto głos z Twojego rodzinnego stada! Posłuchaj kumpla z pastwiska, nie pyskuj i nagraj psa!"
                naglowek_ekranu = "[Wykryto Samca - Tryb Barana]"
            else:
                zwierze = FONETYCZNA_KROWA
                komentarz = "Wykryto dźwięki z zagrody! Posłuchaj koleżanki z łąki, przestań wydawać rozkazy i daj psu dojść do głosu!"
                naglowek_ekranu = "[Wykryto Samicę - Tryb Krowy]"
                
            if st.session_state.licznik_ludzki == 1:
                wylosowany = f"{zwierze} Nie mogę przetłumaczyć tego, bo za szybko mówisz."
            elif st.session_state.licznik_ludzki == 2:
                wylosowany = f"{zwierze} Nie mogę przetłumaczyć - Mów wolno i wyraźnie. {komentarz}"
            else:
                wylosowany = f"{zwierze} {zwierze} A teraz powiedz to drukowanymi, patrząc w lustro! Człowieku, aplikacja służy do tłumaczenia zwierzaków, więc weź na wstrzymanie!"
                st.session_state.licznik_ludzki = 0
        else:
            st.session_state.licznik_ludzki = 0
            if TRYB_ANALIZY and wykryte_hz < 200:
                wylosowany = pobierz_tekst_kontekstowy(TEKSTY_GIGANT_STRES, "gigant")
                naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Sfrustrowany Gigant]"
                uzyj_neutralnego = True 
            elif TRYB_ANALIZY and 200 <= wykryte_hz < 450:
                wylosowany = pobierz_tekst_kontekstowy(TEKSTY_DUZY_OWCZAREK_ZABAWA, "duzy")
                naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Owczarek w akcji]"
            elif TRYB_ANALIZY and 450 <= wykryte_hz < 800:  # DODANE PASMO DLA ŚREDNICH PSÓW
                wylosowany = pobierz_tekst_kontekstowy(TEKSTY_SREDNI_BEAGLE, "sredni")
                naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Średni Spryciarz]"
            elif TRYB_ANALIZY and 800 <= wykryte_hz < 1200: # DODANE PASMO DLA MAŁYCH PSÓW
                wylosowany = pobierz_tekst_kontekstowy(TEKSTY_MALUCH, "maluch")
                naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Mały Wojownik]"
            elif TRYB_ANALIZY and wykryte_hz >= 1200:
                wylosowany = pobierz_tekst_kontekstowy(TEKSTY_MINIATURA_JAMNIK, "miniatura")
                naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Sfrustrowany Maluch]"
            else:
                if is_morning:
                    wylosowany = pobierz_tekst_kontekstowy(GRUPA_TEKSTY_PORANNE, "rano")
                    naglowek_ekranu = "[Poranny Bieguniem]"
                    uzyj_dodatkowego = False
                    if st.session_state.get("wyczerpana_rano", False): uzyj_neutralnego = True
                elif is_pre_noon:
                    wylosowany = pobierz_tekst_kontekstowy(GRUPA_TEKSTOW_PRZEDPOLUDNIOWYCH, "przedpoludnie")
                    naglowek_ekranu = "[Przedpołudniowy Samotnik]"
                    if st.session_state.get("wyczerpana_przedpoludnie", False): uzyj_neutralnego = True
                elif is_noon:
                    if st.session_state.ostatnie_pokazywane_zdanie == "Ty mi rzucaj smakołyk, a ja będę łapać.":
                        wylosowany = "Chyba, że wolisz żebym ciebie podgryzał."
                    else:
                        wylosowany = pobierz_tekst_kontekstowy(GRUPA_TEKSTOW_POLUDNIOWYCH, "poludnie")
                    naglowek_ekranu = "[Południowa Rozgrywka]"
                    if st.session_state.get("wyczerpana_poludnie", False): uzyj_neutralnego = True
                elif is_afternoon:
                    wylosowany = pobierz_tekst_kontekstowy(GRUPA_TEKSTOW_POPOLUDNIOWYCH, "popoludnie")
                    naglowek_ekranu = "[Popołudniowa Radość]"
                    if st.session_state.get("wyczerpana_popoludnie", False): uzyj_neutralnego = True
                elif is_evening:
                    wylosowany = pobierz_tekst_kontekstowy(TEKSTY_WIECZORNE, "wieczor")
                    naglowek_ekranu = "[Wieczorny Relaks]"
                    if st.session_state.get("wyczerpana_wieczor", False): uzyj_neutralnego = True
                elif is_night:
                    wylosowany = pobierz_tekst_kontekstowy(TEKSTY_NOCNE, "noc")
                    naglowek_ekranu = "[Nocny Alarm]"
                    uzyj_dodatkowego = False
                    
                if (is_pre_noon or is_noon or is_afternoon) and random.random() < 0.3:
                    wylosowany = pobierz_tekst_kontekstowy(ZDANIA_ROZKAZUJACE, "rozkazy")

    st.session_state.ostatnie_pokazywane_zdanie = wylosowany

    slowa_alarmowe = ["sfajdam", "posikam", "pęcherz", "kupkę", "srać", "rozerwie", "zrąbać"]
    if any(slowo in wylosowany.lower() for slowo in slowa_alarmowe):
        uzyj_dodatkowego = False

    final_tekst = wylosowany
    
    if uzyj_dodatkowego and not wymus_komunikat and not (TRYB_ANALIZY and 85 <= wykryte_hz <= 255):
        final_tekst += f" {random.choice(DODATKOWE_ZDANIA)}"
            
    if uzyj_neutralnego and not wymus_komunikat and not is_evening and not is_night:
        pula_neutralna = GRUPA_TEKSTOW_NEUTRALNYCH.copy()
        if not is_morning: pula_neutralna = [t for t in pula_neutralna if "dwa razy" not in t.lower()]
        if is_morning: pula_neutralna = [t for t in pula_neutralna if "miska jest pusta" not in t.lower()]
        if pula_neutralna: final_tekst += f" {random.choice(pula_neutralna)}"

    tekst_do_czytania = final_tekst.replace(".", ",").replace("!", ",")

    tts = gTTS(text=tekst_do_czytania, lang='pl', slow=False)
    fp_raw = io.BytesIO()
    tts.write_to_fp(fp_raw)
    fp_raw.seek(0)
    
    if TRYB_ANALIZY:
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
    else:
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
col_foot1, col_foot2 = st.columns(2)
with col_foot1:
    st.caption("HauTłumacz v10.4 - Stabilna wersja chmurowa.")
with col_foot2:
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

