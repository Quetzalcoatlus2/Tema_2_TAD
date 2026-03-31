from datetime import datetime, timezone  # Importă tipurile folosite la timestamp UTC.
import json  # Modul standard pentru serializare/deserializare JSON.
import unicodedata  # Utilitar pentru normalizare text (diacritice).
from urllib.error import HTTPError, URLError  # Excepții de rețea pentru apelurile HTTP externe.
from urllib.parse import urlencode  # Convertește dicționare în query string URL.
from urllib.request import Request, urlopen  # Construiește și execută request-uri HTTP simple.

from flask import Flask, jsonify, make_response, render_template, request  # Importă primitivele Flask folosite în endpoint-uri.

# Instanța Flask care înregistrează toate rutele HTTP.
app = Flask(__name__)  # Creează aplicația Flask (punctul central al rutei API/UI).

# "Baza de date" în memorie:
# - cheia = id numeric
# - valoarea = obiectul măsurării validate.
baza_masuratori = {}  # Dict in-memory: cheia este id-ul, valoarea este obiectul măsurării.
urmatorul_id = 1  # Contor incremental pentru generarea id-urilor noi.

# Endpointuri externe și constante de configurare.
NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"  # Endpoint de geocodare (oraș -> coordonate).
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"  # Endpoint meteo curent pe coordonate.
USER_AGENT_EXTERNE = "Tema2-TAD-Masuratori/1.0 (educational project)"  # User-Agent explicit pentru upstream APIs.
METODE_HTTP = ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE"]  # Metode suportate în API.
METODE_COLECTIE = METODE_HTTP  # Alias pentru metodele permise pe colecție.
METODE_ELEMENT = METODE_HTTP  # Alias pentru metodele permise pe element.
CORS_ALLOW_HEADERS = "Content-Type, Authorization, Accept"  # Lista antetelor acceptate în preflight CORS.

# Aliasuri pentru câmpurile text opționale acceptate în payload.
CAMPURI_TEXT_OPTIONALE = {
    "location": ["location", "locatie", "pozitie_instalare"],
    "description": ["description", "descriere", "detalii"],
    "category": ["category", "categorie", "domeniu"],
    "sensor_name": ["sensor_name", "nume_senzor"],
    "sensor_model": ["sensor_model", "model_senzor"],
    "sensor_manufacturer": ["sensor_manufacturer", "producator_senzor"],
    "operator_name": ["operator_name", "responsabil", "persoana_responsabila"],
    "city": ["city", "oras"],
    "county": ["county", "judet"],
    "source_system": ["source_system", "sursa_date", "platforma_sursa"],
}

# Maparea statică a metricilor importate din Open-Meteo.
MAPARE_METRICI_OPEN_METEO = [
    {
        "cheie": "relative_humidity_2m",
        "indicator": "umiditate relativă",
        "unitate_implicita": "u.m.",
    },
    {
        "cheie": "wind_speed_10m",
        "indicator": "viteză vânt la 10m",
        "unitate_implicita": "u.m.",
    },
    {
        "cheie": "pressure_msl",
        "indicator": "presiune atmosferică la nivelul mării",
        "unitate_implicita": "u.m.",
    },
    {
        "cheie": "precipitation",
        "indicator": "precipitații curente",
        "unitate_implicita": "u.m.",
    },
    {
        "cheie": "temperature_2m",
        "indicator": "temperatură aer exterior",
        "unitate_implicita": "°C",
        "fara_valori_negative": True,
    },
]

# Etichete statice folosite în payload-ul de colecție pentru UI.
ETICHETE_UI_OPERATII = {
    "GET": "preia / vezi",
    "HEAD": "verifică antete / existență",
    "POST": "adaugă / creează",
    "PUT": "înlocuiește / salvează",
    "PATCH": "actualizare parțială",
    "DELETE": "șterge",
    "OPTIONS": "capacități / metode permise",
    "TRACE": "diagnostic trasabilitate",
}

# Acțiuni semantice expuse în răspunsul de colecție.
ACTIUNI_SEMANTICE_COLECTIE = [
    {"nume": "preia_masuratori", "metoda": "GET", "ruta": "/masuratori"},
    {"nume": "verifica_antete_colectie", "metoda": "HEAD", "ruta": "/masuratori"},
    {"nume": "adauga_masurare", "metoda": "POST", "ruta": "/masuratori"},
    {"nume": "inlocuieste_colectia", "metoda": "PUT", "ruta": "/masuratori"},
    {"nume": "actualizeaza_partial_colectia", "metoda": "PATCH", "ruta": "/masuratori"},
    {"nume": "goleste_colectia", "metoda": "DELETE", "ruta": "/masuratori"},
    {"nume": "capabilitati_colectie", "metoda": "OPTIONS", "ruta": "/masuratori"},
    {"nume": "trace_colectie", "metoda": "TRACE", "ruta": "/masuratori"},
    {"nume": "trace_colectie_ui", "metoda": "POST", "ruta": "/masuratori/trace/colectie"},
    {"nume": "preview_date_externe", "metoda": "POST", "ruta": "/masuratori/preview-extern"},
    {"nume": "sincronizeaza_din_open_meteo", "metoda": "POST", "ruta": "/masuratori/sincronizeaza"},
]

# Acțiuni semantice expuse pentru endpoint-urile pe element.
ACTIUNI_SEMANTICE_ELEMENT = [
    {"nume": "vezi_masurare", "metoda": "GET", "ruta": "/masuratori/<id>"},
    {"nume": "verifica_antete_element", "metoda": "HEAD", "ruta": "/masuratori/<id>"},
    {"nume": "creeaza_masurare_la_id", "metoda": "POST", "ruta": "/masuratori/<id>"},
    {"nume": "salveaza_masurare", "metoda": "PUT", "ruta": "/masuratori/<id>"},
    {"nume": "actualizeaza_partial_element", "metoda": "PATCH", "ruta": "/masuratori/<id>"},
    {"nume": "sterge_masurare", "metoda": "DELETE", "ruta": "/masuratori/<id>"},
    {"nume": "capabilitati_element", "metoda": "OPTIONS", "ruta": "/masuratori/<id>"},
    {"nume": "trace_element", "metoda": "TRACE", "ruta": "/masuratori/<id>"},
    {"nume": "trace_element_ui", "metoda": "POST", "ruta": "/masuratori/trace/element/<id>"},
]

# Lista statică a câmpurilor opționale incluse în răspunsul colecției.
CAMPURI_OPTIONALE = [
    "location",
    "description",
    "category",
    "sensor_name",
    "sensor_model",
    "sensor_manufacturer",
    "operator_name",
    "city",
    "county",
    "source_system",
    "tags",
    "sampling_interval_seconds",
    "measurement_summary",
]


# Generează timestamp UTC în format ISO-8601, ex: 2026-03-29T18:20:00Z.
def acum_utc_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")  # Formatează momentul în ISO UTC cu sufix Z.


# Returnează elementele colecției ordonate crescător după id.
def lista_ordonata():
    return [baza_masuratori[item_id] for item_id in sorted(baza_masuratori.keys())]  # List comprehension ordonată după id.


# Caută prima cheie existentă din lista de aliasuri și returnează valoarea ei.
def prima_valoare(payload, chei):
    for cheie in chei:  # Iterează aliasurile în ordinea priorității.
        if cheie in payload:  # Verifică dacă aliasul există în payload.
            return payload.get(cheie)  # Returnează prima potrivire găsită.
    return None  # Dacă niciun alias nu există, întoarce None.


# Normalizează intrări numerice:
# - acceptă int/float/string numeric
# - respinge bool, string gol, valori negative și valori invalide.
def valoare_numerica(brut):
    if isinstance(brut, bool):  # Exclude bool; în Python bool este subtip de int.
        return None
    if isinstance(brut, (int, float)):  # Caz numeric direct.
        valoare = float(brut)  # Normalizează intern la float.
    elif isinstance(brut, str):  # Caz text care poate conține număr.
        text = brut.strip()  # Elimină spațiile inutile.
        if not text:  # Șir gol după trim => invalid.
            return None
        try:  # Încearcă parse numeric din text.
            valoare = float(text)
        except ValueError:  # Dacă parse-ul eșuează, întoarce invalid.
            return None
    else:
        return None  # Tip neacceptat pentru câmp numeric.

    if valoare < 0:  # Regula de business: valorile negative nu sunt permise.
        return None

    if valoare.is_integer():  # Dacă partea fracționară e zero,
        return int(valoare)  # convertește la int pentru reprezentare curată.
    return valoare  # Altfel păstrează float.


# Curăță textul și convertește valorile nevalide la None.
def text_scurt(valoare):
    if valoare is None:  # None rămâne None.
        return None
    if not isinstance(valoare, str):  # Acceptă doar string.
        return None
    curat = valoare.strip()  # Elimină spațiile de început/sfârșit.
    return curat if curat else None  # Returnează textul curat sau None dacă e gol.


# Validează câmpul de etichete: listă de stringuri ne-goale.
def valideaza_etichete(etichete):
    if etichete is None:  # Câmp opțional; lipsa lui nu e eroare.
        return None, None
    if not isinstance(etichete, list):  # Tipul trebuie să fie list.
        return None, "etichete/tags trebuie să fie listă de texte."

    rezultat = []  # Va conține etichetele validate/curățate.
    for element in etichete:  # Iterează fiecare etichetă primită.
        if not isinstance(element, str) or not element.strip():  # Fiecare etichetă trebuie să fie text nevid.
            return None, "fiecare etichetă trebuie să fie text nevid."
        rezultat.append(element.strip())  # Curăță și stochează eticheta.
    return rezultat, None  # Returnează lista validă + lipsa erorii.


# Validează intervalul de eșantionare (trebuie să fie numeric și > 0).
def valideaza_interval(interval):
    if interval is None:  # Câmp opțional.
        return None, None
    numeric = valoare_numerica(interval)  # Refolosește validatorul numeric generic.
    if numeric is None or numeric == 0:  # Intervalul trebuie strict pozitiv.
        return None, "sampling_interval_seconds/frecventa_secunde trebuie să fie numeric și > 0."
    return numeric, None  # Returnează valoarea validată.


# Normalizează payload-ul clientului într-un format intern unic,
# acceptând aliasuri de chei (ex: station/statie/punct_masurare).
def valideaza_payload(payload):
    if not isinstance(payload, dict):  # Contract: body-ul API trebuie să fie obiect.
        return None, "Body trebuie să fie obiect JSON."

    statie = text_scurt(prima_valoare(payload, ["station", "statie", "punct_masurare"]))  # Citește stația din aliasuri.
    indicator = text_scurt(prima_valoare(payload, ["metric", "indicator", "parametru"]))  # Citește indicatorul din aliasuri.
    unitate = text_scurt(prima_valoare(payload, ["unit", "unitate", "unitate_masura"]))  # Citește unitatea din aliasuri.
    valoare = valoare_numerica(prima_valoare(payload, ["value", "valoare", "valoare_masurata"]))  # Validează numeric valoarea.

    if not statie:  # Câmp obligatoriu.
        return None, "Lipsește station/statie/punct_masurare."
    if not indicator:  # Câmp obligatoriu.
        return None, "Lipsește metric/indicator/parametru."
    if not unitate:  # Câmp obligatoriu.
        return None, "Lipsește unit/unitate/unitate_masura."
    if valoare is None:  # Câmp obligatoriu numeric valid.
        return None, "value/valoare trebuie să fie numeric și >= 0."

    moment = prima_valoare(payload, ["timestamp", "moment", "moment_inregistrare"])  # Ia timestamp-ul dacă a fost trimis.
    if moment is None:  # Dacă lipsește, completează cu momentul curent UTC.
        moment = acum_utc_iso()
    else:
        moment = text_scurt(moment)  # Curăță timestamp-ul text.
        if not moment:  # Timestamp prezent dar gol => invalid.
            return None, "timestamp/moment trebuie să fie text nevid dacă este trimis."

    rezultat = {  # Payload canonic intern după normalizare.
        "station": statie,
        "metric": indicator,
        "value": valoare,
        "unit": unitate,
        "timestamp": moment,
    }

    for camp, aliasuri in CAMPURI_TEXT_OPTIONALE.items():  # Iterează aliasurile configurate la nivel de modul.
        valoare_text = text_scurt(prima_valoare(payload, aliasuri))  # Extrage și curăță valoarea.
        if valoare_text:  # Adaugă doar dacă există text util.
            rezultat[camp] = valoare_text

    etichete, eroare_etichete = valideaza_etichete(prima_valoare(payload, ["tags", "etichete", "cuvinte_cheie"]))  # Validează lista de tags.
    if eroare_etichete:
        return None, eroare_etichete
    if etichete:
        rezultat["tags"] = etichete  # Scrie tags validați în payload-ul final.

    interval, eroare_interval = valideaza_interval(prima_valoare(payload, ["sampling_interval_seconds", "frecventa_secunde", "interval_esantionare"]))  # Validează intervalul opțional.
    if eroare_interval:
        return None, eroare_interval
    if interval is not None:
        rezultat["sampling_interval_seconds"] = interval  # Scrie intervalul doar dacă există.

    rezumat = f"{indicator} măsurat la {statie}: {valoare} {unitate}"  # Construiește un summary text pentru UI/log.
    rezultat["measurement_summary"] = rezumat  # Atașează summary în payloadul intern.

    return rezultat, None  # Returnează payloadul valid + fără eroare.


# Wrapper standard pentru răspunsuri JSON de eroare.
def raspuns_eroare(mesaj, cod=400):
    return jsonify({"eroare": mesaj}), cod  # Shortcut standard pentru răspunsuri de eroare JSON.


# Construiește header-ul Allow din lista de metode.
def header_allow_pentru(metode):
    return ", ".join(metode)  # Metodele sunt deja curate; avem nevoie doar de join.


# CORS global pentru a permite testarea din tool-uri web (ex: API Checker).
@app.after_request
def adauga_antete_cors(raspuns):
    raspuns.headers["Access-Control-Allow-Origin"] = "*"  # Permite origini multiple (development friendly).
    raspuns.headers["Access-Control-Allow-Methods"] = header_allow_pentru(METODE_HTTP)  # Anunță metodele permise.
    raspuns.headers["Access-Control-Allow-Headers"] = CORS_ALLOW_HEADERS  # Anunță ce antete sunt permise.
    return raspuns  # Returnează același response cu antetele CORS adăugate.


# Răspuns standardizat pentru OPTIONS.
def raspuns_options(ruta, metode, descriere_resursa):
    payload = {  # Construiește payload descriptiv pentru cererea OPTIONS.
        "tip_raspuns": "options",
        "ruta": ruta,
        "resursa": descriere_resursa,
        "metode_permise": metode,
        "nota": "Metoda OPTIONS descrie capabilitățile resursei.",
    }

    raspuns = make_response(jsonify(payload), 200)  # Construiește response JSON cu cod 200.
    allow = header_allow_pentru(metode)  # Transformă lista de metode în șir pentru header.
    raspuns.headers["Allow"] = allow  # Header HTTP standard pentru metodele permise.
    raspuns.headers["Access-Control-Allow-Methods"] = allow  # Refolosește lista pentru CORS preflight.
    raspuns.headers["Access-Control-Allow-Headers"] = "Content-Type"  # Permite Content-Type în preflight.
    return raspuns  # Returnează răspunsul complet pentru OPTIONS.


# Construiește payload-ul de trace (util pentru debugging).
def construieste_payload_trace(ruta, descriere_resursa, simulat_ui=False):
    payload = {  # Structură de debug ce reflectă request-ul curent.
        "tip_raspuns": "trace",
        "ruta": ruta,
        "resursa": descriere_resursa,
        "metoda_reflectata": "TRACE",
        "metoda_transport": request.method,  # Metoda HTTP reală folosită pe transport.
        "query_params": request.args.to_dict(flat=True),  # Query string convertit în dict simplu.
        "headers_primite": dict(request.headers),  # Snapshot complet al headerelor primite.
        "body_primit": request.get_data(as_text=True),  # Body-ul brut ca text.
        "simulare_ui": simulat_ui,
    }

    if simulat_ui:  # Când TRACE vine prin helper UI, atașează explicația explicită.
        payload["nota"] = "Browserul blochează metoda TRACE direct; răspunsul este obținut prin endpoint helper POST."

    return payload  # Returnează obiectul trace gata de serializat.


# Returnează un răspuns HTTP pentru trace, cu header Allow inclus.
def raspuns_trace(ruta, descriere_resursa, metode, simulat_ui=False):
    payload = construieste_payload_trace(ruta, descriere_resursa, simulat_ui=simulat_ui)  # Construiește payloadul de trace.
    raspuns = make_response(jsonify(payload), 200)  # Îl împachetează într-un response JSON.
    raspuns.headers["Allow"] = header_allow_pentru(metode)  # Include metodele permise pentru ruta curentă.
    return raspuns  # Returnează response-ul final de trace.


# Construiește payload-ul răspunsului de colecție (metadata + elemente).
def raspuns_colectie():
    return {  # Returnează un payload bogat pentru dashboard/documentare API.
        "tip_raspuns": "colectie_masuratori",  # Tip semantic al răspunsului.
        "descriere": "Colecție completă de măsurători, cu metadate și elemente.",  # Descriere umană pentru client.
        "operatii_colectie": METODE_COLECTIE,  # Metode acceptate pe ruta de colecție.
        "operatii_element": METODE_ELEMENT,  # Metode acceptate pe ruta de element.
        "operatii_ui": METODE_COLECTIE,  # Metode afișate în UI pentru colecție.
        "etichete_ui": ETICHETE_UI_OPERATII,
        "nota_operatii_ui": "În browser, TRACE este disponibil prin butoane helper care trimit POST către endpointuri dedicate.",  # Clarificare pentru limitarea browserului.
        "regula_date": "Operațiile de scriere folosesc exclusiv date externe (Nominatim + Open-Meteo).",  # Regula de business pentru write.
        "actiuni_semantice_colectie": ACTIUNI_SEMANTICE_COLECTIE,
        "actiuni_semantice_element": ACTIUNI_SEMANTICE_ELEMENT,
        "campuri_principale": ["id", "station", "metric", "value", "unit", "timestamp"],  # Câmpuri obligatorii importante.
        "campuri_optionale": CAMPURI_OPTIONALE,
        "numar_elemente": len(baza_masuratori),  # Numărul curent de elemente din memorie.
        "elemente": lista_ordonata(),  # Lista elementelor ordonată crescător după id.
    }


# Client HTTP simplu pentru endpointuri externe JSON.
def preia_json(url, timeout_secunde=12, antete=None):
    antete_finale = {
        "User-Agent": USER_AGENT_EXTERNE,  # User-Agent explicit pentru request-uri upstream.
        "Accept": "application/json",  # Solicită payload JSON.
    }
    if antete:  # Dacă apelantul oferă antete suplimentare, le suprapune.
        antete_finale.update(antete)

    cerere = Request(url, headers=antete_finale, method="GET")  # Construiește request HTTP GET.
    with urlopen(cerere, timeout=timeout_secunde) as raspuns:  # Deschide conexiunea cu timeout controlat.
        continut = raspuns.read().decode("utf-8")  # Citește bytes și decodează UTF-8.
    return json.loads(continut)  # Parsează textul JSON în obiect Python.


# Geocodare localitate via Nominatim -> lat/lon + metadate adresă.
def geocode_oras_nominatim(oras, judet=None, tara="Romania"):
    bucati = [oras]  # Începe query-ul cu orașul.
    if judet:
        bucati.append(judet)  # Adaugă județul dacă există.
    if tara:
        bucati.append(tara)  # Adaugă țara dacă există.

    params = {
        "q": ", ".join(bucati),  # Compune query-ul final "oras, judet, tara".
        "format": "jsonv2",  # Formatul cerut de la Nominatim.
        "limit": 1,  # Solicită doar primul rezultat.
        "addressdetails": 1,  # Include câmpuri de adresă detaliate.
    }
    url = f"{NOMINATIM_SEARCH_URL}?{urlencode(params)}"  # Encodează parametrii în query string.
    rezultate = preia_json(url)  # Execută request-ul și parsează JSON.

    if not isinstance(rezultate, list) or not rezultate:  # Verifică schema minimă a răspunsului.
        raise ValueError("Nu am găsit coordonate pentru localitatea cerută.")

    rezultat = rezultate[0]  # Alege primul (și singurul) rezultat cerut.
    adresa = rezultat.get("address", {})  # Extrage sub-obiectul address dacă există.

    try:
        latitudine = float(rezultat["lat"])  # Parsează latitudinea ca float.
        longitudine = float(rezultat["lon"])  # Parsează longitudinea ca float.
    except (KeyError, TypeError, ValueError) as eroare:
        raise ValueError("Răspuns invalid de la Nominatim pentru coordonate.") from eroare  # Re-raise cu mesaj de business.

    oras_rezolvat = (
        adresa.get("city")  # Prioritate 1: city.
        or adresa.get("town")  # Prioritate 2: town.
        or adresa.get("village")  # Prioritate 3: village.
        or adresa.get("municipality")  # Prioritate 4: municipality.
        or oras  # Fallback final: orașul cerut inițial.
    )
    judet_rezolvat = adresa.get("county") or adresa.get("state_district") or judet  # Fallback pe ce există.
    tara_rezolvata = adresa.get("country") or tara  # Fallback pe țara cerută.

    return {
        "latitude": latitudine,  # Latitudine numerică pentru Open-Meteo.
        "longitude": longitudine,  # Longitudine numerică pentru Open-Meteo.
        "city": oras_rezolvat,  # Oraș rezolvat de geocoder.
        "county": judet_rezolvat,  # Județ rezolvat.
        "country": tara_rezolvata,  # Țară rezolvată.
        "display_name": rezultat.get("display_name") or oras_rezolvat,  # Etichetă completă fallback.
    }


# Citește măsurările curente din Open-Meteo pentru coordonatele date.
def citeste_open_meteo(latitudine, longitudine):
    parametri_curenti = ",".join([  # Construiește lista CSV de metrici curente cerute.
        "temperature_2m",
        "apparent_temperature",
        "relative_humidity_2m",
        "wind_speed_10m",
        "pressure_msl",
        "precipitation",
    ])

    params = {
        "latitude": f"{latitudine:.6f}",  # Formatează lat cu precizie fixă.
        "longitude": f"{longitudine:.6f}",  # Formatează lon cu precizie fixă.
        "current": parametri_curenti,  # Metricile cerute în răspuns.
        "timezone": "auto",  # Lasă API-ul să deducă timezone-ul local.
        "forecast_days": 1,  # Include date pentru ziua curentă.
    }

    url = f"{OPEN_METEO_FORECAST_URL}?{urlencode(params)}"  # Construiește URL-ul final cu query params.
    raspuns = preia_json(url)  # Execută request-ul către Open-Meteo.

    valori_curente = raspuns.get("current")  # Sub-obiectul cu valori măsurate.
    unitati_curente = raspuns.get("current_units")  # Sub-obiectul cu unități per metrică.
    if not isinstance(valori_curente, dict) or not isinstance(unitati_curente, dict):  # Verifică schema minimă.
        raise ValueError("Răspuns invalid de la Open-Meteo.")

    return {
        "current": valori_curente,  # Valorile curente brute.
        "current_units": unitati_curente,  # Unitățile valorilor curente.
        "timezone": raspuns.get("timezone"),  # Timezone-ul determinat de Open-Meteo.
    }


# Transformă răspunsul Open-Meteo în payload-uri candidate pentru schema internă.
def payloaduri_din_open_meteo(info_geo, meteo):
    valori_curente = meteo.get("current", {})  # Extrage dict-ul cu valori măsurate.
    unitati_curente = meteo.get("current_units", {})  # Extrage dict-ul cu unități.
    moment = valori_curente.get("time") or acum_utc_iso()  # Folosește timpul din API sau fallback UTC local.

    locatie_text = f"lat {info_geo['latitude']:.4f}, lon {info_geo['longitude']:.4f}"  # Formatează coordonatele pentru câmpul location.
    statie = info_geo.get("display_name") or info_geo.get("city") or "Open-Meteo"  # Eticheta stației.
    oras = info_geo.get("city")  # Oraș rezolvat.
    judet = info_geo.get("county")  # Județ rezolvat.

    baza_payload = {  # Câmpuri comune adăugate în fiecare payload metric.
        "statie": statie,
        "oras": oras,
        "judet": judet,
        "locatie": locatie_text,
        "platforma_sursa": "open-meteo",
        "descriere": f"Import automat din Open-Meteo pentru {oras or 'localitatea selectată'}.",
        "moment_inregistrare": moment,
    }

    payloaduri = []  # Lista finală de payloaduri candidate.
    for metrica in MAPARE_METRICI_OPEN_METEO:  # Iterează maparea statică definită global.
        cheie_api = metrica["cheie"]  # Cheia din răspunsul Open-Meteo.
        valoare = valori_curente.get(cheie_api)  # Citește valoarea curentă pentru cheia respectivă.
        if valoare is None:
            continue  # Sare metricile indisponibile în răspuns.

        if metrica.get("fara_valori_negative"):  # Reguli suplimentare pentru anumite metrici.
            if not isinstance(valoare, (int, float)) or valoare < 0:
                continue  # Exclude valori invalide pentru metricile marcate.

        unitate = unitati_curente.get(cheie_api) or metrica["unitate_implicita"]  # Unitatea din API sau fallback implicit.
        payload = {
            **baza_payload,  # Include câmpurile comune.
            "indicator": metrica["indicator"],  # Denumirea internă a indicatorului.
            "valoare": valoare,  # Valoarea măsurată curentă.
            "unitate": unitate,  # Unitatea valorii.
            "etichete": ["extern", "open-meteo", "nominatim", cheie_api],  # Tags utile pentru urmărit proveniența.
        }
        payloaduri.append(payload)  # Adaugă payloadul metricii în lista finală.

    return payloaduri  # Returnează toate candidatele generate din răspunsul extern.


# Normalizează string-uri (lowercase + fără diacritice) pentru matching tolerant.
def text_normalizat(valoare):
    if not isinstance(valoare, str):  # Acceptă numai string.
        return ""

    baza = unicodedata.normalize("NFD", valoare.lower())  # NFD separă litera de semnul diacritic.
    fara_diacritice = "".join(caracter for caracter in baza if unicodedata.category(caracter) != "Mn")  # Elimină mark-urile diacritice.
    return " ".join(fara_diacritice.split())  # Compactează spațiile multiple la unul singur.


# Extrage parametrii de localizare din payload (cu fallback-uri implicite).
def extrage_localizare(payload):
    oras = text_scurt(prima_valoare(payload, ["oras", "city"])) or "Iasi"  # Oraș din payload sau fallback implicit.
    judet = text_scurt(prima_valoare(payload, ["judet", "county", "state"]))  # Județ opțional.
    tara = text_scurt(prima_valoare(payload, ["tara", "country"])) or "Romania"  # Țară din payload sau fallback.
    return oras, judet, tara  # Returnează tuple-ul complet de localizare.


# Pipeline complet pentru date externe: localizare -> meteo -> validare payload intern.
def pregateste_date_externe(payload):
    oras, judet, tara = extrage_localizare(payload)  # Destructurează tuple-ul returnat în cele 3 variabile de localizare.
    info_geo = geocode_oras_nominatim(oras, judet, tara)  # Apelează geocodarea pentru a obține coordonate + metadate.
    meteo = citeste_open_meteo(info_geo["latitude"], info_geo["longitude"])  # Citește valorile meteo pe lat/lon.
    candidati = payloaduri_din_open_meteo(info_geo, meteo)  # Transformă răspunsul Open-Meteo în payload-uri candidate.

    elemente_validate = []  # Va conține doar elementele care trec validarea internă.
    elemente_ignorate = []  # Va păstra elementele respinse + motivul respingerii.
    for candidat in candidati:  # Iterează fiecare candidat rezultat din maparea externă.
        element, mesaj = valideaza_payload(candidat)  # Normalizează și validează schema internă.
        if mesaj:  # Dacă validatorul întoarce mesaj, elementul este invalid.
            elemente_ignorate.append({  # Adaugă intrarea respinsă într-o listă de audit.
                "indicator": candidat.get("indicator"),  # Indicatorul extern care a eșuat.
                "motiv": mesaj,  # Mesajul explicit al validării.
            })
            continue  # Sare la următorul candidat fără a adăuga în lista validă.

        elemente_validate.append(element)  # Candidatele valide sunt stocate pentru utilizare ulterioară.

    return {  # Returnează toate artefactele pipeline-ului extern într-un singur obiect.
        "oras_cerut": oras,  # Localitatea cerută explicit de client.
        "info_geo": info_geo,  # Datele geocodate (lat/lon + adresă rezolvată).
        "elemente_validate": elemente_validate,  # Lista elementelor gata de persistat.
        "elemente_ignorate": elemente_ignorate,  # Lista elementelor respinse cu motiv.
    }


# Wrapper robust pentru extragere externă + tratare erori de rețea/validare.
def extrage_date_externe_din_request():
    payload = request.get_json(silent=True)  # Parsează JSON-ul din request.
    if payload is None:  # Fără body => obiect gol (fallback).
        payload = {}
    elif not isinstance(payload, dict):  # Acceptăm doar obiect JSON.
        return None, None, raspuns_eroare("Body trebuie să fie obiect JSON.", 400)

    try:  # Protejează secțiunea care depinde de rețea + validare externă.
        date_externe = pregateste_date_externe(payload)  # Rulează pipeline-ul geocoding + meteo + validare.
    except ValueError as eroare:  # Erori de business/validare a datelor primite.
        return payload, None, raspuns_eroare(str(eroare), 400)  # 400 = input nevalid.
    except (HTTPError, URLError, TimeoutError, OSError):  # Erori I/O/rețea către sursa externă.
        return payload, None, raspuns_eroare("Sursa externă este indisponibilă momentan.", 502)  # 502 = upstream indisponibil.

    return payload, date_externe, None  # Contract succes: avem payload + date_externe, fără răspuns de eroare.


# Alege elementul extern după indicator cerut; fallback = primul valid.
def selecteaza_element_extern(elemente_validate, payload_client):
    if not elemente_validate:  # Guard clause: nu avem nimic valid de selectat.
        return None

    indicator_cerut = text_scurt(prima_valoare(payload_client, ["indicator", "metric", "parametru"]))  # Acceptă aliasuri de cheie.
    if not indicator_cerut:  # Dacă clientul nu a specificat indicator, fallback = primul valid.
        return elemente_validate[0]

    indicator_cerut_normalizat = text_normalizat(indicator_cerut)  # Normalizează (lower + fără diacritice + spații compacte).

    for element in elemente_validate:  # Caută potrivire tolerantă în fiecare element valid.
        metric = element.get("metric")  # Citește numele intern al indicatorului.
        metric_normalizat = text_normalizat(metric)  # Normalizează pentru comparare robustă.
        if (
            metric_normalizat == indicator_cerut_normalizat  # Match exact.
            or indicator_cerut_normalizat in metric_normalizat  # Match prin includere (cerut în metric).
            or metric_normalizat in indicator_cerut_normalizat  # Match prin includere inversă.
        ):
            return element  # Return imediat primul match.

    return elemente_validate[0]  # Fallback final: primul element valid dacă nu există match explicit.


# Caută primul id care potrivește metric + (opțional) oraș.
def gaseste_id_dupa_metric_si_oras(metric_cautat, oras_cautat):
    metric_normalizat = text_normalizat(metric_cautat)  # Normalizează cheia metrică pentru comparare consistentă.
    oras_normalizat = text_normalizat(oras_cautat)  # Normalizează orașul țintă.

    if not metric_normalizat:  # Fără metrică nu are sens matching-ul.
        return None

    for item_id in sorted(baza_masuratori.keys()):  # Iterează determinist după id crescător.
        element = baza_masuratori[item_id]  # Elementul curent din colecție.
        metric_curent = text_normalizat(element.get("metric"))  # Normalizează metrica elementului.
        if metric_curent != metric_normalizat:  # Filtrare după metrică.
            continue

        oras_curent = text_normalizat(element.get("city"))  # Normalizează orașul elementului.
        if oras_normalizat:  # Dacă clientul a dat oraș, cerem și match pe oraș.
            if oras_curent == oras_normalizat:
                return item_id  # Primul id care potrivește metrică + oraș.
        else:
            return item_id  # Dacă orașul nu e dat, e suficient match pe metrică.

    return None  # Nu a fost găsit niciun id compatibil.


# Salvează elementul în colecție, menținând corect următorul id.
def salveaza_element(element, item_id=None):
    global urmatorul_id  # Declară că funcția modifică variabila globală.

    if item_id is None:  # Dacă id-ul nu e forțat, se folosește următorul id liber.
        item_id = urmatorul_id

    if item_id >= urmatorul_id:  # Menține corect monotonia contorului global.
        urmatorul_id = item_id + 1

    creat = {"id": item_id, **element}  # Dict merge: adaugă `id` peste payload-ul validat.
    baza_masuratori[item_id] = creat  # Persistă elementul în colecția in-memory.
    return creat  # Returnează elementul final salvat.


# Aplică patch doar pentru câmpurile care se schimbă.
def aplica_patch_element(element_baza, campuri_noi):
    element_actualizat = {**element_baza}  # Copie shallow pentru a evita mutarea originalului.
    campuri_actualizate = []  # Va colecta doar cheile efectiv modificate.

    for camp, valoare in campuri_noi.items():  # Iterează perechile cheie-valoare noi.
        if element_actualizat.get(camp) != valoare:  # Modifică doar dacă valoarea e diferită.
            element_actualizat[camp] = valoare  # Aplică noua valoare în copia de lucru.
            campuri_actualizate.append(camp)  # Marchează câmpul ca modificat.

    return element_actualizat, sorted(campuri_actualizate)  # Returnează elementul patch-uit + lista câmpurilor ordonată.


# Creează răspuns standard 201 + header Location.
def raspuns_creare(payload, item_id):
    raspuns = make_response(jsonify(payload), 201)  # Creează răspuns JSON cu status 201 Created.
    raspuns.headers["Location"] = f"/masuratori/{item_id}"  # Header standard pentru resursa nou creată.
    return raspuns  # Returnează obiectul Response complet.


# Flux comun pentru endpointurile care consumă date externe și aleg un singur element.
def extrage_element_extern_din_request(actiune, mesaj_eroare, extra=None, adauga_oras_cerut=False):
    payload, date_externe, raspuns_eroare_externa = extrage_date_externe_din_request()  # Rulează pipeline-ul comun extern.
    if raspuns_eroare_externa:  # Propagă direct eroarea dacă etapa externă a eșuat.
        return None, None, raspuns_eroare_externa

    element = selecteaza_element_extern(date_externe["elemente_validate"], payload)  # Alege elementul cerut/implicit.
    if element is None:
        payload_eroare = {
            "eroare": mesaj_eroare,
            "actiune": actiune,
            "numar_ignorate": len(date_externe["elemente_ignorate"]),
            "elemente_ignorate": date_externe["elemente_ignorate"],
        }
        if adauga_oras_cerut:
            payload_eroare["oras_cerut"] = date_externe["oras_cerut"]
        if extra:
            payload_eroare.update(extra)
        return None, None, make_response(jsonify(payload_eroare), 502)

    return element, date_externe, None  # Contract succes: elementul ales + context extern.


# Pagina UI principală.
@app.route("/", methods=["GET"])
def acasa():
    return render_template("panou_masuratori.html")  # Randează template-ul HTML al dashboard-ului local.


# TRACE helper pentru colecție (browserul nu permite TRACE direct).
@app.route("/measurements/trace/collection", methods=["POST"])
@app.route("/masuratori/trace/colectie", methods=["POST"])
def endpoint_trace_ui_colectie():
    return raspuns_trace("/masuratori", "colectie_masuratori", METODE_COLECTIE, simulat_ui=True)  # Returnează trace helper pentru colecție (transport POST).


# TRACE helper pentru element individual.
@app.route("/measurements/trace/item/<int:item_id>", methods=["POST"])
@app.route("/masuratori/trace/element/<int:item_id>", methods=["POST"])
def endpoint_trace_ui_element(item_id):
    if item_id <= 0:  # Validează parametru de rută convertit automat la int de Flask.
        return raspuns_eroare("item_id trebuie să fie pozitiv.", 400)  # 400 pentru id invalid.
    return raspuns_trace(f"/masuratori/{item_id}", f"element_masurare_{item_id}", METODE_ELEMENT, simulat_ui=True)  # Returnează trace simulat pentru browser.


# Preview import extern (fără persistare în baza_masuratori).
@app.route("/measurements/external-preview", methods=["POST"])
@app.route("/masuratori/preview-extern", methods=["POST"])
def endpoint_preview_extern():
    _, date_externe, raspuns_eroare_externa = extrage_date_externe_din_request()  # Rulează pipeline extern fără persistare.
    if raspuns_eroare_externa:  # Propagă eroarea dacă upstream-ul eșuează.
        return raspuns_eroare_externa

    elemente_preview = [  # Construiește lista de preview cu id-uri temporare.
        {"id_preview": index, **element}  # Dict merge: atașează `id_preview` peste element.
        for index, element in enumerate(date_externe["elemente_validate"], start=1)  # enumerate(..., start=1) dă indexare umană.
    ]

    return jsonify({  # Returnează preview-ul în format JSON, status 200.
        "mesaj": "Preview date externe generat.",  # Mesaj orientat UI.
        "actiune": "preview_date_externe",  # Etichetă semantică a acțiunii.
        "sursa": "open-meteo",  # Sursa datelor externe.
        "oras_cerut": date_externe["oras_cerut"],  # Input-ul clientului.
        "oras_rezolvat": date_externe["info_geo"].get("city"),  # Orașul returnat de geocodare.
        "numar_preview": len(elemente_preview),  # Numărul elementelor valide afișate în preview.
        "numar_ignorate": len(date_externe["elemente_ignorate"]),  # Câte intrări au fost respinse.
        "elemente_preview": elemente_preview,  # Lista elementelor candidate validate.
        "elemente_ignorate": date_externe["elemente_ignorate"],  # Lista respinsă cu motive.
    }), 200


# Import complet din sursa externă și persistare în colecția locală.
@app.route("/measurements/synchronize", methods=["POST"])
@app.route("/masuratori/sincronizeaza", methods=["POST"])
def endpoint_sincronizare_externa():
    _, date_externe, raspuns_eroare_externa = extrage_date_externe_din_request()  # Obține setul extern validat pentru sincronizare.
    if raspuns_eroare_externa:  # Oprește fluxul dacă upstream-ul a returnat eroare.
        return raspuns_eroare_externa

    elemente_adaugate = [  # Persistă fiecare element valid în baza locală.
        salveaza_element(element)  # Salvează și returnează elementul final cu id.
        for element in date_externe["elemente_validate"]
    ]
    elemente_ignorate = date_externe["elemente_ignorate"]  # Alias local pentru lista de respingeri.

    if not elemente_adaugate:  # Dacă nu s-a putut adăuga nimic valid, întoarce eșec upstream.
        return jsonify({  # Payload de eroare detaliat pentru diagnostic.
            "eroare": "Nu am putut importa măsurători valide din sursa externă.",
            "actiune": "sincronizeaza_din_open_meteo",
            "oras_cerut": date_externe["oras_cerut"],
            "numar_ignorate": len(elemente_ignorate),
            "elemente_ignorate": elemente_ignorate,
        }), 502

    return jsonify({  # Sincronizare reușită: răspuns JSON cu status 201.
        "mesaj": "Sincronizare externă finalizată.",
        "actiune": "sincronizeaza_din_open_meteo",
        "sursa": "open-meteo",
        "oras_cerut": date_externe["oras_cerut"],
        "oras_rezolvat": date_externe["info_geo"].get("city"),
        "numar_adaugate": len(elemente_adaugate),
        "numar_ignorate": len(elemente_ignorate),
        "ids_generate": [element["id"] for element in elemente_adaugate],  # List comprehension pentru extragerea id-urilor.
        "elemente_adaugate": elemente_adaugate,
        "elemente_ignorate": elemente_ignorate,
    }), 201


# Endpoint de colecție: GET/HEAD/POST/PUT/PATCH/DELETE/OPTIONS/TRACE.
@app.route("/measurements", methods=METODE_COLECTIE)
@app.route("/masuratori", methods=METODE_COLECTIE)
def endpoint_colectie():
    global baza_masuratori  # Funcția reasignează colecția în ramura DELETE/PUT.
    global urmatorul_id  # Funcția reasignează contorul în ramura DELETE/PUT.

    if request.method == "OPTIONS":  # Returnează capabilitățile resursei.
        return raspuns_options("/masuratori", METODE_COLECTIE, "colectie_masuratori")

    if request.method == "TRACE":  # Diagnostic request/headers/body.
        return raspuns_trace("/masuratori", "colectie_masuratori", METODE_COLECTIE)

    if request.method == "HEAD":  # HEAD întoarce doar antete, fără body.
        raspuns = make_response("", 200)
        raspuns.headers["Allow"] = header_allow_pentru(METODE_COLECTIE)  # Enumeră metodele permise.
        raspuns.headers["X-Numar-Elemente"] = str(len(baza_masuratori))  # Metadata utilă pentru UI.
        return raspuns

    if request.method == "GET":  # Returnează colecția completă.
        return jsonify(raspuns_colectie()), 200

    # POST: adaugă un element nou din sursa externă.
    if request.method == "POST":  # Creează un element nou în colecție din date externe.
        element, date_externe, raspuns_eroare_externa = extrage_element_extern_din_request(
            "post_colectie_din_api_extern",  # Etichetă semantică pentru logging/răspuns.
            "Nu am putut extrage niciun element valid din sursa externă.",
            adauga_oras_cerut=True,  # Include `oras_cerut` în payload-ul de eroare.
        )
        if raspuns_eroare_externa:  # Abort dacă upstream/validarea a eșuat.
            return raspuns_eroare_externa

        creat = salveaza_element(element)  # Persistă elementul și obține payload-ul final cu id.

        return raspuns_creare(
            {
                **creat,  # Include toate câmpurile elementului creat.
                "actiune": "post_colectie_din_api_extern",  # Metadată semantică.
                "sursa": "open-meteo",  # Metadată despre proveniență.
                "oras_rezolvat": date_externe["info_geo"].get("city"),  # Orașul rezolvat de geocoder.
            },
            creat["id"],  # Id-ul resursei noi pentru header-ul Location.
        )

    # PUT: înlocuiește toată colecția cu date externe validate.
    if request.method == "PUT":  # Înlocuiește întreaga colecție cu un nou set extern validat.
        _, date_externe, raspuns_eroare_externa = extrage_date_externe_din_request()
        if raspuns_eroare_externa:
            return raspuns_eroare_externa

        if not date_externe["elemente_validate"]:  # Caz de eșec: nu există nimic valid de importat.
            return jsonify({
                "eroare": "Nu am putut importa măsurători valide pentru înlocuirea colecției.",
                "actiune": "put_colectie_din_api_extern",
                "oras_cerut": date_externe["oras_cerut"],
                "numar_ignorate": len(date_externe["elemente_ignorate"]),
                "elemente_ignorate": date_externe["elemente_ignorate"],
            }), 502

        date_noi = {
            index: {"id": index, **element}  # Reindexează elementele de la 1 și injectează cheia id.
            for index, element in enumerate(date_externe["elemente_validate"], start=1)
        }

        baza_masuratori = date_noi  # Înlocuire completă a colecției in-memory.
        urmatorul_id = len(baza_masuratori) + 1  # Pregătește următorul id liber după reindexare.

        raspuns = raspuns_colectie()  # Pornește de la payload-ul standard de colecție.
        raspuns["actiune"] = "put_colectie_din_api_extern"  # Adaugă metadate specifice acțiunii.
        raspuns["sursa"] = "open-meteo"
        raspuns["oras_rezolvat"] = date_externe["info_geo"].get("city")
        raspuns["numar_ignorate"] = len(date_externe["elemente_ignorate"])
        raspuns["elemente_ignorate"] = date_externe["elemente_ignorate"]
        return jsonify(raspuns), 200

    # PATCH: update parțial după criteriu metric + city; dacă nu există, creează.
    if request.method == "PATCH":  # Upsert semantic pe baza criteriului metric + oraș.
        element_nou, date_externe, raspuns_eroare_externa = extrage_element_extern_din_request(
            "patch_colectie_din_api_extern",
            "Nu am putut extrage niciun element valid pentru patch din sursa externă.",
            adauga_oras_cerut=True,
        )
        if raspuns_eroare_externa:
            return raspuns_eroare_externa
        id_tinta = gaseste_id_dupa_metric_si_oras(element_nou.get("metric"), element_nou.get("city"))  # Caută id existent compatibil.

        status_patch = "adaugat"  # Valoare implicită; se schimbă la "actualizat" dacă id există.
        cod_status = 201  # Implicit tratăm ca create.
        campuri_actualizate = []  # Colectează câmpurile efectiv schimbate.

        if id_tinta is None:  # Nu există match => creează element nou.
            element_final = salveaza_element(element_nou)
            id_tinta = element_final["id"]
            campuri_actualizate = sorted(list(element_nou.keys()))  # La create, toate cheile sunt considerate actualizate.
        else:  # Există match => patch pe elementul curent.
            element_actualizat, campuri_actualizate = aplica_patch_element(baza_masuratori[id_tinta], element_nou)
            baza_masuratori[id_tinta] = element_actualizat
            status_patch = "actualizat"
            cod_status = 200

        element_final = baza_masuratori[id_tinta]  # Citește versiunea finală persistată.
        payload_raspuns = {
            "actiune": "patch_colectie_din_api_extern",
            "status_patch": status_patch,
            "id_tinta": id_tinta,
            "campuri_actualizate": campuri_actualizate,
            "sursa": "open-meteo",
            "oras_rezolvat": date_externe["info_geo"].get("city"),
            "element": element_final,
        }

        if cod_status == 201:  # Pentru create întoarce 201 + Location.
            return raspuns_creare(payload_raspuns, id_tinta)

        return jsonify(payload_raspuns), 200  # Pentru update întoarce 200.

    if request.method == "DELETE":  # Șterge complet colecția.
        sterse = len(baza_masuratori)  # Memorează câte elemente au fost eliminate.
        baza_masuratori = {}  # Resetează structura de date.
        urmatorul_id = 1  # Resetează contorul id-urilor.
        return jsonify({
            "mesaj": "Toate măsurătorile din colecție au fost șterse.",
            "numar_sterse": sterse,
            "colectie_curenta": [],
        }), 200

    return raspuns_eroare("Metodă HTTP neacceptată pe colecție.", 405)  # Fallback defensiv.


# Endpoint element individual: /masuratori/<id>.
@app.route("/measurements/<int:item_id>", methods=METODE_ELEMENT)
@app.route("/masuratori/<int:item_id>", methods=METODE_ELEMENT)
def endpoint_element(item_id):
    if item_id <= 0:  # Validare parametru de rută.
        return raspuns_eroare("item_id trebuie să fie pozitiv.", 400)

    if request.method == "OPTIONS":  # Capabilități endpoint element.
        return raspuns_options(f"/masuratori/{item_id}", METODE_ELEMENT, f"element_masurare_{item_id}")

    if request.method == "TRACE":  # Trace direct pe resursa individuală.
        return raspuns_trace(f"/masuratori/{item_id}", f"element_masurare_{item_id}", METODE_ELEMENT)

    if request.method == "HEAD":  # HEAD pentru existență + metadate.
        element = baza_masuratori.get(item_id)  # `.get` evită KeyError.
        exista = element is not None  # Convertire explicită la boolean semantic.
        cod = 200 if exista else 404  # Operator ternar pentru codul HTTP.

        raspuns = make_response("", cod)
        raspuns.headers["Allow"] = header_allow_pentru(METODE_ELEMENT)
        raspuns.headers["X-Item-Id"] = str(item_id)
        raspuns.headers["X-Item-Exists"] = "true" if exista else "false"
        if exista:  # Header suplimentar doar dacă itemul există efectiv.
            raspuns.headers["X-Item-Metric"] = str(element.get("metric", ""))
        return raspuns

    if request.method == "GET":  # Returnează payload-ul elementului.
        element = baza_masuratori.get(item_id)
        if element is None:  # Not found.
            return raspuns_eroare("Elementul cerut nu există.", 404)
        return jsonify(element), 200

    # POST la /{id}: creează doar dacă id-ul nu există deja.
    if request.method == "POST":  # Create strict: nu suprascrie un id existent.
        if item_id in baza_masuratori:  # Conflict dacă id-ul există deja.
            return raspuns_eroare("Elementul există deja pentru acest id.", 409)

        element, _, raspuns_eroare_externa = extrage_element_extern_din_request(
            "post_element_din_api_extern",
            "Nu am putut extrage un element valid pentru acest id din sursa externă.",
            extra={"id_cerut": item_id},  # Include id-ul în contextul erorii.
        )
        if raspuns_eroare_externa:
            return raspuns_eroare_externa

        creat = salveaza_element(element, item_id=item_id)  # Persistă elementul exact la id-ul cerut.

        return raspuns_creare(creat, item_id)

    # PUT la /{id}: upsert (actualizează dacă există, creează dacă nu).
    if request.method == "PUT":  # Upsert: actualizează dacă există, creează altfel.
        element, _, raspuns_eroare_externa = extrage_element_extern_din_request(
            "put_element_din_api_extern",
            "Nu am putut extrage un element valid pentru actualizare din sursa externă.",
            extra={"id_cerut": item_id},
        )
        if raspuns_eroare_externa:
            return raspuns_eroare_externa

        exista = item_id in baza_masuratori  # Memo: dacă exista, răspunsul final este 200.
        actualizat = salveaza_element(element, item_id=item_id)  # Save comun pentru create/update.

        if exista:  # Ramura update.
            return jsonify(actualizat), 200

        return raspuns_creare(actualizat, item_id)  # Ramura create.

    # PATCH la /{id}: modifică doar câmpurile diferite.
    if request.method == "PATCH":  # Patch parțial pe item existent.
        element_existent = baza_masuratori.get(item_id)
        if element_existent is None:
            return raspuns_eroare("Elementul cerut nu există pentru patch.", 404)

        element_nou, date_externe, raspuns_eroare_externa = extrage_element_extern_din_request(
            "patch_element_din_api_extern",
            "Nu am putut extrage un element valid pentru patch din sursa externă.",
            extra={"id_cerut": item_id},
        )
        if raspuns_eroare_externa:
            return raspuns_eroare_externa
        element_actualizat, campuri_actualizate = aplica_patch_element(element_existent, element_nou)  # Returnează noul obiect + câmpurile schimbate.

        baza_masuratori[item_id] = element_actualizat  # Persistă rezultatul patch-ului.

        return jsonify({
            "actiune": "patch_element_din_api_extern",
            "id_actualizat": item_id,
            "campuri_actualizate": campuri_actualizate,
            "sursa": "open-meteo",
            "oras_rezolvat": date_externe["info_geo"].get("city"),
            "element": element_actualizat,
        }), 200

    if request.method == "DELETE":  # Șterge item-ul individual dacă există.
        element = baza_masuratori.get(item_id)
        if element is None:
            return raspuns_eroare("Elementul cerut nu există.", 404)

        del baza_masuratori[item_id]  # Operatorul `del` elimină cheia din dict.
        return jsonify({
            "mesaj": "Elementul selectat a fost șters.",
            "id_sters": item_id,
        }), 200

    return raspuns_eroare("Metodă HTTP neacceptată pe element.", 405)  # Fallback defensiv pentru metode neașteptate.


# Entry point local pentru rulare directă a serviciului.
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)  # Rulează serverul Flask local pe portul 5000 în mod debug.
