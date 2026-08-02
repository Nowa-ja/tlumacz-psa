import streamlit as st
import io
import random
from datetime import datetime, time
from scipy.io import wavfile
import numpy as np
from gtts import gTTS

# --- BEZPIECZNA KONFIGURACJA STRONY ---
st.set_page_config(page_title="HauTłumacz PRO v11.0", page_icon="🐕", layout="centered")

# --- FUNKCJA INTEGRUJĄCA BLOG I STRONĘ GŁÓWNĄ ---
def sekcja_tlumacza():
    """Tutaj znajduje się cała logika Twojego dotychczasowego tłumacza"""
    # --- INICJALIZACJA PAMIĘCI SYSTEMU ---
    if "ostatni_tekst" not in st.session_state:
        st.session_state.ostatni_tekst = ""
    if "wykorzystane_teksty" not in st.session_state:
        st.session_state.wykorzystane_teksty = set()

    # --- STABILNA ANALIZA HZ ORAZ DETEKCJA WARCZENIA ---
    def analizuj_audio(audio_bytes):
        try:
            sample_rate, data = wavfile.read(io.BytesIO(audio_bytes))
            if len(data.shape) > 1:
                data = data.mean(axis=1)
            if len(data) == 0:
                return 600.0, False
                
            fft_spectrum = np.fft.rfft(data)
            freq = np.fft.rfftfreq(len(data), d=1.0/sample_rate)
            
            szczytowa_indeks = np.argmax(np.abs(fft_spectrum))
            wykryte = freq[szczytowa_indeks]
            
            czy_warczenie = False
            calkowita_energia = np.sum(np.abs(fft_spectrum))
            
            if calkowita_energia > 0:
                niskie_pasmo = (freq >= 60) & (freq <= 140)
                energia_basu = np.sum(np.abs(fft_spectrum[niskie_pasmo]))
                ostre_pasmo = (freq >= 450) & (freq <= 950)
                energia_ostra = np.sum(np.abs(fft_spectrum[ostre_pasmo]))
                
                if 60 <= wykryte <= 140 and (energia_basu / calkowita_energia) > 0.35:
                    czy_warczenie = True
                elif 450 <= wykryte <= 950 and (energia_ostra / calkowita_energia) > 0.30:
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
        "Wyczułem fajny towar w okolicy - maybe jest singlem?",
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

    TEKSTY_DUZY_OWCHAREK_ZABAWA = [
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

       # --- STYLE CSS (ZMODYFIKOWANE ŁAGODNE TŁO DLA OCZU) ---
    st.markdown("""
        <style>
        /* Główne tło strony - stonowany, ciemniejszy pastelowy szary/zielony */
        .stApp, [data-testid="stAppViewContainer"] { 
            background-color: #e2e8e4 !important; 
        }
        
        /* Tło bocznego panelu (Menu) - dopasowane i ciemniejsze */
        [data-testid="stSidebar"] { 
            background-color: #cbd5ce !important; 
        }
        
        h1 { color: #1e4620 !important; text-align: center; margin-top: 10px; }
        .stAudioInput { border: 2px dashed #81c784 !important; border-radius: 12px; padding: 10px; background-color: #f1f5f2; }
        
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
        
        /* Jasne, kontrastowe karty wpisów - tekst będzie idealnie widoczny */
        .blog-card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            border-left: 5px solid #1e4620;
            color: #111111 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🐕 HauTłumacz PRO v11.0")
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
        if wykryte_hz <= 300:
            final_tekst = "Ostrzeżenie"
            naglowek_ekranu = "[🚨 ALERT NISKIEJ CZĘSTOTLIWOŚCI]"
            tryb_alarmu = True
        elif czy_warczenie:
            final_tekst = pobierz_tekst_kontekstowy(TEKSTY_WARCZENIE_ALARM)
            naglowek_ekranu = "[🚨 KRTYTYCZNE OSTRZEŻENIE - EMOCJA: AGRESJA/STRACH]"
            tryb_alarmu = True
        elif 301 <= wykryte_hz <= 450:
            if wykryte_hz < 360:
                zwierze = FONETYCZNY_BARAN
                komentarz = "Ewidętnie nagrano barana! Nagraj psa a nie barana!"
                naglowek_ekranu = "[Wykryto Samca - Tryb Barana]"
            else:
                zwierze = FONETYCHNA_KROWA
                komentarz = "Wykryto dźwięki z zagrody! Posłuchaj koleżanki z łąki, przestań wyć i daj psu dojść do głosu!"
                naglowek_ekranu = "[Wykryto Samicę - Tryb Krowy]"
            final_tekst = f"{zwierze} Nie mogę przetłumaczyć tego dźwięku, bo zamiast psa wyraźnie słyszę człowieka! {komentarz}"
        elif wykryte_hz > 3000:
            final_tekst = "Słyszę tylko szum tła, odgłosy ulicy lub samochód. Poczekaj na ciszę i pozwól zaszczekać psu!"
            naglowek_ekranu = "[⚠️ Zakłócenia Otoczenia]"
        else:
            if 450 < wykryte_hz < 550 and not (is_morning or is_evening or is_night):
                final_tekst = pobierz_tekst_kontekstowy(TEKSTY_DUZY_OWCHAREK_ZABAWA)
                naglowek_ekranu = f"[{int(wykryte_hz)} Hz - Duży Owczarek]"
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

    # ==================== GENERATOR LEKTORA ====================
        tekst_do_czytania = final_tekst.replace(".", ",").replace("!", ",")
        tts = gTTS(text=tekst_do_czytania, lang='pl', slow=False)
        fp_raw = io.BytesIO()
        tts.write_to_fp(fp_raw)
        fp_raw.seek(0)
        
        try:
            sample_rate, data = wavfile.read(fp_raw)
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
                st.markdown(f"<div class='red-alert-box'>{naglowek_ekranu}<br><br>{final_tekst}</div>", unsafe_allow_html=True)
            else:
                st.success(f"{naglowek_ekranu}: {final_tekst}")

    # ==================== STOPKA Z PEŁNYM REGULAMINEM ====================
    st.write("---")
    if st.button("📝 Regulamin strony"):
        st.info("""
        **Regulamin i informacje o serwisie hauhau.online**
        
        Drogi użytkowniku. Jest mi bardzo miło gościć Ciebie na stronie „hauhau.online”...
        (Tutaj znajduje się reszta Twojego tekstu regulaminu, który nie uległ zmianie).
        """)

# ==================== NOWA SEKCJA: ENCYKLOPEDIA HZ (BLOG) ====================
def sekcja_bloga():
    """Tutaj tworzysz swoje posty o fascynującym świecie częstotliwości"""
    st.title("🌐 Encyklopedia Częstotliwości Hz")
    st.write("Odkryj niewidzialny i niesłyszalny świat wibracji, który rządzi życiem na Ziemi.")
    st.write("---")
    
    # POST 1
    st.markdown("""
    <div class='blog-card'>
        <h3>🔊 Post #1: Tajemny język natury – Czym są częstotliwości Hz?</h3>
        <p><b>Data publikacji:</b> Dzisiaj | <b>Autor:</b> Tery</p>
        <p>Częstotliwości Hz: te znane, te pomijane i te, o których prawie nie myślimy. 
Witaj na stronie poświęconej naszym czworonożnym przyjacielom. Na tej stronie będziesz mógł jak kazdy zainteresowany komunikacją ze zwierzątami dowiedzieć się wielu szczegółów, którego pomogą Ci komunikować się w szczególności z Psami, ale nie tylko. Kiedy słyszymy słowo „częstotliwość”, wielu osobom od razu przychodzą do głowy muzyka, radio albo tajemniczo brzmiące liczby zapisane w hercach, czyli w Hz. To właśnie herc jest jednostką częstotliwości i oznacza liczbę powtórzeń zjawiska w ciągu jednej sekundy. 1 Hz to jedno drganie na sekundę, 10 Hz to dziesięć drgań na sekundę, a 100 Hz to już sto drgań w tym samym czasie. Brzmi prosto, ale za tą prostotą kryje się ogromny świat zjawisk, które wpływają na nasze codzienne życie bardziej, niż zwykle zauważamy. Najbardziej znane częstotliwości to te związane z dźwiękiem. Ucho człowieka, w przybliżeniu, słyszy dźwięki od około 40 Hz do 20 000 Hz, choć granice te zależą od wieku i kondycji słuchu. Niskie częstotliwości odbieramy jako basy, wysokie jako tony ostre i przenikliwe. Gdy słyszymy dudnienie subwoofera, mamy do czynienia z dolnym zakresem słyszalności. Gdy słyszymy śpiew ptaków albo wysoki dźwięk fletu, mówimy raczej o częstotliwościach wyższych. To właśnie w muzyce herce są szczególnie „namacalne”. Struna gitary, membrana głośnika, głos człowieka — wszystko to drga. Im szybsze drgania, tym wyższy słyszany dźwięk. Częstotliwość pozwala więc opisać coś, co wydaje się ulotne i emocjonalne, w ścisły, fizyczny sposób. Z jednej strony mamy sztukę, z drugiej precyzję pomiaru. To bardzo ciekawe spotkanie świata humanistycznego i naukowego. Znane są też częstotliwości związane z siecią elektryczną. W Polsce i w większości Europy prąd przemienny ma częstotliwość 50 Hz. To oznacza, że kierunek zmian napięcia i prądu powtarza się 50 razy na sekundę. Dla większości ludzi jest to informacja techniczna, ale w praktyce wpływa ona na działanie wielu urządzeń. Dawniej miała też znaczenie choćby przy pracy zegarów elektrycznych czy niektórych silników. Częstotliwość 50 Hz jest więc czymś powszechnym, choć na co dzień niemal niewidzialnym. Innym dobrze znanym obszarem są fale radiowe. Kiedy ustawiamy stację radiową, widzimy liczby wyrażone zwykle w megahercach, na przykład 100 MHz. To nadal częstotliwość, tylko znacznie większa. W tym przypadku nie chodzi jednak o dźwięk, lecz o drgania pola elektromagnetycznego. Dzięki nim możliwa jest transmisja informacji: radia, telewizji, komunikacji bezprzewodowej. Współczesny świat dosłownie zanurzony jest w częstotliwościach, których nie słyszymy ani nie widzimy, ale z których stale korzystamy. I tu zaczyna się sfera częstotliwości „nieznanych”, a przynajmniej mniej uświadamianych. Jednym z takich zakresów są infradźwięki, czyli częstotliwości poniżej 20 Hz. Człowiek zazwyczaj ich nie słyszy, ale może je odczuwać. Mogą być związane z burzami, trzęsieniami ziemi, silnym wiatrem, pracą dużych maszyn czy ruchem fal morskich. Czasem mówi się o nich w kontekście niepokoju albo dziwnego uczucia dyskomfortu, choć nie zawsze łatwo to jednoznacznie udowodnić w każdej sytuacji. To interesujący przykład zjawiska fizycznego, które działa na człowieka nawet wtedy, gdy nie dociera do niego jako zwykły dźwięk. Z drugiej strony mamy ultradźwięki, czyli częstotliwości powyżej granicy ludzkiego słuchu. Nie słyszymy ich, ale są powszechnie wykorzystywane. Medycyna stosuje ultradźwięki w badaniach obrazowych, technika używa ich do czyszczenia precyzyjnych elementów, a przyroda zna je od dawna — korzystają z nich między innymi nietoperze i delfiny. Dla nich wysokie częstotliwości są narzędziem orientacji w przestrzeni. Dla człowieka stały się narzędziem nauki i diagnostyki. Warto też pamiętać, że częstotliwość nie dotyczy wyłącznie dźwięku czy fal radiowych. Każdy ruch okresowy można opisać w hercach. Wahadło, drgająca sprężyna, pulsujące układy elektroniczne, miganie sygnału, a nawet rytm pracy serca — wszystko to można analizować przez pryzmat częstotliwości. W tym sensie Hz to nie tylko jednostka fizyczna, lecz także sposób patrzenia na świat: przez regularność, powtarzalność i rytm. Są również częstotliwości, które funkcjonują w przestrzeni popularnej niemal jak symbole. Czasem można spotkać się z twierdzeniami, że konkretne wartości Hz mają szczególne działanie na psychikę, ciało albo emocje. W internecie krąży wiele uproszczeń i pseudonaukowych teorii przypisujących poszczególnym liczbom niemal magiczne właściwości. Trzeba tu zachować ostrożność. Sama częstotliwość jest wielkością fizyczną, ale jej znaczenie zależy od kontekstu: amplitudy, rodzaju fali, środowiska, czasu działania i sposobu odbioru. Bez tych informacji liczba sama w sobie niewiele mówi. Fizyka uczy właśnie tego, by nie zatrzymywać się na efektownym haśle, lecz pytać o mechanizm. To szczególnie ważne dziś, gdy wiele pojęć naukowych trafia do obiegu medialnego w uproszczonej formie. „Wibracje”, „rezonans”, „częstotliwości” brzmią atrakcyjnie, ale łatwo użyć ich nieprecyzyjnie. Tymczasem prawdziwe znaczenie częstotliwości jest i tak fascynujące. To dzięki niej rozumiemy muzykę, łączność bezprzewodową, diagnostykę medyczną, działanie urządzeń elektrycznych i wiele procesów przyrodniczych. Nie trzeba dodawać do tego tajemnicy na siłę — sama nauka jest wystarczająco niezwykła. Można powiedzieć, że żyjemy w świecie częstotliwości znanych i nieznanych. Znanych, bo słyszalnych, mierzalnych i obecnych w technice. Nieznanych, bo ukrytych poza zasięgiem naszych zmysłów albo po prostu niedostrzeganych w codziennym pośpiechu. Hertz nie jest tylko jednostką z podręcznika fizyki. To klucz do zrozumienia rytmu świata — od drgania struny, przez fale radiowe, aż po zjawiska, których nigdy nie usłyszymy, a które mimo to nieustannie nam towarzyszą.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # POST 2
    st.markdown("""
    <div class='blog-card'>
        <h3>🌱 Post #2: Psy i częstotliwości – świat, którego człowiek nie słyszy tak jak one </h3>
        <p><b>Data publikacji:</b> Dzisiaj | <b>Autor:</b> Tery</p>
        <p> Psy od tysięcy lat żyją obok człowieka, ale ich sposób odbierania świata wciąż potrafi zaskakiwać. Jednym z najciekawszych elementów tej relacji są częstotliwości — czyli dźwięki o różnej wysokości, które psy potrafią słyszeć znacznie lepiej niż ludzie. To właśnie dzięki nim psy reagują na wiele sygnałów, których człowiek często nawet nie zauważa.
Słuch psa jest wyjątkowo czuły, zwłaszcza w zakresie wysokich częstotliwości. Podczas gdy człowiek słyszy mniej więcej do 20 000 Hz, psy mogą odbierać dźwięki znacznie wyższe. Oznacza to, że wychwytują delikatne szmery, piski, odgłosy urządzeń elektronicznych, a także specjalne gwizdki treningowe, które dla nas bywają ledwo słyszalne albo wręcz niesłyszalne. Dla psa taki sygnał może być jasną informacją: przyjdź, zostań, wróć, zwróć uwagę.
Ale częstotliwości to nie tylko słyszenie. To także komunikacja. Psy same używają różnych dźwięków, aby przekazać emocje i intencje. Niskie warczenie może oznaczać ostrzeżenie lub dyskomfort, szczekanie może być sygnałem alarmowym, ekscytacją albo próbą zwrócenia uwagi, a skomlenie czy wycie często wiąże się z samotnością, stresem lub potrzebą kontaktu. Każdy z tych dźwięków ma swoje miejsce w świecie psiej komunikacji.
Warto też pamiętać, że psy nie odbierają dźwięku tylko uszami. Całym ciałem reagują na rytm, natężenie i częstotliwość otoczenia. Zmiana tonu głosu opiekuna, nagły wysoki dźwięk, stukot, brzęczenie czy nawet sposób, w jaki coś wibruje w przestrzeni, może wpłynąć na ich zachowanie. Psy są mistrzami odczytywania sygnałów, które dla człowieka są często zbyt subtelne.
To właśnie dlatego relacja człowieka z psem jest tak wyjątkowa. Uczymy się od nich wrażliwości na to, czego nie widać od razu. Częstotliwości stają się tu czymś więcej niż terminem z fizyki — są językiem porozumienia, bezpieczeństwa i zaufania. Dzięki nim możemy lepiej zrozumieć, jak pies odbiera nasz głos, emocje i otoczenie.
Na naszej stronie będziemy pokazywać, jak te zjawiska działają w praktyce: jakie częstotliwości są ważne dla psów, jak je wykorzystują, jak można je obserwować i jak dzięki tej wiedzy budować lepszą więź ze swoim czworonogiem. Bo kiedy zaczynamy słuchać świata tak, jak słucha go pies, odkrywamy zupełnie nowy poziom komunikacji.</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== AKTUALNA NAWIGACJA STRONY (PASEK BOCZNY) ====================
st.sidebar.title("🐾 Menu Główne")
wybór = st.sidebar.radio("Przejdź do:", ["🐕 HauTłumacz", "🌐 Encyklopedia Hz (Blog)"])

# Uruchamianie odpowiedniej zakładki pod tym samym adresem hauhau.online
if wybór == "🐕 HauTłumacz":
    sekcja_tlumacza()
elif wybór == "🌐 Encyklopedia Hz (Blog)":
    sekcja_bloga()
