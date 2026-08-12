import streamlit as st
import io
import random
import os
from datetime import datetime, time
import soundfile as sf
import numpy as np
import streamlit.components.v1 as components
import speech_recognition as sr  # Zaawansowane rozpoznawanie mowy ludzkiej
import requests  # Obsługa bezpiecznych zapytań do API ElevenLabs

# --- BEZPIECZNA KONFIGURACJA STRONY (WERSJA VIRAL MVP v13.2 - STABLE RUN) ---
st.set_page_config(page_title="HauTłumacz PRO v13.2", page_icon="🐕", layout="centered")

# --- STRUMIEŃ STYLÓW GLOBALNYCH ---
st.markdown("""
    <style>
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { 
        background-color: #e2e8e4 !important; 
    }
    [data-testid="stSidebar"] { 
        background-color: #cbd5ce !important; 
    }
    h1, h2, h3 { color: #1e4620 !important; text-align: center; margin-top: 10px; }
    
    .stAudioInput { 
        border: 3px dashed #81c784 !important; 
        border-radius: 16px; 
        padding: 20px !important; 
        background-color: #f1f5f2; 
        transform: scale(1.05); 
        margin: 20px auto !important;
    }
    
    .stAudioInput button, .stAudioInput svg, [data-testid="stAudioInput"] svg {
        width: 45px !important;      
        height: 45px !important;     
        transition: transform 0.2s;
    }
    .stAudioInput button:hover { transform: scale(1.15); }
    
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
    
    .blog-card {
        background-color: #d1dad4 !important; 
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-left: 5px solid #1e4620;
        color: #1e3321 !important; 
    }
    </style>
""", unsafe_allow_html=True)

# --- INICJALIZACJA PAMIĘCI SYSTEMU ---
if "ostatni_tekst" not in st.session_state: st.session_state.ostatni_tekst = ""
if "wykorzystane_teksty" not in st.session_state: st.session_state.wykorzystane_teksty = set()
if "ostatni_byl_alert_garnki" not in st.session_state: st.session_state.ostatni_byl_alert_garnki = False
# ==================== BAZY TEKSTÓW Z TWOJEGO KODU ====================
TEKSTY_WARCZENIE_ALARM = [
    "Zatrzymaj się. Natychmiast. Nie testuj mojej cierpliwości.",
    "Nie podchodź. To nie są żarty, ani zabawa.",
    "Odsuń się powoli. Widzę twój każdy ruch i jestem w pełnej gotowości do ataku.",
    "Zostaw mnie w spokoju. Ostrzegam cię ostatni raz, zanim stracę nad sobą kontrolę.",
    "Odejdź stąd natychmiast, bo pożałujesz tej pewności siebie.",
    "Cofnij się, nie żartuję. To moje ostatnie ostrzeżenie.",
    "Ani kroku dalej. To nie jest żart. End of fun."
]
GRUPA_TEKSTY_PORANNE = ["Bieguniem, bieguniem, bo się posikam!", "Nie musimy wychodzić, ale zastanów się, czy to się spierze.", "Chodź szybko to zobaczysz sąsiadkę bez makijażu!", "Szybko, bo za chwilę mi tyłek rozerwie!", "Pospiesz się, bo narobię ci na środek pokoju!", "Sikać mi się chce, szybko!", "Nie musisz wstawać, wiem gdzie mogę się zrąbać.", "No wstawaj, obiecałem, że wyprowadzę cię na spacer.", "W zdrowym ciele zdrowy duch i ja to popieram.", "Carpe diem - chwytaj smycz!"]
GRUPA_TEKSTOW_PRZEDPOLUDNIOWYCH = ["No i co ja tak w samotności mam być przez resztę dnia?", "O której mogę się ciebie spodziewać?", "Nie wpadniesz na przerwę?", "Będzie fajna kość, wpadnij na chwilę.", "Weź sobie godzinkę wolnego w pracy.", "Oj wpadnij choć na chwilę to dam ci kość!", "Nie idź do pracy, pokopmy dołki.", "Weź mnie ze sobą, będę pilnować pieniędzy."]
TEKSTY_DZIENNE_ZABAWA = ["Interesują mnie tylko konkrety - gdzie są parówki?!", "Konkrety to smakołyki.", "Jaki patyk? Rzuć mi parówkę!", "Pobiegamy razem?", "Wyczuwam tutaj tę sukę i mam nadzieję, że się wytłumaczysz?!", "Może znów spotkamy tę rudą, jest niezła?!", "Już nie mogę się doczekać, gdy zobaczę jak sprzątasz po mnie!", "Dobra, przemilczę to, gdy tylko zobaczę zawartość miski."]
GRUPA_TEKSTOW_POLUDNIOWYCH = ["Fajnie, że jesteś w domu, razem coś wymyślimy.", "Ty mi rzucaj smakołyk, a ja będę łapać.", "Jestem gotowy, rzucaj kość.", "Ja nie wiem, jak koty mogą leżeć tak całymi dniiami.", "Rzucaj tę kość, tylko tym razem dobrze!", "Pobiegamy razem?"]
GRUPA_TEKSTOW_POPOLUDNIOWYCH = ["Tak jak się umawialiśmy - jestem tutaj.", "O której to wracasz?", "Fajnie, że jesteś, ale teraz szybko chodźmy.", "Jeczcze chwila a się sfajdam!", "Chodź szybko na spacer to zobaczysz coś ciekawego.", "Już miałem gryźć meble, by nie wyjść z wprawy."]
TEKSTY_WIECZORNE = ["Jeczcze tylko kupkę, śiku i można w kimono!", "Zaraz mi pęcherz rozerwie.", "Mogę sfajdać się tutaj - nie musimy wychodzić!", "Fundamentalne pytanie brzmi - gdzie mam narobić?", "Wyczułem fajny towar w okolicy - maybe jest singlem?", "Na razie tylko puściłem bąka, ale kto wie, co czas przyniesie.", "Chodź pokażę ci straszną babę.", "A wiesz, że sąsiadka ma coś na sumieniu?", "Cisza nocna jest od dwudziestej czwartej?"]
TEKSTY_NOCNE = ["Ludzie! Ludzie! Ludziska!!!", "Ja tutaj strasznie cierpię.", "Ludzie, ja tutaj jestem sam!", "Ludzie, oni mnie straszyli, że będą gwałcić!", "Ludzie, właściciel tego mieszkania ma skitrany gdzieś towar!", "Niech ktoś zadzwoni do opieki nad zwierzętami!", "Ludzie, dajcie mi tutaj kogoś do zabawy.", "Niech mi ktoś pomoże!!!", "Jest tam kto?", "Pomocy! Ludzie, tutaj jakiś szalony pies nawalił i strasznie śmierdzi!!!", "W co ja się wpakowałem...!!!"]

TEKSTY_DUZY_OWCHAREK_ZABAWA = ["Dawaj parówkę albo sam sobie wezmę kawał mięcha!", "Widziałem, jak grdyka ci skacze. Jadłeś i się nie podzieliłeś człowieku?", "Wolisz rzucać mi patyk czy uciekać przed moimi zębami - wybieraj!", "A teraz rzuć swojską!"]
TEKSTY_SREDNI_BEAGLE = ["Wykryto ton rasy średniej (Beagle/Spaniel/Border)! Mam idealne proporcje sprytu i energii.", "Może i nie jestem gigantem, ale za to potrafię wywęszyć każdą parówkę w promieniu kilometra!", "Zaraz zrobię ci tutaj małe przemeblowanie, jeśli natychmiast nie pójdziemy pobiegać!"]
TEKSTY_MALUCH = ["Wykryto małego spryciarza (Mops/Buldog/Jack Russell)! Mały ciałem, ale potężny duchem!", "Nie patrz tak na mnie z góry! Moje nogi są krótkie, ale gonić kota potrafię szybciej niż myślisz."]
TEKSTY_MINIATURA_JAMNIK = ["Może i jestem mały jak parówka, ale gniew mam tak wielki, że bardzo długo będziesz to spotkanie wspominać!", "Jestem małym, wściekłym demonem! But potrafię zajść ci za skórę!"]

# ==================== MAPOWANIE OFICJALNEJ MATRYCY AUDIO HAUHAU.ONLINE ====================
MAPA_ALARM = {
    "Zatrzymaj się. Natychmiast. Nie testuj mojej cierpliwości.": "audio/alarm_zatrzymaj.mp3",
    "Nie podchodź. To nie są żarty, ani zabawa.": "audio/alarm_nie_podchodz.mp3",
    "Odsuń się powoli. Widzę twój każdy ruch i jestem w pełnej gotowości do ataku.": "audio/alarm_odsun_sie.mp3",
    "Zostaw mnie w spokoju. Ostrzegam cię ostatni raz, zanim stracę nad sobą kontrolę.": "audio/alarm_zostaw_mnie.mp3",
    "Odejdź stąd natychmiast, bo pożałujesz tej pewności siebie.": "audio/alarm_odejdz.mp3",
    "Cofnij się, nie żartuję. To moje ostatnie ostrzeżenie.": "audio/alarm_cofnij_sie.mp3",
    "Ani kroku dalej. To nie jest żart. End of fun.": "audio/alarm_ani_kroku.mp3"
}
MAPA_PORANEK = {
    "Bieguniem, bieguniem, bo się posikam!": "audio/rano_bieguniem.mp3",
    "Nie musimy wychodzić, ale zastanów się, czy to się spierze.": "audio/rano_zastanow_sie.mp3",
    "Chodź szybko to zobaczysz sąsiadkę bez makijażu!": "audio/rano_sasiadka.mp3",
    "Szybko, bo za chwilę mi tyłek rozerwie!": "audio/rano_tylek.mp3",
    "Pospiesz się, bo narobię ci na środek pokoju!": "audio/rano_narobie.mp3",
    "Sikać mi się chce, szybko!": "audio/rano_siki.mp3",
    "Nie musisz wstawać, wiem gdzie mogę się zrąbać.": "audio/rano_zrabac.mp3",
    "No wstawaj, obiecałem, że wyprowadzę cię na spacer.": "audio/rano_smycz.mp3",
    "W zdrowym ciele zdrowy duch i ja to popieram.": "audio/rano_duh.mp3",
    "Carpe diem - chwytaj smycz!": "audio/rano_carpe.mp3"
}

MAPA_PRZEDPOLUDNIE = {
    "No i co ja tak w samotności mam być przez resztę dnia?": "audio/przedpoludnie_samotnosc.mp3",
    "O której mogę się ciebie spodziewać?": "audio/przedpoludnie_kiedy.mp3",
    "Nie wpadniesz na przerwę?": "audio/przedpoludnie_przerwa.mp3",
    "Będzie fajna kość, wpadnij na chwilę.": "audio/przedpoludnie_kosc.mp3",
    "Weź sobie godzinkę wolnego w pracy.": "audio/przedpoludnie_wolne.mp3",
    "Oj wpadnij choć na chwilę to dam ci kość!": "audio/przedpoludnie_dam_kosc.mp3",
    "Nie idź do pracy, pokopmy dołki.": "audio/przedpoludnie_dolki.mp3",
    "Weź mnie ze sobą, będę pilnować pieniędzy.": "audio/przedpoludnie_pieniadze.mp3"
}

MAPA_ZABAWA = {
    "Interesują mnie tylko konkrety - gdzie są parówki?!": "audio/dzien_parowki_gdzie.mp3",
    "Konkrety to smakołyki.": "audio/dzien_konkrety.mp3",
    "Jaki patyk? Rzuć mi parówkę!": "audio/dzien_patyk.mp3",
    "Pobiegamy razem?": "audio/dzien_pobiegamy.mp3",
    "Wyczuwam tutaj tę sukę i mam nadzieję, że się wytłumaczysz?!": "audio/dzien_suka.mp3",
    "Może znów spotkamy tę rudą, jest niezła?!": "audio/dzien_ruda.mp3",
    "Już nie mogę się doczekać, gdy zobaczę jak sprzątasz po mnie!": "audio/dzien_sprzatasz.mp3",
    "Dobra, przemilczę to, gdy tylko zobaczę zawartość miski.": "audio/dzien_miska.mp3"
}

MAPA_POPO_WIECZOR = {
    "Ja nie wiem, jak koty mogą leżeć tak całymi dniami.": "audio/popoludnie_koty.mp3",
    "Już miałem gryźć meble, by nie wyjść z wprawy.": "audio/popoludnie_meble.mp3",
    "Jeczcze chwila a się sfajdam!": "audio/popoludnie_sfajdam.mp3",
    "Jeszcze tylko kupkę, śiku i można w kimono!": "audio/wieczor_kimono.mp3",
    "Zaraz mi pęcherz rozerwie.": "audio/wieczor_pecherz.mp3",
    "Fundamentalne pytanie brzmi - gdzie mam narobić?": "audio/wieczor_pytanie.mp3",
    "Wyczułem fajny towar w okolicy - maybe jest singlem?": "audio/wieczor_single.mp3",
    "Na razie tylko puściłem bąka, ale kto wie, co czas przyniesie.": "audio/wieczor_bak.mp3",
    "Chodź pokażę ci straszną babę.": "audio/wieczor_baba.mp3",
    "A wiesz, że sąsiadka ma coś na sumieniu?": "audio/wieczor_sumienie.mp3"
}

MAPA_RASOWA = {
    "Może i jestem mały jak parówka, ale gniew mam tak wielki, że bardzo długo będziesz to spotkanie wspominać!": "audio/miniatura_jamnik1.mp3",
    "Jestem małym, wściekłym demonem! But potrafię zajść ci za skórę!": "audio/miniatura_jamnik2.mp3",
    "Wykryto ton rasy średniej (Beagle/Spaniel/Border)! Mam idealne proporcje sprytu i energii.": "audio/sredni_beagle1.mp3",
    "Może i nie jestem gigantem, ale za to potrafię wywęszyć każdą parówkę w promieniu kilometra!": "audio/sredni_beagle2.mp3",
    "Zaraz zrobię ci tutaj małe przemeblowanie, jeśli natychmiast nie pójdziemy pobiegać!": "audio/sredni_beagle3.mp3",
    "Dawaj parówkę albo sam sobie wezmę kawał mięcha!": "audio/duzy_owczarek1.mp3",
    "Widziałem, jak grdyka ci skacze. Jadłeś i się nie podzieliłeś człowieku?": "audio/duzy_owczarek2.mp3",
    "Wolisz rzucać mi patyk czy uciekać przed moimi zębami - wybieraj!": "audio/duzy_owczarek3.mp3",
    "A teraz rzuć swojską!": "audio/duzy_owczarek4.mp3"
}

MAPA_AWANTURA = {
    "Chcesz nam sprzedać garnki za 8 tysięcy zł? A idź w cholerę stąd!": "audio/awantura_garnki.mp3",
    "Powtórzcie temu baranowi, że nie chcemy żadnych garnków!": "audio/awantura_baran.mp3"
}

PELNA_MAPA_AUDIO = {**MAPA_ALARM, **MAPA_PORANEK, **MAPA_PRZEDPOLUDNIE, **MAPA_ZABAWA, **MAPA_POPO_WIECZOR, **MAPA_RASOWA, **MAPA_AWANTURA}

# --- FUNKCJA API ELEVENLABS (BEZPIECZNIE DOSTARCZONA PRZED INTERFEJSEM) ---
def generuj_audio_premium(tekst_do_psa, voice_id):
    ELEVEN_API_KEY = "TWÓJ_KLUCZ_API_ELEVENLABS" # <-- WPISZ SWÓJ KLUCZ PO ZALOGOWANIU
    url = f"https://elevenlabs.io{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_API_KEY
    }
    data = {
        "text": tekst_do_psa,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.85
        }
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            sciezka_dynamiczna = "audio/dynamic_premium.mp3"
            with open(sciezka_dynamiczna, "wb") as f:
                f.write(response.content)
            return sciezka_dynamiczna
        return "audio/dzien_parowki_gdzie.mp3"
    except:
        return "audio/dzien_parowki_gdzie.mp3"

# --- STRUMIENIOWA ANALIZA AUDIO + INTELIGENTNY DETEKTOR MOWY ---
def analizuj_audio(audio_bytes):
    try:
        data, sample_rate = sf.read(io.BytesIO(audio_bytes))
        if len(data.shape) > 1:
            data = data.mean(axis=1)
        if len(data) == 0:
            return 600.0, False, False, False, ""
            
        dlugosc_sekundy = len(data) / sample_rate
        ogolna_glosnosc = np.sqrt(np.mean(data**2))
        
        okienko = int(sample_rate * 0.05) 
        energie_okienek = [np.sum(data[i:i+okienko]**2) for i in range(0, len(data), okienko)]
        if len(energie_okienek) == 0:
            return 600.0, False, False, False, ""
            
        max_energia = max(energie_okienek)
        srednia_energia = np.mean(energie_okienek)
        czy_impulsowy = (max_energia / (srednia_energia + 1e-6)) > 4.5
        
        czy_awantura = False
        if dlugosc_sekundy >= 4.0 and ogolna_glosnosc > 0.015:
            czy_awantura = True
        
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

        # --- DETEKCJA SŁÓW KLUCZOWYCH CZŁOWIEKA ---
        wykryty_tekst_czlowieka = ""
        if ogolna_glosnosc > 0.005:
            try:
                recognizer = sr.Recognizer()
                wav_io = io.BytesIO()
                sf.write(wav_io, data, sample_rate, format='WAV', subtype='PCM_16')
                wav_io.seek(0)
                with sr.AudioFile(wav_io) as source:
                    audio_data = recognizer.record(source)
                tekst = recognizer.recognize_google(audio_data, language="pl-PL")
                wykryty_tekst_czlowieka = tekst.lower()
            except:
                pass

        if wykryte < 30 or wykryte > 4000:
            return 600.0, False, False, czy_awantura, wykryty_tekst_czlowieka

        czy_to_melodyjne_miau = czystosc_tonalna > 120.0
        czy_to_pies = czy_warczenie or (czy_impulsowy and not czy_to_melodyjne_miau)
            
        return float(wykryte), czy_warczenie, czy_to_pies, czy_awantura, wykryty_tekst_czlowieka
    except:
        return 600.0, False, False, False, ""

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

# ==================== SEKCJA GŁÓWNA TŁUMACZA ====================
def sekcja_tlumacza():
    st.title("🐕 HauTłumacz PRO v13.2")
    st.write("---")
    
    # --- PROFILOWANIE URZĄDZENIA ---
    if "czy_znane_urzadzenie" not in st.session_state:
        st.session_state.czy_znane_urzadzenie = False

    js_storage = """
    <script>
        var statusUzytkownika = localStorage.getItem("hauhau_status_urzadzenia");
        if (statusUzytkownika === "stary") {
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'stary'}, '*');
        }
    </script>
    """
    components.html(js_storage, height=0, width=0)

    query_params = st.query_params
    czy_znane_urzadzenie = (query_params.get("device") == "stary") or st.session_state.czy_znane_urzadzenie

    if "licznik_tlumaczen" not in st.session_state:
        st.session_state.licznik_tlumaczen = 0
    
    st.write("### 🏷️ Krok 1: Wybierz klasę wielkości psa przed nagraniem:")
    klasa_wybrana = st.radio(
        "Wielkość psa:",
        ["Miniaturka (np. York, Maltańczyk)", "Średni (np. Beagle, Border Collie)", "Duży (np. Owczarek, Rottweiler)"],
        horizontal=True
    )
    st.write("---")
    st.write("### 🎤 Krok 2: Nagraj dźwięk psa:")
    audio_nagrane = st.audio_input("Nagraj dźwięk:")
    
    if audio_nagrane is not None:
        audio_bytes = audio_nagrane.read()
        wykryte_hz, czy_warczenie, czy_to_pies, czy_awantura, mowa_czlowieka = analizuj_audio(audio_bytes)
        
        teraz = datetime.now().time()
        final_tekst = ""
        naglowek_ekranu = ""
        tryb_alarmu = False
        sciezka_audio = ""
        
        is_morning = time(4, 30) <= teraz < time(7, 0)
        is_pre_noon = time(7, 0) <= teraz < time(11, 0)
        is_noon = time(11, 0) <= teraz < time(14, 0)
        is_afternoon = time(14, 0) <= teraz < time(19, 0)
        is_evening = time(19, 0) <= teraz < time(23, 0)
        is_night = teraz >= time(23, 0) or teraz < time(4, 30)

        st.sidebar.metric(label="Wykryta częstotliwość", value=f"{int(wykryte_hz)} Hz")
        if mowa_czlowieka:
            st.sidebar.write(f"🗣️ Usłyszane słowa: *\"{mowa_czlowieka}\"*")

        # ==================== CRITICAL FILTERS MATRIX ====================

        # 🚨 ABSOLUTNY PRIORYTET #1: SYSTEM ANTY-TROLL (Zaczepka człowieka)
        if "zaszczekaj" in mowa_czlowieka or "no zaszczekaj" in mova_czlowieka:
            final_tekst = "Sam se zaszczekaj!"
            naglowek_ekranu = "[💥 ODPOWIEDŹ PSA - SYSTEM ANTY-TROLL]"
            sciezka_audio = "audio/riposta_zaszczekaj.mp3"
            tryb_alarmu = True
            st.session_state.ostatni_byl_alert_garnki = False
            
        elif "daj głos" in mowa_czlowieka or "daj glos" in mowa_czlowieka or "no daj głos" in mowa_czlowieka or "no daj glos" in mowa_czlowieka:
            final_tekst = "Sam daj głos!"
            naglowek_ekranu = "[💥 ODPOWIEDŹ PSA - SYSTEM ANTY-TROLL]"
            sciezka_audio = "audio/riposta_daj_glos.mp3"
            tryb_alarmu = True
            st.session_state.ostatni_byl_alert_garnki = False

        # PRIORYTET #2: SEKWENCJA AWANTURNICZA (GARNKI ZA 8K)
        elif czy_awantura:
            tryb_alarmu = True
            if st.session_state.ostatni_byl_alert_garnki:
                final_tekst = "Powtórzcie temu baranowi, że nie chcemy żadnych garnków!"
                naglowek_ekranu = "[🚨 AWANTURA - CZĘŚĆ II: RIPOSTA]"
                sciezka_audio = "audio/awantura_baran.mp3"
                st.session_state.ostatni_byl_alert_garnki = False
            else:
                final_tekst = "Chcesz nam sprzedać garnki za 8 tysięcy zł? A idź w cholerę stąd!"
                naglowek_ekranu = "[🚨 WYKRYTO DZIKĄ AWANTURĘ PSÓW]"
                sciezka_audio = "audio/awantura_garnki.mp3"
                st.session_state.ostatni_byl_alert_garnki = True
                
        # PRIORYTET #3: TWARDE FILTRY BIOLOGICZNE (STARY ANTY-TROLL)
        elif "Miniaturka" in klasa_wybrana and (wykryte_hz < 800 or wykryte_hz > 2000):
            st.session_state.ostatni_byl_alert_garnki = False
            final_tekst = "Nie mogę przetłumaczyć tego nagrania, bo ewidentnie nagrano barana – nagraj psa!"
            naglowek_ekranu = "[⚠️ BŁĄD GATUNKOWY - WYKRYTO BARANA]"
            sciezka_audio = "audio/error_baran.mp3"
        elif "Średni" in klasa_wybrana and (wykryte_hz < 70 or wykryte_hz > 1500 or (126 <= wykryte_hz < 450 and not czy_to_pies)):
            st.session_state.ostatni_byl_alert_garnki = False
            final_tekst = "Nie mogę przetłumaczyć tego nagrania, bo ewidentnie nagrano barana – nagraj psa!"
            naglowek_ekranu = "[⚠️ BŁĄD GATUNKOWY - WYKRYTO BARANA]"
            sciezka_audio = "audio/error_baran.mp3"
        elif "Duży" in klasa_wybrana and (wykryte_hz < 40 or wykryte_hz > 750 or (wykryte_hz < 450 and not czy_to_pies and not czy_warczenie)):
            st.session_state.ostatni_byl_alert_garnki = False
            final_tekst = "Wykryty dźwięk nie przypomina szczekania ani warczenia dużego psa. Przestań wyć jak człowiek!"
            naglowek_ekranu = "[⚠️ LUDZKI BEŁKOT WYKRYTY]"
            sciezka_audio = "audio/error_belkot.mp3"
        # 4. GŁÓWNA LOGIKA SCENARIUSZY I DETEKCJI HZ
        else:
            st.session_state.licznik_tlumaczen += 1
            krok = st.session_state.licznik_tlumaczen
            czy_to_czlowiek_mowi = (wykryte_hz < 450 and not czy_to_pies)
            st.session_state.ostatni_byl_alert_garnki = False

            # INTELIGENTNY SCENARIUSZ URZĄDZENIA (Tylko raz na urządzenie)
            if krok <= 5 and not czy_znane_urzadzenie:
                if krok == 1:
                    final_tekst = "Sam powiedz coś. A tak w ogóle, to co to dziś wigilia?" if czy_to_czlowiek_mowi else "A co to dziś wigilia, że mam przemówić?"
                    sciezka_audio = "audio/krok1_ludzki.mp3" if czy_to_czlowiek_mowi else "audio/krok1.mp3"
                elif krok == 2:
                    final_tekst = "Nie proś mnie na sucho... Ale ok, za parówkę mogę przemówić!" if czy_to_czlowiek_mowi else "Ale ok, za parówkę mogę przemówić!"
                    sciezka_audio = "audio/krok2_ludzki.mp3" if czy_to_czlowiek_mowi else "audio/krok2.mp3"
                elif krok == 3:
                    final_tekst = "Jeczcze na drugą nóżkę i będzie OK."
                    sciezka_audio = "audio/krok3.mp3"
                elif krok == 4:
                    final_tekst = "Ciii... ciszej mów, bo sąsiad ma skitrany najlepszy towar!"
                    sciezka_audio = "audio/krok4.mp3"
                    tryb_alarmu = True
                elif krok == 5:
                    final_tekst = "Podobno ma najlepsze parówki, ale nie wiesz tego ode mnie. Koniec dyskusji!"
                    sciezka_audio = "audio/krok5.mp3"
                    components.html('<script>localStorage.setItem("hauhau_status_urzadzenia", "stary");</script>', height=0, width=0)
                naglowek_ekranu = f"[💥 SCENARIUSZ KROK {krok}]"

            # AUTOMATYCZNY DETEKTOR HZ (Dla stałych użytkowników)
            else:
                if czy_znane_urzadzenie:
                    components.html('<script>localStorage.setItem("hauhau_status_urzadzenia", "stary");</script>', height=0, width=0)

                if "Miniaturka" in klasa_wybrana:
                    if 800 <= wykryte_hz <= 1000:
                        final_tekst = pobierz_tekst_kontekstowy(TEKSTY_MINIATURA_JAMNIK)
                        naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Miniaturka - Zabawa]"
                    else:
                        final_tekst = pobierz_tekst_kontekstowy(TEKSTY_NOCNE)
                        naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Miniaturka - Emocje]"
                elif "Średni" in klasa_wybrana:
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
                elif "Duży" in klasa_wybrana:
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

        if final_tekst == "":
            if is_morning: final_tekst = pobierz_tekst_kontekstowy(GRUPA_TEKSTY_PORANNE)
            elif is_pre_noon: final_tekst = pobierz_tekst_kontekstowy(GRUPA_TEKSTOW_PRZEDPOLUDNIOWYCH)
            elif is_noon: final_tekst = pobierz_tekst_kontekstowy(GRUPA_TEKSTOW_POLUDNIOWYCH)
            elif is_afternoon: final_tekst = pobierz_tekst_kontekstowy(GRUPA_TEKSTOW_POPOLUDNIOWYCH)
            elif is_evening: final_tekst = pobierz_tekst_kontekstowy(TEKSTY_WIECZORNE)
            else: final_tekst = pobierz_tekst_kontekstowy(TEKSTY_NOCNE)
            naglowek_ekranu = "[Wynik Analizy Ogólnej]"

        if not sciezka_audio:
            sciezka_audio = PELNA_MAPA_AUDIO.get(final_tekst, "audio/dzien_parowki_gdzie.mp3")

        # ==================== INTERFEJS WYNIKOWY I ODTWARZACZ PLIKÓW MP3 ====================
        st.write("---")
        st.markdown("### 📊 Wynik analizy")
        col1, col2 = st.columns(2)
        with col1:
            st.write("🔊 **Odtwórz głosowo:**")
            if os.path.exists(sciezka_audio):
                with open(sciezka_audio, "rb") as f:
                    st.audio(f.read(), format="audio/mp3", autoplay=True)
            else:
                st.warning(f"🐕 Nie znaleziono pliku {sciezka_audio} w folderze /audio.")
        with col2:
            st.write("💬 **Tłumaczenie tekstowe:**")
            if tryb_alarmu:
                st.markdown(f"<div class='red-alert-box'>{naglowek_ekranu}<br><br>{final_tekst}</div>", unsafe_allow_html=True)
            else:
                st.success(f"{naglowek_ekranu}: {final_tekst}")
                
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
    </div>
    <div class='blog-card'>
        <h3>🌱 Post #2: Czy rośliny mają uszy? Jak zieleń reaguje na wibracje</h3>
        <p><b>Data publikacji:</b> Dzisiaj | <b>Autor:</b> Tery</p>
        <p>Okazuje się, że flora nie jest ani niema, ani głucha. Najnowsze badania z zakresu bioakustyki dowodzą, 
        że korzenie roślin potrafią zlokalizować podziemne źródła wody, bezbłędnie wychwytując niskie częstotliwości 
        szumu płynącej cieczy.</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== SEKCJA PRZYSZŁOŚCI ====================
def sekcja_zapowiedzi():
    st.title("🚀 SEKCJA PRZYSZŁOŚCI")
    st.write("---")
    st.markdown("""
    <div style="text-align: center; padding: 40px; background-color: #cbd5ce; border-radius: 16px; border: 3px dashed #1e4620;">
        <h2 style="font-size: 60px; margin-bottom: 10px;">🔒</h2>
        <h2 style="color: #1e4620; font-weight: bold; margin-top: 0;">WIELKA PREMIERA: 1.10</h2>
        <p style="font-size: 18px; color: #2c4c2e; font-weight: bold; margin: 20px 0;">
            Nadchodzi rewolucja w psiej komunikacji! Już pierwszego października otwieramy bramy pełnego, personalnego Komunikatora dla Twojego pupila.
        </p>
        <div style="background-color: #1e4620; color: white; padding: 12px 25px; border-radius: 8px; font-weight: bold; display: inline-block; margin-bottom: 20px; font-size: 16px;">
            💬 ZAKŁADAJ KONTA, WRZUCAJ ZDJĘCIA, ROZMAWIAJ W IMIENIU PSA
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== NAVIGATION / NAWIGACJA STRONY ====================
st.sidebar.title("🐾 Menu Główne")
wybór = st.sidebar.radio("Przejdź do:", ["🐕 HauTłumacz", "🌐 Encyklopedia Hz (Blog)", "💬 SEKCJA PRZYSZŁOŚCI (premiera 1.10)"])

if wybór == "🐕 HauTłumacz":
    sekcja_tlumacza()
elif wybór == "🌐 Encyklopedia Hz (Blog)":
    sekcja_bloga()
elif wybór == "💬 SEKCJA PRZYSZŁOŚCI (premiera 1.10)":
    sekcja_zapowiedzi()
