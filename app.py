import streamlit as st
import io
import random
from datetime import datetime, time
from scipy.io import wavfile
import numpy as np
from gtts import gTTS

# --- BEZPIECZNA KONFIGURACJA STRONY ---
st.set_page_config(page_title="HauTłumacz PRO v12.2", page_icon="🐕", layout="centered")

# --- STRUMIEŃ STYLÓW GLOBALNYCH ---
st.markdown("""
    <style>
    /* Główne tło strony - stonowany, ciemniejszy pastelowy szary/zielony */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { 
        background-color: #e2e8e4 !important; 
    }
    
    /* Tło bocznego panelu (Menu) - dopasowane i ciemniejsze */
    [data-testid="stSidebar"] { 
        background-color: #cbd5ce !important; 
    }
    
    h1, h2, h3 { color: #1e4620 !important; text-align: center; margin-top: 10px; }
    
    /* POWIĘKSZENIE CAŁEGO WIDŻETU NAGRYWANIA I IKONY MIKROFONU */
    .stAudioInput { 
        border: 3px dashed #81c784 !important; 
        border-radius: 16px; 
        padding: 20px !important; 
        background-color: #f1f5f2; 
        transform: scale(1.05); 
        margin: 20px auto !important;
    }
    
    /* Zwiększenie wewnętrznej ikony mikrofonu */
    .stAudioInput button, .stAudioInput svg, [data-testid="stAudioInput"] svg {
        width: 45px !important;      
        height: 45px !important;     
        transition: transform 0.2s;
    }

    /* Efekt po najechaniu myszką na mikrofon */
    .stAudioInput button:hover {
        transform: scale(1.15);
    }
    
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
    
    /* MATOWE KARTY WPISÓW W ENCYKLOPEDII */
    .blog-card {
        background-color: #d1dad4 !important; 
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-left: 5px solid #1e4620;
        color: #1e3321 !important; 
    }
    
    /* KARTY PROFILI PSA */
    .dog-profile-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border-left: 6px solid #81c784;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        color: #1e3321;
    }
    
    /* CHMURKI CZATU */
    .chat-bubble {
        background-color: #d1dad4;
        padding: 10px 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        border-bottom-left-radius: 2px;
        color: #1e3321;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICJALIZACJA BAZY SYSTEMU I TRWAŁEJ PAMIĘCI (ZGODNIE Z RODO) ---
if "ostatni_tekst" not in st.session_state: st.session_state.ostatni_tekst = ""
if "wykorzystane_teksty" not in st.session_state: st.session_state.wykorzystane_teksty = set()
if "uzytkownik_zalogowany" not in st.session_state: st.session_state.uzytkownik_zalogowany = None

# Lokalna baza danych w pamięci sesji (zastępuje serwer SQL w Streamlicie)
if "baza_psow" not in st.session_state:
    st.session_state.baza_psow = {
        "Burek": {"klasa": "duzy", "wlasciciel": "przyklad@hauhau.online", "posty": ["[🥳 WYNIK]: Dawaj parówkę albo sam sobie weznę!"]},
        "Chrupek": {"klasa": "miniaturka", "wlasciciel": "test@hauhau.online", "posty": ["[😨 WYNIK]: Jestem małym, wściekłym demonem!"]}
    }
if "baza_wiadomosci" not in st.session_state:
    st.session_state.baza_wiadomosci = []
# ==================== BAZY TEKSTÓW Z TWOJEGO KODU ====================
TEKSTY_WARCZENIE_ALARM = [
    "Zatrzymaj się. Natychmiast. Nie testuj mojej cierpliwości.",
    "Nie podchodź. To nie są żarty, ani zabawa.",
    "Odsuń się powoli. Widzę twój każdy ruch i jestem w pełnej godowości do ataku.",
    "Zostaw mnie w spokoju. Ostrzegam cię ostatni raz, zanim stracę nad sobą kontrolę.",
    "Odejdź stąd natychmiast, bo pożałujesz tej pewności siebie.",
    "Cofnij się, nie żartuję. To moje ostatnie ostrzeżenie.",
    "Ani kroku dalej. To nie jest żart. Koniec zabawy."
]
GRUPA_TEKSTY_PORANNE = ["Bieguniem, bieguniem, bo się posikam!", "Nie musimy wychodzić, ale zastanów się, czy to się spierze.", "Chodź szybko to zobaczysz sąsiadkę bez makijażu!", "Szybko, bo za chwilę mi tyłek rozerwie!", "Pospiesz się, bo narobię ci na środek pokoju!", "Sikać mi się chce, szybko!", "Nie musisz wstawać, wiem gdzie mogę się zrąbać.", "No wstawaj, obiecałem, że wyprowadzę cię na spacer.", "W zdrowym ciele zdrowy duch i ja to popieram.", "Carpe diem - chwytaj smycz!"]
GRUPA_TEKSTOW_PRZEDPOLUDNIOWYCH = ["No i co ja tak w samotności mam być przez resztę dnia?", "O której mogę się ciebie spodziewać?", "Nie wpadniesz na przerwę?", "Będzie fajna kość, wpadnij na chwilę.", "Weź sobie godzinkę wolnego w pracy.", "Oj wpadnij choć na chwilę to dam ci kość!", "Nie idź do pracy, pokopmy dołki.", "Weź mnie ze sobą, będę pilnować pieniędzy."]
TEKSTY_DZIENNE_ZABAWA = ["Interesują mnie tylko konkrety - gdzie są parówki?!", "Konkrety to smakołyki.", "Jaki patyk? Rzuć mi parówkę!", "Pobiegamy razem?", "Wyczuwam tutaj tę sukę i mam nadzieję, że się wytłumaczysz?!", "Może znów spotkamy tę rudą, jest niezła?!", "Już nie mogę się doczekać, gdy zobaczę jak sprzątasz po mnie!", "Dobra, przemilczę to, gdy tylko zobaczę zawartość miski."]
GRUPA_TEKSTOW_POLUDNIOWYCH = ["Fajnie, że jesteś w domu, razem iOS czymś wymyślimy.", "Ty mi rzucaj smakołyk, a ja będę łapać.", "Jestem gotowy, rzucaj kość.", "Ja nie wiem, jak koty mogą leżeć tak całymi dniiami.", "Rzucaj tę kość, tylko tym razem dobrze!", "Pobiegamy razem?"]
GRUPA_TEKSTOW_POPOLUDNIOWYCH = ["Tak jak się umawialiśmy - jestem tutaj.", "O której to wracasz?", "Fajnie, że jesteś, ale teraz szybko chodźmy.", "Jeszcze chwila a się sfajdam!", "Chodź szybko na spacer to zobaczysz coś ciekawego.", "Już miałem gryźć meble, by nie wyjść z wprawy."]
TEKSTY_WIECZORNE = ["Jeszcze tylko kupkę, śiku i można w kimono!", "Zaraz mi pęcherz rozerwie.", "Mogę sfajdać się tutaj - nie musimy wychodzić!", "Fundamentalne pytanie brzmi - gdzie mam narobić?", "Wyczułem fajny towar w okolicy - maybe jest singlem?", "Na razie tylko puściłem bąka, ale kto wie, co czas przyniesie.", "Chodź pokażę ci straszną babę.", "A wiesz, że sąsiadka ma coś na sumieniu?", "Cisza nocna jest od dwudziestej czwartej?"]
TEKSTY_NOCNE = ["Ludzie! Ludzie! Ludziska!!!", "Ja tutaj strasznie cierpię.", "Ludzie, ja tutaj jestem sam!", "Ludzie, oni mnie straszyli, że będą gwałcić!", "Ludzie, właściciel tego mieszkania ma skitrany gdzieś towar!", "Niech ktoś zadzwoni do opieki nad zwierzętami!", "Ludzie, dajcie mi tutaj kogoś do zabawy.", "Niech mi ktoś pomoże!!!", "Jest tam kto?", "Pomocy! Ludzie, tutaj jakiś szalony pies nawalił i strasznie śmierdzi!!!", "W co ja się wpakowałem...!!!"]

TEKSTY_DUZY_OWCHAREK_ZABAWA = ["Dawaj parówkę albo sam sobie wezmę kawał mięcha!", "Widziałem, jak grdyka ci skacze. Jadłeś i się nie podzieliłeś człowieku?", "Wolisz rzucać mi patyk czy uciekać przed moimi zębami - wybieraj!", "A teraz rzuć swojską!"]
TEKSTY_SREDNI_BEAGLE = ["Wykryto ton rasy średniej (Beagle/Spaniel/Border)! Mam idealne proporcje sprytu i energii.", "Może i nie jestem gigantem, ale za to potrafię wywęszyć każdą parówkę w promieniu kilometra!", "Zaraz zrobię ci tutaj małe przemeblowanie, jeśli natychmiast nie pójdziemy pobiegać!"]
TEKSTY_MALUCH = ["Wykryto małego spryciarza (Mops/Buldog/Jack Russell)! Mały ciałem, ale potężny duchem!", "Nie patrz tak na mnie z góry! Moje nogi są krótkie, ale gonić kota potrafię szybciej niż myślisz."]
TEKSTY_MINIATURA_JAMNIK = ["Może i jestem mały jak parówka, ale gniew mam tak wielki, że bardzo długo będziesz to spotkanie wspominać!", "Jestem małym, wściekłym demonem! But potrafię zajść ci za skórę!"]

FONETYCZNY_BARAN = "Bęęęęęę!"
FONETYCHNA_KROWA = "Móóóóóó!"

# --- STRUMIENIOWA ANALIZA AUDIO (FFT) ---
def analizuj_audio(audio_bytes):
    try:
        sample_rate, data = wavfile.read(io.BytesIO(audio_bytes))
        if len(data.shape) > 1:
            data = data.mean(axis=1)
        if len(data) == 0:
            return 600.0, False, False
            
        okienko = int(sample_rate * 0.05) 
        energie_okienek = [np.sum(data[i:i+okienko]**2) for i in range(0, len(data), okienko)]
        if len(energie_okienek) == 0:
            return 600.0, False, False
            
        max_energia = max(energie_okienek)
        srednia_energia = np.mean(energie_okienek)
        czy_impulsowy = (max_energia / (srednia_energia + 1e-6)) > 4.5
        
        fft_spectrum = np.fft.rfft(data)
        freq = np.fft.rfftfreq(len(data), d=1.0/sample_rate)
        
        magnituda = np.abs(fft_spectrum)
        szczytowa_indeks = np.argmax(magnituda)
        wykryte = freq[szczytowa_indeks]
        
        srednia_widma = np.mean(magnituda)
        max_widma = magnituda[szczytowa_indeks]
        czystosc_tonalna = max_widma / (srednia_widma + 1e-6)
        
        czy_warczenie = False
        calkowita_energia = np.sum(magnituda)
        
        if calkowita_energia > 0:
            niskie_pasmo = (freq >= 40) & (freq <= 300)
            energia_basu = np.sum(magnituda[niskie_pasmo])
            if (energia_basu / calkowita_energia) > 0.20:
                czy_warczenie = True

        if wykryte < 30 or wykryte > 4000:
            return 600.0, False, False

        czy_to_melodyjne_miau = czystosc_tonalna > 120.0
        czy_to_pies = czy_warczenie or (czy_impulsowy and not czy_to_melodyjne_miau)
            
        return float(wykryte), czy_warczenie, czy_to_pies
    except:
        return 600.0, False, False

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
# ==================== SEKCJA GŁÓWNA TŁUMACZA (Z USZCZELNIONĄ BLOKADĄ) ====================
def sekcja_tlumacza():
    st.title("🐕 HauTłumacz PRO v12.2")
    st.write("---")
    
    # SYSTEMOWE SPRZĘŻENIE Z PROFILAMI PSÓW (RODO)
    moje_psy = [imie for imie, dane in st.session_state.baza_psow.items() if dane["wlasciciel"] == st.session_state.uzytkownik_zalogowany]
    
    # WYBÓR KLASY GABARYTOWEJ (GUZICZKI FILTRACJI PASMOWEJ)
    st.write("### 🏷️ Krok 1: Wybierz klasę wielkości psa przed nagraniem:")
    klasa_wybrana = st.radio(
        "Wielkość psa:",
        ["Miniaturka (np. York, Maltańczyk)", "Średni (np. Beagle, Border Collie)", "Duży (np. Owczarek, Rottweiler)"],
        horizontal=True
    )
    
    if st.session_state.uzytkownik_zalogowany and moje_psy:
        wybrany_pies = st.selectbox("Wybierz profil psa, którego nagrywasz:", moje_psy)
        st.success(f"Powiązano z psem: {wybrany_pies}")
    else:
        wybrany_pies = None

    st.write("---")
    audio_nagrane = st.audio_input("Nagraj dźwięk:")
    
    if audio_nagrane is not None:
        audio_bytes = audio_nagrane.read()
        wykryte_hz, czy_warczenie, czy_to_pies = analizuj_audio(audio_bytes)
        
        teraz = datetime.now().time()
        final_tekst = ""
        naglowek_ekranu = ""
        tryb_alarmu = False
        styl_glosu = "sredni"  
        
        is_morning = time(4, 30) <= teraz < time(7, 0)
        is_pre_noon = time(7, 0) <= teraz < time(11, 0)
        is_noon = time(11, 0) <= teraz < time(14, 0)
        is_afternoon = time(14, 0) <= teraz < time(19, 0)
        is_evening = time(19, 0) <= teraz < time(23, 0)
        is_night = teraz >= time(23, 0) or teraz < time(4, 30)

        st.sidebar.metric(label="Wykryta częstotliwość", value=f"{int(wykryte_hz)} Hz")

        # ==================== RYGORYSTYCZNY, ODSEPAROWANY SYSTEM DECYZYJNY HZ ====================
        
        # UTWARDZONA BLOKADA GATUNKOWA - Odcina ludzkie wycie poniżej 450 Hz, jeśli dźwięk nie ma dynamiki psa
        if wykryte_hz < 450 and not czy_to_pies:
            final_tekst = "Wykryty dźwięk nie posiada wybuchowej dynamiki ani struktury psiego szczekania/warczenia. Przestań wyć jak człowiek i pozwól dojść psu do głosu! 🐕"
            naglowek_ekranu = "[⚠️ LUDZKI BEŁKOT WYKRYTY]"
            czy_warczenie = False

        # 1. FILTR DLA MINIATURKI (Akceptuje TYLKO wysokie pasmo: 800 - 2000 Hz)
        elif "Miniaturka" in klasa_wybrana:
            styl_glosu = "miniatura"
            if wykryte_hz < 800 or wykryte_hz > 2000:
                final_tekst = f"Wykryto {int(wykryte_hz)} Hz. To pasmo jest zbyt niskie dla miniaturki! Zaznaczono małego psa, a nagrano większego zwierzaka."
                naglowek_ekranu = "[⚠️ BŁĄD ZAKRESU - TO NIE MINIATURKA]"
                czy_warczenie = False 
            else:
                if 800 <= wykryte_hz <= 1000:
                    final_tekst = pobierz_tekst_kontekstowy(TEKSTY_MINIATURA_JAMNIK)
                    naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Miniaturka - Zabawa]"
                else:
                    final_tekst = pobierz_tekst_kontekstowy(TEKSTY_NOCNE)
                    naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Miniaturka - Emocje]"

        # 2. FILTR DLA PSA ŚREDNIEGO (Akceptuje pasmo: 70 - 950 Hz)
        elif "Średni" in klasa_wybrana:
            styl_glosu = "sredni"
            if wykryte_hz < 70 or wykryte_hz > 950:
                final_tekst = f"Wykryto {int(wykryte_hz)} Hz. To nie jest pasmo rasy średniej! Spróbuj zmienić wybór guzików."
                naglowek_ekranu = "[⚠️ BŁĄD ZAKRESU - TO NIE ŚREDNI PIES]"
                czy_warczenie = False
            else:
                if 70 <= wykryte_hz <= 95:
                    final_tekst = pobierz_tekst_kontekstowy(TEKSTY_WARCZENIE_ALARM)
                    naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Średni - Stres]"
                    tryb_alarmu = True
                elif 96 <= wykryte_hz <= 125:
                    final_tekst = pobierz_tekst_kontekstowy(TEKSTY_SREDNI_BEAGLE)
                    naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Średni - Zabawa]"
                else: 
                    final_tekst = pobierz_tekst_kontekstowy(TEKSTY_DZIENNE_ZABAWA)
                    naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Średni - Komunikat]"

        # 3. FILTR DLA DUŻEGO PSA (Akceptuje TYLKO głębokie pasmo: 40 - 750 Hz)
        elif "Duży" in klasa_wybrana:
            styl_glosu = "duzy"
            if wykryte_hz < 40 or wykryte_hz > 750:
                final_tekst = f"Wykryto {int(wykryte_hz)} Hz. Dźwięk jest zbyt wysoki dla dużego psa! Przełącz zakres na mniejszą rasę."
                naglowek_ekranu = "[⚠️ BŁĄD ZAKRESU - TO NIE DUŻY PIES]"
                czy_warczenie = False
            else:
                if 45 <= wykryte_hz <= 65:
                    final_tekst = pobierz_tekst_kontekstowy(TEKSTY_WARCZENIE_ALARM)
                    naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Duży - Stres]"
                    tryb_alarmu = True
                elif 66 <= wykryte_hz <= 85:
                    final_tekst = pobierz_tekst_kontekstowy(TEKSTY_DUZY_OWCHAREK_ZABAWA)
                    naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Duży - Zabawa]"
                else: 
                    final_tekst = pobierz_tekst_kontekstowy(GRUPA_TEKSTOW_POPOLUDNIOWYCH)
                    naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Duży - Ekscytacja]"

        # OSTATECZNY BLOK REAKCJI CZASOWEJ (Gdy wyłączona jest filtracja profilowa)
        if final_tekst == "":
            if not czy_to_pies:
                final_tekst = "Wykryty dźwięk nie posiada wybuchowej dynamiki psiego szczekania. Spróbuj zaszczekać wyraźniej!"
                naglowek_ekranu = "[⚠️ Dźwięk zignorowany]"
            else:
                if is_morning: final_tekst = pobierz_tekst_kontekstowy(GRUPA_TEKSTY_PORANNE)
                elif is_pre_noon: final_tekst = pobierz_tekst_kontekstowy(GRUPA_TEKSTOW_PRZEDPOLUDNIOWYCH)
                elif is_noon: final_tekst = pobierz_tekst_kontekstowy(GRUPA_TEKSTOW_POLUDNIOWYCH)
                elif is_afternoon: final_tekst = pobierz_tekst_kontekstowy(GRUPA_TEKSTOW_POPOLUDNIOWYCH)
                elif is_evening: final_tekst = pobierz_tekst_kontekstowy(TEKSTY_WIECZORNE)
                else: final_tekst = pobierz_tekst_kontekstowy(TEKSTY_NOCNE)
                naglowek_ekranu = "[Wynik Analizy Ogólnej]"

        # ==================== MODYFIKATOR PITCH GENERATORA LEKTORA ====================
        tekst_do_czytania = final_tekst.replace(".", ",").replace("!", ",")
        tts = gTTS(text=tekst_do_czytania, lang='pl', slow=False)
        fp_raw = io.BytesIO()
        tts.write_to_fp(fp_raw)
        fp_raw.seek(0)
        
        try:
            sample_rate, data = wavfile.read(fp_raw)
            mnoznik_predkosci = 1.30 if tryb_alarmu else 1.15
            if styl_glosu in ["maly", "miniatura"]: mnoznik_predkosci = 1.25
            
            skurczony_rozmiar = int(len(data) / mnoznik_predkosci)
            indeksy = np.round(np.linspace(0, len(data) - 1, skurczony_rozmiar)).astype(int)
            przyspieszone_data = data[indeksy]
            
            if styl_glosu == "duzy": sample_rate = int(sample_rate * 0.82)  
            elif styl_glosu in ["maly", "sredni"]: sample_rate = int(sample_rate * 1.10)  
            elif styl_glosu == "miniatura": sample_rate = int(sample_rate * 1.30)  
                
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
                st.markdown(f"<div class='red-alert-box'>{naglowek_ekranu}<br><br>{final_tekst}</div>", unsafe_allow_html=True)
            else:
                st.success(f"{naglowek_ekranu}: {final_tekst}")
                
        if wybrany_pies and final_tekst != "" and "[⚠️" not in naglowek_ekranu:
            if st.button("📱 Udostępnij to szczeknięcie na profilu psa"):
                st.session_state.baza_psow[wybrany_pies]["posty"].append(f"{naglowek_ekranu}: {final_tekst}")
                st.success("Dodano pomyślnie na psią tablicę!")

    # --- TWÓJ ORYGINALNY, PEŁNY REGULAMIN STRONY (NIEUCIĘTY) ---
    st.write("---")
    if st.button("📝 Regulamin strony"):
        st.info("""
        **Regulamin i informacje o serwisie hauhau.online**
        
        Drogi użytkowniku.
        Jest mi bardzo miło gościć Ciebie na stronie „hauhau.online” i liczę na to, że efekt mojej pracy sprawi Ci wiele przyjemności w trakcie użytkowania tłumacza oraz przyczyni się do pogłębienia relacji między psiakiem a człowiekiem. 
        
        - Na stronie hauhau.online nie są gromadzone żadne dane oraz dźwięki wydobywane przez zwierzęta, które nagrasz w celu przetłumaczenia. 
        - Na stronie hauhau.online nie są gromadzone żadne tłumaczenia, a każdy kolejny proces nagrywania kasuje nagranie poprzednie tak samo jak opuszczenie strony. Więc jeśli chcesz zachować tekst, utrwal go samodzielnie.
        
        **Zasady korzystania z profili i komunikatora:**
        - System posiada dodatkowe moduły kont społecznościowych, które wymagają podania i weryfikacji adresu e-mail oraz numeru telefonu w celu zapewnienia bezpieczeństwa społeczności.
        - Dane te są przetwarzane tymczasowo. Zgodnie z RODO, w każdej chwili możesz kliknąć czerwony przycisk „Usuń moje konto” w panelu bocznym, aby bezpowrotnie wymazać wszelkie dane swoje oraz swoich psów z pamięci systemu.
        - Na platformie obowiązuje bezwzględny zakaz publikowania treści nielegalnych, handlu substancjami zakazanymi oraz używania wulgaryzmów. Konta naruszające ten punkt będą natychmiastowo blokowane, a ich dane (w tym numer telefonu i IP) mogą zostać przekazane organom ścigania.
        
        Cały proces tłumaczenia odbywa się na bieżąco i jest on wynikiem klasyfikacji przez algorytm i dobierania słów zapisanych w bazie danych, która z każdym dniem powiększa się o kolejne zwroty i słowa. 
        
        W celu przetłumaczenia bardziej skomplikowanych dźwięków zapraszam do kontaktu drogą elektroniczną pod adresem: hauhau.kontakt@gmail.com w celu ustalenia warunków tłumaczenia psisięgłego – (zastrzegając, że czas odpowiedzi może być dłuższy). Dołożę wszelkich starań, aby tłumaczenie spełniało najwyższe standardy. 
        
        Życzę wszystkim wiele radości z użytkowania tłumacza!
        """)


# ==================== ENCYKLOPEDIA HZ (BLOG) ====================
def sekcja_bloga():
    st.title("🌐 Encyklopedia Częstotliwości Hz")
    st.write("Odkryj niewidzialny i niesłyszalny świat wibracji, który rządzi życiem na Ziemi.")
    st.write("---")
    st.markdown("""
    <div class='blog-card'>
        <h3>🔊 Post #1: Tajemny język natury – Czym są częstotliwości Hz?</h3>
        <p><b>Data publikacji:</b> Dzisiaj | <b>Autor:</b> Tery</p>
        <p>Większość z nas postrzega świat tylko przez to, co widzą ludzkie oczy i słyszą ludzkie uszy. 
        Człowiek rejestruje dźwięki w granicach od 20 do 20 000 Hz. Wszystko poniżej i powyżej tej granicy 
        pozostaje dla nas kompletną ciszą. Jednak dla reszty planety ta "cisza" to tętniący życiem kanał informacyjny.</p>
        <p>Zrozumienie częstotliwości pozwala całkowicie zmienić nasz stosunek do otaczającego nas świata. 
        Zwierzęta, rośliny, a nawet mikroorganizmy nieustannie nadają i odbierają sygnały falowe. 
        Wibracja to pierwotna forma komunikacji w kosmosie.</p>
    </div>
    <div class='blog-card'>
        <h3>🌱 Post #2: Czy rośliny mają uszy? Jak zieleń reaguje na wibracje</h3>
        <p><b>Data publikacji:</b> Dzisiaj | <b>Autor:</b> Tery</p>
        <p>Okazuje się, że flora nie jest ani niema, ani głucha. Najnowsze badania z zakresu bioakustyki dowodzą, 
        że korzenie roślin potrafią zlokalizować podziemne źródła wody, bezbłędnie wychwytując niskie częstotliwości 
        szumu płynącej cieczy. Co więcej, niektóre kwiaty potrafią w ciągu kilku sekund drastycznie zwiększyć stężenie cukru 
        w swoim nektarze, gdy tylko zarejestrują częstotliwość machania skrzydeł (Hz) zbliżającej się pszczoły!</p>
        <p>Świat częstotliwości pokazuje, że życie wokół nas jest o wiele bardziej świadome i połączone, niż nam się wydaje.</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== SEKCJA PROFILI PSÓW ====================
def sekcja_profili():
    st.title("📱 Zarządzanie Psami")
    if not st.session_state.uzytkownik_zalogowany:
        st.warning("🔒 Aby stworzyć profil psa, najpierw przejdź do lewego panelu bocznego, zaznacz okienko RODO i zaloguj się swoim mailem!")
    else:
        st.subheader("➕ Stwórz profil dla swojego pupila")
        imie = st.text_input("Imię psa:")
        klasa = st.selectbox("Klasa wielkości (Zgodna z matrycą Hz oraz tonem lektora):", ["miniaturka", "sredni", "duzy"])
        if st.button("Zapisz profil psa 💾"):
            if imie:
                st.session_state.baza_psow[imie] = {
                    "klasa": klasa,
                    "wlasciciel": st.session_state.uzytkownik_zalogowany,
                    "posty": []
                }
                st.success(f"Pies {imie} został oficjalnie zarejestrowany w hauhau.online!")
                st.rerun()

    st.write("---")
    st.subheader("🐾 Aktywne profile w sieci:")
    for imie, dane in st.session_state.baza_psow.items():
        st.markdown(f"""
        <div class='dog-profile-card'>
            <h4>🐕 {imie} (Klasa: {dane['klasa'].upper()})</h4>
            <p><b>Właściciel / Menedżer konta:</b> {dane['wlasciciel']}</p>
        </div>
        """, unsafe_allow_html=True)
        if dane["posty"]:
            st.write("📌 *Ostatnie udostępnione tłumaczenia na tablicy:*")
            for post in dane["posty"][-2:]:
                st.info(post)

# ==================== SEKCJA KOMUNIKATORA (Z PANELEM FB STORIES) ====================
def sekcja_komunikatora():
    st.title("💬 Psi Komunikator tekstowy")
    moje_psy = [imie for imie, dane in st.session_state.baza_psow.items() if dane["wlasciciel"] == st.session_state.uzytkownik_zalogowany]
    
    if not st.session_state.uzytkownik_zalogowany:
        st.error("🔒 SYSTEM ZABLOKOWANY: Krok 1 - Przejdź do lewego panelu bocznego, zaznacz zgodę RODO i wpisz swój adres e-mail, aby zalogować się jako Menedżer.")
    elif not moje_psy:
        st.warning("🔒 Krok 2 - Jesteś zalogowany, ale Twój portfel jest pusty! Przejdź w menu bocznym do zakładki '📱 Profile Psów' i zarejestruj chociaż jednego psa. Komunikator wymaga tożsamości zwierzaka!")
    else:
        st.success(f"🔓 Witamy w sieci hauhau.online! Rozmawiasz z profilu menedżerskiego: {st.session_state.uzytkownik_zalogowany}")
        
        # ------------------------------------------------------------------
        # Dynamiczne okienko dostępnych psów w stylu Facebook Messenger
        # ------------------------------------------------------------------
        st.write("🟢 **Dostępne psy w sieci hauhau.online:**")
        liczba_psow = len(st.session_state.baza_psow)
        if liczba_psow > 0:
            kolumny_avatarow = st.columns(min(liczba_psow, 6))
            for i, (imie_psa, dane_psa) in enumerate(st.session_state.baza_psow.items()):
                if dane_psa["klasa"] == "miniaturka": avatar = "🐶"
                elif dane_psa["klasa"] == "sredni": avatar = "🐕"
                else: avatar = "🦮"
                
                with kolumny_avatarow[i % 6]:
                    st.markdown(f"""
                    <div style="text-align: center; margin-bottom: 15px;">
                        <div style="
                            width: 60px; 
                            height: 60px; 
                            border-radius: 50%; 
                            background-color: #81c784; 
                            font-size: 32px; 
                            line-height: 60px; 
                            margin: 0 auto;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                            border: 3px solid #fff;
                            position: relative;
                        ">
                            {avatar}
                            <span style="
                                width: 12px; 
                                height: 12px; 
                                background-color: #4caf50; 
                                border-radius: 50%; 
                                position: absolute; 
                                bottom: 2px; 
                                right: 2px; 
                                border: 2px solid white;
                            "></span>
                        </div>
                        <p style="margin-top: 5px; font-weight: bold; font-size: 14px; color: #1e4620; margin-bottom: 0;">{imie_psa}</p>
                    </div>
                    """, unsafe_allow_html=True)
        st.write("---")
        
        nadawca = st.selectbox("Mów w imieniu psa:", moje_psy)
        odbiorcy = [imie for imie in st.session_state.baza_psow.keys() if imie != nadawca]
        
        if not odbiorcy:
            st.info("Na razie jesteś jedynym zarejestrowanym psem w sieci. Poczekaj na innych użytkowników lub przejdź do zakładki 'Profile Psów' i stwórz drugiego psa z innego maila do testów!")
        else:
            odbiorca = st.selectbox("Wybierz psa do rozmowy:", odbiorcy)
            
            st.write("🐾 **Szybkie, psie zwroty akcji (Szablony z humorem):**")
            col1, col2, col3 = st.columns(3)
            szablon = ""
            with col1:
                if st.button("Bone"): szablon = "*Macha energicznie ogonem i patrzy na Twoją miskę* Dasz gryza?"
            with col2:
                if st.button("Tree"): szablon = "Hau! Idziemy sprawdzić zapachy na wybiegu przy bloku?"
            with col3:
                if st.button("Angry"): szablon = "*Warczy i stawia sierść* Nie podchodź do mojego człowieka, to mój rewir!"

            wiadomosc = st.text_input("Napisz coś od siebie...", value=szablon)
            if st.button("Wyślij szczeknięcie 🚀"):
                if wiadomosc:
                    st.session_state.baza_wiadomosci.append({
                        "od": nadawca,
                        "do": odbiorca,
                        "tekst": wiadomosc,
                        "czas": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()

            st.write("---")
            st.subheader("📥 Psia skrzynka odbiorcza")
            for msg in st.session_state.baza_wiadomosci:
                if (msg["od"] == nadawca and msg["do"] == odbiorca) or (msg["od"] == odbiorca and msg["do"] == nadawca):
                    st.markdown(f"""
                    <div class='chat-bubble'>
                        <b>{msg['od']} ➡️ {msg['do']}:</b> {msg['tekst']} <span style='float:right; font-size:10px; color:gray;'>{msg['czas']}</span>
                    </div>
                    """, unsafe_allow_html=True)

# ==================== BEZPIECZNE STRUKTURY LOGOWANIA W SIDEBARZE (RODO) ====================
st.sidebar.title("🔐 Autoryzacja RODO")
if st.sidebar.checkbox("Akceptuję regulamin i przetwarzanie danych (RODO)"):
    if not st.session_state.uzytkownik_zalogowany:
        email_input = st.sidebar.text_input("Wpisz swój email:")
        if st.sidebar.button("Zaloguj się jako Menedżer"):
            if email_input:
                st.session_state.uzytkownik_zalogowany = email_input
                st.rerun()
    else:
        st.sidebar.success(f"Zalogowano: {st.session_state.uzytkownik_zalogowany}")
        if st.sidebar.button("🚨 USUŃ MOJE KONTO (Kaskadowe czyszczenie RODO)"):
            user = st.session_state.uzytkownik_zalogowany
            st.session_state.baza_psow = {k: v for k, v in st.session_state.baza_psow.items() if v['wlasciciel'] != user}
            st.session_state.uzytkownik_zalogowany = None
            st.sidebar.info("Wszystkie dane osobowe i psie zostały trwale wymazane.")
            st.rerun()
else:
    st.session_state.uzytkownik_zalogowany = None
    st.sidebar.warning("Musisz zaznaczyć RODO, aby odblokować logowanie.")

# ==================== NAVIGATION / NAWIGACJA (PASEK BOCZNY) ====================
st.sidebar.title("🐾 Nawigacja") 
wybór = st.sidebar.radio("Przejdź do:", ["🐕 HauTłumacz", "📱 Profile Psów", "💬 Psi Komunikator", "🌐 Encyklopedia Hz (Blog)"])

if wybór == "🐕 HauTłumacz":
    sekcja_tlumacza()
elif wybór == "📱 Profile Psów":
    sekcja_profili()
elif wybór == "💬 Psi Komunikator":
    sekcja_komunikatora()
elif wybór == "🌐 Encyklopedia Hz (Blog)":
    sekcja_bloga()

