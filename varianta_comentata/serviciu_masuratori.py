# [AUTO-COMMENT] Linia 1.
from datetime import datetime, timezone
# [AUTO-COMMENT] Linia 2.
import json
# [AUTO-COMMENT] Linia 3.
import unicodedata
# [AUTO-COMMENT] Linia 4.
from urllib.error import HTTPError, URLError
# [AUTO-COMMENT] Linia 5.
from urllib.parse import urlencode
# [AUTO-COMMENT] Linia 6.
from urllib.request import Request, urlopen
# [AUTO-COMMENT] Linia 7: linie goală.

# [AUTO-COMMENT] Linia 8.
from flask import Flask, jsonify, make_response, render_template, request
# [AUTO-COMMENT] Linia 9: linie goală.

# [AUTO-COMMENT] Linia 10.
app = Flask(__name__)
# [AUTO-COMMENT] Linia 11: linie goală.

# [AUTO-COMMENT] Linia 12.
baza_masuratori = {}
# [AUTO-COMMENT] Linia 13.
urmatorul_id = 1
# [AUTO-COMMENT] Linia 14: linie goală.

# [AUTO-COMMENT] Linia 15.
NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
# [AUTO-COMMENT] Linia 16.
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
# [AUTO-COMMENT] Linia 17.
USER_AGENT_EXTERNE = "Tema2-TAD-Masuratori/1.0 (educational project)"
# [AUTO-COMMENT] Linia 18.
METODE_HTTP = ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE"]
# [AUTO-COMMENT] Linia 19.
METODE_COLECTIE = METODE_HTTP
# [AUTO-COMMENT] Linia 20.
METODE_ELEMENT = METODE_HTTP
# [AUTO-COMMENT] Linia 21: linie goală.

# [AUTO-COMMENT] Linia 22: linie goală.

# [AUTO-COMMENT] Linia 23.
def acum_utc_iso():
# [AUTO-COMMENT] Linia 24.
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
# [AUTO-COMMENT] Linia 25: linie goală.

# [AUTO-COMMENT] Linia 26: linie goală.

# [AUTO-COMMENT] Linia 27.
def lista_ordonata():
# [AUTO-COMMENT] Linia 28.
    return [baza_masuratori[item_id] for item_id in sorted(baza_masuratori.keys())]
# [AUTO-COMMENT] Linia 29: linie goală.

# [AUTO-COMMENT] Linia 30: linie goală.

# [AUTO-COMMENT] Linia 31.
def prima_valoare(payload, chei):
# [AUTO-COMMENT] Linia 32.
    for cheie in chei:
# [AUTO-COMMENT] Linia 33.
        if cheie in payload:
# [AUTO-COMMENT] Linia 34.
            return payload.get(cheie)
# [AUTO-COMMENT] Linia 35.
    return None
# [AUTO-COMMENT] Linia 36: linie goală.

# [AUTO-COMMENT] Linia 37: linie goală.

# [AUTO-COMMENT] Linia 38.
def valoare_numerica(brut):
# [AUTO-COMMENT] Linia 39.
    if isinstance(brut, bool):
# [AUTO-COMMENT] Linia 40.
        return None
# [AUTO-COMMENT] Linia 41.
    if isinstance(brut, (int, float)):
# [AUTO-COMMENT] Linia 42.
        valoare = float(brut)
# [AUTO-COMMENT] Linia 43.
    elif isinstance(brut, str):
# [AUTO-COMMENT] Linia 44.
        text = brut.strip()
# [AUTO-COMMENT] Linia 45.
        if not text:
# [AUTO-COMMENT] Linia 46.
            return None
# [AUTO-COMMENT] Linia 47.
        try:
# [AUTO-COMMENT] Linia 48.
            valoare = float(text)
# [AUTO-COMMENT] Linia 49.
        except ValueError:
# [AUTO-COMMENT] Linia 50.
            return None
# [AUTO-COMMENT] Linia 51.
    else:
# [AUTO-COMMENT] Linia 52.
        return None
# [AUTO-COMMENT] Linia 53: linie goală.

# [AUTO-COMMENT] Linia 54.
    if valoare < 0:
# [AUTO-COMMENT] Linia 55.
        return None
# [AUTO-COMMENT] Linia 56: linie goală.

# [AUTO-COMMENT] Linia 57.
    if valoare.is_integer():
# [AUTO-COMMENT] Linia 58.
        return int(valoare)
# [AUTO-COMMENT] Linia 59.
    return valoare
# [AUTO-COMMENT] Linia 60: linie goală.

# [AUTO-COMMENT] Linia 61: linie goală.

# [AUTO-COMMENT] Linia 62.
def text_scurt(valoare):
# [AUTO-COMMENT] Linia 63.
    if valoare is None:
# [AUTO-COMMENT] Linia 64.
        return None
# [AUTO-COMMENT] Linia 65.
    if not isinstance(valoare, str):
# [AUTO-COMMENT] Linia 66.
        return None
# [AUTO-COMMENT] Linia 67.
    curat = valoare.strip()
# [AUTO-COMMENT] Linia 68.
    return curat if curat else None
# [AUTO-COMMENT] Linia 69: linie goală.

# [AUTO-COMMENT] Linia 70: linie goală.

# [AUTO-COMMENT] Linia 71.
def valideaza_etichete(etichete):
# [AUTO-COMMENT] Linia 72.
    if etichete is None:
# [AUTO-COMMENT] Linia 73.
        return None, None
# [AUTO-COMMENT] Linia 74.
    if not isinstance(etichete, list):
# [AUTO-COMMENT] Linia 75.
        return None, "etichete/tags trebuie să fie listă de texte."
# [AUTO-COMMENT] Linia 76: linie goală.

# [AUTO-COMMENT] Linia 77.
    rezultat = []
# [AUTO-COMMENT] Linia 78.
    for element in etichete:
# [AUTO-COMMENT] Linia 79.
        if not isinstance(element, str) or not element.strip():
# [AUTO-COMMENT] Linia 80.
            return None, "fiecare etichetă trebuie să fie text nevid."
# [AUTO-COMMENT] Linia 81.
        rezultat.append(element.strip())
# [AUTO-COMMENT] Linia 82.
    return rezultat, None
# [AUTO-COMMENT] Linia 83: linie goală.

# [AUTO-COMMENT] Linia 84: linie goală.

# [AUTO-COMMENT] Linia 85.
def valideaza_interval(interval):
# [AUTO-COMMENT] Linia 86.
    if interval is None:
# [AUTO-COMMENT] Linia 87.
        return None, None
# [AUTO-COMMENT] Linia 88.
    numeric = valoare_numerica(interval)
# [AUTO-COMMENT] Linia 89.
    if numeric is None or numeric == 0:
# [AUTO-COMMENT] Linia 90.
        return None, "sampling_interval_seconds/frecventa_secunde trebuie să fie numeric și > 0."
# [AUTO-COMMENT] Linia 91.
    return numeric, None
# [AUTO-COMMENT] Linia 92: linie goală.

# [AUTO-COMMENT] Linia 93: linie goală.

# [AUTO-COMMENT] Linia 94.
def valideaza_payload(payload):
# [AUTO-COMMENT] Linia 95.
    if not isinstance(payload, dict):
# [AUTO-COMMENT] Linia 96.
        return None, "Body trebuie să fie obiect JSON."
# [AUTO-COMMENT] Linia 97: linie goală.

# [AUTO-COMMENT] Linia 98.
    statie = text_scurt(prima_valoare(payload, ["station", "statie", "punct_masurare"]))
# [AUTO-COMMENT] Linia 99.
    indicator = text_scurt(prima_valoare(payload, ["metric", "indicator", "parametru"]))
# [AUTO-COMMENT] Linia 100.
    unitate = text_scurt(prima_valoare(payload, ["unit", "unitate", "unitate_masura"]))
# [AUTO-COMMENT] Linia 101.
    valoare = valoare_numerica(prima_valoare(payload, ["value", "valoare", "valoare_masurata"]))
# [AUTO-COMMENT] Linia 102: linie goală.

# [AUTO-COMMENT] Linia 103.
    if not statie:
# [AUTO-COMMENT] Linia 104.
        return None, "Lipsește station/statie/punct_masurare."
# [AUTO-COMMENT] Linia 105.
    if not indicator:
# [AUTO-COMMENT] Linia 106.
        return None, "Lipsește metric/indicator/parametru."
# [AUTO-COMMENT] Linia 107.
    if not unitate:
# [AUTO-COMMENT] Linia 108.
        return None, "Lipsește unit/unitate/unitate_masura."
# [AUTO-COMMENT] Linia 109.
    if valoare is None:
# [AUTO-COMMENT] Linia 110.
        return None, "value/valoare trebuie să fie numeric și >= 0."
# [AUTO-COMMENT] Linia 111: linie goală.

# [AUTO-COMMENT] Linia 112.
    moment = prima_valoare(payload, ["timestamp", "moment", "moment_inregistrare"])
# [AUTO-COMMENT] Linia 113.
    if moment is None:
# [AUTO-COMMENT] Linia 114.
        moment = acum_utc_iso()
# [AUTO-COMMENT] Linia 115.
    else:
# [AUTO-COMMENT] Linia 116.
        moment = text_scurt(moment)
# [AUTO-COMMENT] Linia 117.
        if not moment:
# [AUTO-COMMENT] Linia 118.
            return None, "timestamp/moment trebuie să fie text nevid dacă este trimis."
# [AUTO-COMMENT] Linia 119: linie goală.

# [AUTO-COMMENT] Linia 120.
    campuri_text_optionale = {
# [AUTO-COMMENT] Linia 121.
        "location": ["location", "locatie", "pozitie_instalare"],
# [AUTO-COMMENT] Linia 122.
        "description": ["description", "descriere", "detalii"],
# [AUTO-COMMENT] Linia 123.
        "category": ["category", "categorie", "domeniu"],
# [AUTO-COMMENT] Linia 124.
        "sensor_name": ["sensor_name", "nume_senzor"],
# [AUTO-COMMENT] Linia 125.
        "sensor_model": ["sensor_model", "model_senzor"],
# [AUTO-COMMENT] Linia 126.
        "sensor_manufacturer": ["sensor_manufacturer", "producator_senzor"],
# [AUTO-COMMENT] Linia 127.
        "operator_name": ["operator_name", "responsabil", "persoana_responsabila"],
# [AUTO-COMMENT] Linia 128.
        "city": ["city", "oras"],
# [AUTO-COMMENT] Linia 129.
        "county": ["county", "judet"],
# [AUTO-COMMENT] Linia 130.
        "source_system": ["source_system", "sursa_date", "platforma_sursa"],
# [AUTO-COMMENT] Linia 131.
    }
# [AUTO-COMMENT] Linia 132: linie goală.

# [AUTO-COMMENT] Linia 133.
    rezultat = {
# [AUTO-COMMENT] Linia 134.
        "station": statie,
# [AUTO-COMMENT] Linia 135.
        "metric": indicator,
# [AUTO-COMMENT] Linia 136.
        "value": valoare,
# [AUTO-COMMENT] Linia 137.
        "unit": unitate,
# [AUTO-COMMENT] Linia 138.
        "timestamp": moment,
# [AUTO-COMMENT] Linia 139.
    }
# [AUTO-COMMENT] Linia 140: linie goală.

# [AUTO-COMMENT] Linia 141.
    for camp, aliasuri in campuri_text_optionale.items():
# [AUTO-COMMENT] Linia 142.
        valoare_text = text_scurt(prima_valoare(payload, aliasuri))
# [AUTO-COMMENT] Linia 143.
        if valoare_text:
# [AUTO-COMMENT] Linia 144.
            rezultat[camp] = valoare_text
# [AUTO-COMMENT] Linia 145: linie goală.

# [AUTO-COMMENT] Linia 146.
    etichete, eroare_etichete = valideaza_etichete(prima_valoare(payload, ["tags", "etichete", "cuvinte_cheie"]))
# [AUTO-COMMENT] Linia 147.
    if eroare_etichete:
# [AUTO-COMMENT] Linia 148.
        return None, eroare_etichete
# [AUTO-COMMENT] Linia 149.
    if etichete:
# [AUTO-COMMENT] Linia 150.
        rezultat["tags"] = etichete
# [AUTO-COMMENT] Linia 151: linie goală.

# [AUTO-COMMENT] Linia 152.
    interval, eroare_interval = valideaza_interval(prima_valoare(payload, ["sampling_interval_seconds", "frecventa_secunde", "interval_esantionare"]))
# [AUTO-COMMENT] Linia 153.
    if eroare_interval:
# [AUTO-COMMENT] Linia 154.
        return None, eroare_interval
# [AUTO-COMMENT] Linia 155.
    if interval is not None:
# [AUTO-COMMENT] Linia 156.
        rezultat["sampling_interval_seconds"] = interval
# [AUTO-COMMENT] Linia 157: linie goală.

# [AUTO-COMMENT] Linia 158.
    rezumat = f"{indicator} măsurat la {statie}: {valoare} {unitate}"
# [AUTO-COMMENT] Linia 159.
    rezultat["measurement_summary"] = rezumat
# [AUTO-COMMENT] Linia 160: linie goală.

# [AUTO-COMMENT] Linia 161.
    return rezultat, None
# [AUTO-COMMENT] Linia 162: linie goală.

# [AUTO-COMMENT] Linia 163: linie goală.

# [AUTO-COMMENT] Linia 164.
def raspuns_eroare(mesaj, cod=400):
# [AUTO-COMMENT] Linia 165.
    return jsonify({"eroare": mesaj}), cod
# [AUTO-COMMENT] Linia 166: linie goală.

# [AUTO-COMMENT] Linia 167: linie goală.

# [AUTO-COMMENT] Linia 168.
def metode_cu_head_unice(metode):
# [AUTO-COMMENT] Linia 169.
    return list(dict.fromkeys([*metode, "HEAD"]))
# [AUTO-COMMENT] Linia 170: linie goală.

# [AUTO-COMMENT] Linia 171: linie goală.

# [AUTO-COMMENT] Linia 172.
def header_allow_pentru(metode):
# [AUTO-COMMENT] Linia 173.
    return ", ".join(metode_cu_head_unice(metode))
# [AUTO-COMMENT] Linia 174: linie goală.

# [AUTO-COMMENT] Linia 175: linie goală.

# [AUTO-COMMENT] Linia 176.
def raspuns_options(ruta, metode, descriere_resursa):
# [AUTO-COMMENT] Linia 177.
    metode_permise = metode_cu_head_unice(metode)
# [AUTO-COMMENT] Linia 178.
    payload = {
# [AUTO-COMMENT] Linia 179.
        "tip_raspuns": "options",
# [AUTO-COMMENT] Linia 180.
        "ruta": ruta,
# [AUTO-COMMENT] Linia 181.
        "resursa": descriere_resursa,
# [AUTO-COMMENT] Linia 182.
        "metode_permise": metode_permise,
# [AUTO-COMMENT] Linia 183.
        "nota": "Metoda OPTIONS descrie capabilitățile resursei.",
# [AUTO-COMMENT] Linia 184.
    }
# [AUTO-COMMENT] Linia 185: linie goală.

# [AUTO-COMMENT] Linia 186.
    raspuns = make_response(jsonify(payload), 200)
# [AUTO-COMMENT] Linia 187.
    allow = header_allow_pentru(metode)
# [AUTO-COMMENT] Linia 188.
    raspuns.headers["Allow"] = allow
# [AUTO-COMMENT] Linia 189.
    raspuns.headers["Access-Control-Allow-Methods"] = allow
# [AUTO-COMMENT] Linia 190.
    raspuns.headers["Access-Control-Allow-Headers"] = "Content-Type"
# [AUTO-COMMENT] Linia 191.
    return raspuns
# [AUTO-COMMENT] Linia 192: linie goală.

# [AUTO-COMMENT] Linia 193: linie goală.

# [AUTO-COMMENT] Linia 194.
def construieste_payload_trace(ruta, descriere_resursa, simulat_ui=False):
# [AUTO-COMMENT] Linia 195.
    payload = {
# [AUTO-COMMENT] Linia 196.
        "tip_raspuns": "trace",
# [AUTO-COMMENT] Linia 197.
        "ruta": ruta,
# [AUTO-COMMENT] Linia 198.
        "resursa": descriere_resursa,
# [AUTO-COMMENT] Linia 199.
        "metoda_reflectata": "TRACE",
# [AUTO-COMMENT] Linia 200.
        "metoda_transport": request.method,
# [AUTO-COMMENT] Linia 201.
        "query_params": request.args.to_dict(flat=True),
# [AUTO-COMMENT] Linia 202.
        "headers_primite": dict(request.headers),
# [AUTO-COMMENT] Linia 203.
        "body_primit": request.get_data(as_text=True),
# [AUTO-COMMENT] Linia 204.
        "simulare_ui": simulat_ui,
# [AUTO-COMMENT] Linia 205.
    }
# [AUTO-COMMENT] Linia 206: linie goală.

# [AUTO-COMMENT] Linia 207.
    if simulat_ui:
# [AUTO-COMMENT] Linia 208.
        payload["nota"] = "Browserul blochează metoda TRACE direct; răspunsul este obținut prin endpoint helper POST."
# [AUTO-COMMENT] Linia 209: linie goală.

# [AUTO-COMMENT] Linia 210.
    return payload
# [AUTO-COMMENT] Linia 211: linie goală.

# [AUTO-COMMENT] Linia 212: linie goală.

# [AUTO-COMMENT] Linia 213.
def raspuns_trace(ruta, descriere_resursa, metode, simulat_ui=False):
# [AUTO-COMMENT] Linia 214.
    payload = construieste_payload_trace(ruta, descriere_resursa, simulat_ui=simulat_ui)
# [AUTO-COMMENT] Linia 215.
    raspuns = make_response(jsonify(payload), 200)
# [AUTO-COMMENT] Linia 216.
    raspuns.headers["Allow"] = header_allow_pentru(metode)
# [AUTO-COMMENT] Linia 217.
    return raspuns
# [AUTO-COMMENT] Linia 218: linie goală.

# [AUTO-COMMENT] Linia 219: linie goală.

# [AUTO-COMMENT] Linia 220.
def raspuns_colectie():
# [AUTO-COMMENT] Linia 221.
    return {
# [AUTO-COMMENT] Linia 222.
        "tip_raspuns": "colectie_masuratori",
# [AUTO-COMMENT] Linia 223.
        "descriere": "Colecție completă de măsurători, cu metadate și elemente.",
# [AUTO-COMMENT] Linia 224.
        "operatii_colectie": METODE_COLECTIE,
# [AUTO-COMMENT] Linia 225.
        "operatii_element": METODE_ELEMENT,
# [AUTO-COMMENT] Linia 226.
        "operatii_ui": METODE_COLECTIE,
# [AUTO-COMMENT] Linia 227.
        "etichete_ui": {
# [AUTO-COMMENT] Linia 228.
            "GET": "preia / vezi",
# [AUTO-COMMENT] Linia 229.
            "HEAD": "verifică antete / existență",
# [AUTO-COMMENT] Linia 230.
            "POST": "adaugă / creează",
# [AUTO-COMMENT] Linia 231.
            "PUT": "înlocuiește / salvează",
# [AUTO-COMMENT] Linia 232.
            "PATCH": "actualizare parțială",
# [AUTO-COMMENT] Linia 233.
            "DELETE": "șterge",
# [AUTO-COMMENT] Linia 234.
            "OPTIONS": "capacități / metode permise",
# [AUTO-COMMENT] Linia 235.
            "TRACE": "diagnostic trasabilitate",
# [AUTO-COMMENT] Linia 236.
        },
# [AUTO-COMMENT] Linia 237.
        "nota_operatii_ui": "În browser, TRACE este disponibil prin butoane helper care trimit POST către endpointuri dedicate.",
# [AUTO-COMMENT] Linia 238.
        "regula_date": "Operațiile de scriere folosesc exclusiv date externe (Nominatim + Open-Meteo).",
# [AUTO-COMMENT] Linia 239.
        "actiuni_semantice_colectie": [
# [AUTO-COMMENT] Linia 240.
            {"nume": "preia_masuratori", "metoda": "GET", "ruta": "/masuratori"},
# [AUTO-COMMENT] Linia 241.
            {"nume": "verifica_antete_colectie", "metoda": "HEAD", "ruta": "/masuratori"},
# [AUTO-COMMENT] Linia 242.
            {"nume": "adauga_masurare", "metoda": "POST", "ruta": "/masuratori"},
# [AUTO-COMMENT] Linia 243.
            {"nume": "inlocuieste_colectia", "metoda": "PUT", "ruta": "/masuratori"},
# [AUTO-COMMENT] Linia 244.
            {"nume": "actualizeaza_partial_colectia", "metoda": "PATCH", "ruta": "/masuratori"},
# [AUTO-COMMENT] Linia 245.
            {"nume": "goleste_colectia", "metoda": "DELETE", "ruta": "/masuratori"},
# [AUTO-COMMENT] Linia 246.
            {"nume": "capabilitati_colectie", "metoda": "OPTIONS", "ruta": "/masuratori"},
# [AUTO-COMMENT] Linia 247.
            {"nume": "trace_colectie", "metoda": "TRACE", "ruta": "/masuratori"},
# [AUTO-COMMENT] Linia 248.
            {"nume": "trace_colectie_ui", "metoda": "POST", "ruta": "/masuratori/trace/colectie"},
# [AUTO-COMMENT] Linia 249.
            {"nume": "preview_date_externe", "metoda": "POST", "ruta": "/masuratori/preview-extern"},
# [AUTO-COMMENT] Linia 250.
            {"nume": "sincronizeaza_din_open_meteo", "metoda": "POST", "ruta": "/masuratori/sincronizeaza"},
# [AUTO-COMMENT] Linia 251.
        ],
# [AUTO-COMMENT] Linia 252.
        "actiuni_semantice_element": [
# [AUTO-COMMENT] Linia 253.
            {"nume": "vezi_masurare", "metoda": "GET", "ruta": "/masuratori/<id>"},
# [AUTO-COMMENT] Linia 254.
            {"nume": "verifica_antete_element", "metoda": "HEAD", "ruta": "/masuratori/<id>"},
# [AUTO-COMMENT] Linia 255.
            {"nume": "creeaza_masurare_la_id", "metoda": "POST", "ruta": "/masuratori/<id>"},
# [AUTO-COMMENT] Linia 256.
            {"nume": "salveaza_masurare", "metoda": "PUT", "ruta": "/masuratori/<id>"},
# [AUTO-COMMENT] Linia 257.
            {"nume": "actualizeaza_partial_element", "metoda": "PATCH", "ruta": "/masuratori/<id>"},
# [AUTO-COMMENT] Linia 258.
            {"nume": "sterge_masurare", "metoda": "DELETE", "ruta": "/masuratori/<id>"},
# [AUTO-COMMENT] Linia 259.
            {"nume": "capabilitati_element", "metoda": "OPTIONS", "ruta": "/masuratori/<id>"},
# [AUTO-COMMENT] Linia 260.
            {"nume": "trace_element", "metoda": "TRACE", "ruta": "/masuratori/<id>"},
# [AUTO-COMMENT] Linia 261.
            {"nume": "trace_element_ui", "metoda": "POST", "ruta": "/masuratori/trace/element/<id>"},
# [AUTO-COMMENT] Linia 262.
        ],
# [AUTO-COMMENT] Linia 263.
        "campuri_principale": ["id", "station", "metric", "value", "unit", "timestamp"],
# [AUTO-COMMENT] Linia 264.
        "campuri_optionale": [
# [AUTO-COMMENT] Linia 265.
            "location",
# [AUTO-COMMENT] Linia 266.
            "description",
# [AUTO-COMMENT] Linia 267.
            "category",
# [AUTO-COMMENT] Linia 268.
            "sensor_name",
# [AUTO-COMMENT] Linia 269.
            "sensor_model",
# [AUTO-COMMENT] Linia 270.
            "sensor_manufacturer",
# [AUTO-COMMENT] Linia 271.
            "operator_name",
# [AUTO-COMMENT] Linia 272.
            "city",
# [AUTO-COMMENT] Linia 273.
            "county",
# [AUTO-COMMENT] Linia 274.
            "source_system",
# [AUTO-COMMENT] Linia 275.
            "tags",
# [AUTO-COMMENT] Linia 276.
            "sampling_interval_seconds",
# [AUTO-COMMENT] Linia 277.
            "measurement_summary",
# [AUTO-COMMENT] Linia 278.
        ],
# [AUTO-COMMENT] Linia 279.
        "numar_elemente": len(baza_masuratori),
# [AUTO-COMMENT] Linia 280.
        "elemente": lista_ordonata(),
# [AUTO-COMMENT] Linia 281.
    }
# [AUTO-COMMENT] Linia 282: linie goală.

# [AUTO-COMMENT] Linia 283: linie goală.

# [AUTO-COMMENT] Linia 284.
def preia_json(url, timeout_secunde=12, antete=None):
# [AUTO-COMMENT] Linia 285.
    antete_finale = {
# [AUTO-COMMENT] Linia 286.
        "User-Agent": USER_AGENT_EXTERNE,
# [AUTO-COMMENT] Linia 287.
        "Accept": "application/json",
# [AUTO-COMMENT] Linia 288.
    }
# [AUTO-COMMENT] Linia 289.
    if antete:
# [AUTO-COMMENT] Linia 290.
        antete_finale.update(antete)
# [AUTO-COMMENT] Linia 291: linie goală.

# [AUTO-COMMENT] Linia 292.
    cerere = Request(url, headers=antete_finale, method="GET")
# [AUTO-COMMENT] Linia 293.
    with urlopen(cerere, timeout=timeout_secunde) as raspuns:
# [AUTO-COMMENT] Linia 294.
        continut = raspuns.read().decode("utf-8")
# [AUTO-COMMENT] Linia 295.
    return json.loads(continut)
# [AUTO-COMMENT] Linia 296: linie goală.

# [AUTO-COMMENT] Linia 297: linie goală.

# [AUTO-COMMENT] Linia 298.
def geocode_oras_nominatim(oras, judet=None, tara="Romania"):
# [AUTO-COMMENT] Linia 299.
    bucati = [oras]
# [AUTO-COMMENT] Linia 300.
    if judet:
# [AUTO-COMMENT] Linia 301.
        bucati.append(judet)
# [AUTO-COMMENT] Linia 302.
    if tara:
# [AUTO-COMMENT] Linia 303.
        bucati.append(tara)
# [AUTO-COMMENT] Linia 304: linie goală.

# [AUTO-COMMENT] Linia 305.
    params = {
# [AUTO-COMMENT] Linia 306.
        "q": ", ".join(bucati),
# [AUTO-COMMENT] Linia 307.
        "format": "jsonv2",
# [AUTO-COMMENT] Linia 308.
        "limit": 1,
# [AUTO-COMMENT] Linia 309.
        "addressdetails": 1,
# [AUTO-COMMENT] Linia 310.
    }
# [AUTO-COMMENT] Linia 311.
    url = f"{NOMINATIM_SEARCH_URL}?{urlencode(params)}"
# [AUTO-COMMENT] Linia 312.
    rezultate = preia_json(url)
# [AUTO-COMMENT] Linia 313: linie goală.

# [AUTO-COMMENT] Linia 314.
    if not isinstance(rezultate, list) or not rezultate:
# [AUTO-COMMENT] Linia 315.
        raise ValueError("Nu am găsit coordonate pentru localitatea cerută.")
# [AUTO-COMMENT] Linia 316: linie goală.

# [AUTO-COMMENT] Linia 317.
    rezultat = rezultate[0]
# [AUTO-COMMENT] Linia 318.
    adresa = rezultat.get("address", {})
# [AUTO-COMMENT] Linia 319: linie goală.

# [AUTO-COMMENT] Linia 320.
    try:
# [AUTO-COMMENT] Linia 321.
        latitudine = float(rezultat["lat"])
# [AUTO-COMMENT] Linia 322.
        longitudine = float(rezultat["lon"])
# [AUTO-COMMENT] Linia 323.
    except (KeyError, TypeError, ValueError) as eroare:
# [AUTO-COMMENT] Linia 324.
        raise ValueError("Răspuns invalid de la Nominatim pentru coordonate.") from eroare
# [AUTO-COMMENT] Linia 325: linie goală.

# [AUTO-COMMENT] Linia 326.
    oras_rezolvat = (
# [AUTO-COMMENT] Linia 327.
        adresa.get("city")
# [AUTO-COMMENT] Linia 328.
        or adresa.get("town")
# [AUTO-COMMENT] Linia 329.
        or adresa.get("village")
# [AUTO-COMMENT] Linia 330.
        or adresa.get("municipality")
# [AUTO-COMMENT] Linia 331.
        or oras
# [AUTO-COMMENT] Linia 332.
    )
# [AUTO-COMMENT] Linia 333.
    judet_rezolvat = adresa.get("county") or adresa.get("state_district") or judet
# [AUTO-COMMENT] Linia 334.
    tara_rezolvata = adresa.get("country") or tara
# [AUTO-COMMENT] Linia 335: linie goală.

# [AUTO-COMMENT] Linia 336.
    return {
# [AUTO-COMMENT] Linia 337.
        "latitude": latitudine,
# [AUTO-COMMENT] Linia 338.
        "longitude": longitudine,
# [AUTO-COMMENT] Linia 339.
        "city": oras_rezolvat,
# [AUTO-COMMENT] Linia 340.
        "county": judet_rezolvat,
# [AUTO-COMMENT] Linia 341.
        "country": tara_rezolvata,
# [AUTO-COMMENT] Linia 342.
        "display_name": rezultat.get("display_name") or oras_rezolvat,
# [AUTO-COMMENT] Linia 343.
    }
# [AUTO-COMMENT] Linia 344: linie goală.

# [AUTO-COMMENT] Linia 345: linie goală.

# [AUTO-COMMENT] Linia 346.
def citeste_open_meteo(latitudine, longitudine):
# [AUTO-COMMENT] Linia 347.
    parametri_curenti = ",".join([
# [AUTO-COMMENT] Linia 348.
        "temperature_2m",
# [AUTO-COMMENT] Linia 349.
        "apparent_temperature",
# [AUTO-COMMENT] Linia 350.
        "relative_humidity_2m",
# [AUTO-COMMENT] Linia 351.
        "wind_speed_10m",
# [AUTO-COMMENT] Linia 352.
        "pressure_msl",
# [AUTO-COMMENT] Linia 353.
        "precipitation",
# [AUTO-COMMENT] Linia 354.
    ])
# [AUTO-COMMENT] Linia 355: linie goală.

# [AUTO-COMMENT] Linia 356.
    params = {
# [AUTO-COMMENT] Linia 357.
        "latitude": f"{latitudine:.6f}",
# [AUTO-COMMENT] Linia 358.
        "longitude": f"{longitudine:.6f}",
# [AUTO-COMMENT] Linia 359.
        "current": parametri_curenti,
# [AUTO-COMMENT] Linia 360.
        "timezone": "auto",
# [AUTO-COMMENT] Linia 361.
        "forecast_days": 1,
# [AUTO-COMMENT] Linia 362.
    }
# [AUTO-COMMENT] Linia 363: linie goală.

# [AUTO-COMMENT] Linia 364.
    url = f"{OPEN_METEO_FORECAST_URL}?{urlencode(params)}"
# [AUTO-COMMENT] Linia 365.
    raspuns = preia_json(url)
# [AUTO-COMMENT] Linia 366: linie goală.

# [AUTO-COMMENT] Linia 367.
    valori_curente = raspuns.get("current")
# [AUTO-COMMENT] Linia 368.
    unitati_curente = raspuns.get("current_units")
# [AUTO-COMMENT] Linia 369.
    if not isinstance(valori_curente, dict) or not isinstance(unitati_curente, dict):
# [AUTO-COMMENT] Linia 370.
        raise ValueError("Răspuns invalid de la Open-Meteo.")
# [AUTO-COMMENT] Linia 371: linie goală.

# [AUTO-COMMENT] Linia 372.
    return {
# [AUTO-COMMENT] Linia 373.
        "current": valori_curente,
# [AUTO-COMMENT] Linia 374.
        "current_units": unitati_curente,
# [AUTO-COMMENT] Linia 375.
        "timezone": raspuns.get("timezone"),
# [AUTO-COMMENT] Linia 376.
    }
# [AUTO-COMMENT] Linia 377: linie goală.

# [AUTO-COMMENT] Linia 378: linie goală.

# [AUTO-COMMENT] Linia 379.
def payloaduri_din_open_meteo(info_geo, meteo):
# [AUTO-COMMENT] Linia 380.
    valori_curente = meteo.get("current", {})
# [AUTO-COMMENT] Linia 381.
    unitati_curente = meteo.get("current_units", {})
# [AUTO-COMMENT] Linia 382.
    moment = valori_curente.get("time") or acum_utc_iso()
# [AUTO-COMMENT] Linia 383: linie goală.

# [AUTO-COMMENT] Linia 384.
    locatie_text = f"lat {info_geo['latitude']:.4f}, lon {info_geo['longitude']:.4f}"
# [AUTO-COMMENT] Linia 385.
    statie = info_geo.get("display_name") or info_geo.get("city") or "Open-Meteo"
# [AUTO-COMMENT] Linia 386.
    oras = info_geo.get("city")
# [AUTO-COMMENT] Linia 387.
    judet = info_geo.get("county")
# [AUTO-COMMENT] Linia 388: linie goală.

# [AUTO-COMMENT] Linia 389.
    baza_payload = {
# [AUTO-COMMENT] Linia 390.
        "statie": statie,
# [AUTO-COMMENT] Linia 391.
        "oras": oras,
# [AUTO-COMMENT] Linia 392.
        "judet": judet,
# [AUTO-COMMENT] Linia 393.
        "locatie": locatie_text,
# [AUTO-COMMENT] Linia 394.
        "platforma_sursa": "open-meteo",
# [AUTO-COMMENT] Linia 395.
        "descriere": f"Import automat din Open-Meteo pentru {oras or 'localitatea selectată'}.",
# [AUTO-COMMENT] Linia 396.
        "moment_inregistrare": moment,
# [AUTO-COMMENT] Linia 397.
    }
# [AUTO-COMMENT] Linia 398: linie goală.

# [AUTO-COMMENT] Linia 399.
    mapare_metrici = [
# [AUTO-COMMENT] Linia 400.
        {
# [AUTO-COMMENT] Linia 401.
            "cheie": "relative_humidity_2m",
# [AUTO-COMMENT] Linia 402.
            "indicator": "umiditate relativă",
# [AUTO-COMMENT] Linia 403.
            "unitate_implicita": "u.m.",
# [AUTO-COMMENT] Linia 404.
        },
# [AUTO-COMMENT] Linia 405.
        {
# [AUTO-COMMENT] Linia 406.
            "cheie": "wind_speed_10m",
# [AUTO-COMMENT] Linia 407.
            "indicator": "viteză vânt la 10m",
# [AUTO-COMMENT] Linia 408.
            "unitate_implicita": "u.m.",
# [AUTO-COMMENT] Linia 409.
        },
# [AUTO-COMMENT] Linia 410.
        {
# [AUTO-COMMENT] Linia 411.
            "cheie": "pressure_msl",
# [AUTO-COMMENT] Linia 412.
            "indicator": "presiune atmosferică la nivelul mării",
# [AUTO-COMMENT] Linia 413.
            "unitate_implicita": "u.m.",
# [AUTO-COMMENT] Linia 414.
        },
# [AUTO-COMMENT] Linia 415.
        {
# [AUTO-COMMENT] Linia 416.
            "cheie": "precipitation",
# [AUTO-COMMENT] Linia 417.
            "indicator": "precipitații curente",
# [AUTO-COMMENT] Linia 418.
            "unitate_implicita": "u.m.",
# [AUTO-COMMENT] Linia 419.
        },
# [AUTO-COMMENT] Linia 420.
        {
# [AUTO-COMMENT] Linia 421.
            "cheie": "temperature_2m",
# [AUTO-COMMENT] Linia 422.
            "indicator": "temperatură aer exterior",
# [AUTO-COMMENT] Linia 423.
            "unitate_implicita": "°C",
# [AUTO-COMMENT] Linia 424.
            "fara_valori_negative": True,
# [AUTO-COMMENT] Linia 425.
        },
# [AUTO-COMMENT] Linia 426.
    ]
# [AUTO-COMMENT] Linia 427: linie goală.

# [AUTO-COMMENT] Linia 428.
    payloaduri = []
# [AUTO-COMMENT] Linia 429.
    for metrica in mapare_metrici:
# [AUTO-COMMENT] Linia 430.
        cheie_api = metrica["cheie"]
# [AUTO-COMMENT] Linia 431.
        valoare = valori_curente.get(cheie_api)
# [AUTO-COMMENT] Linia 432.
        if valoare is None:
# [AUTO-COMMENT] Linia 433.
            continue
# [AUTO-COMMENT] Linia 434: linie goală.

# [AUTO-COMMENT] Linia 435.
        if metrica.get("fara_valori_negative"):
# [AUTO-COMMENT] Linia 436.
            if not isinstance(valoare, (int, float)) or valoare < 0:
# [AUTO-COMMENT] Linia 437.
                continue
# [AUTO-COMMENT] Linia 438: linie goală.

# [AUTO-COMMENT] Linia 439.
        unitate = unitati_curente.get(cheie_api) or metrica["unitate_implicita"]
# [AUTO-COMMENT] Linia 440.
        payload = {
# [AUTO-COMMENT] Linia 441.
            **baza_payload,
# [AUTO-COMMENT] Linia 442.
            "indicator": metrica["indicator"],
# [AUTO-COMMENT] Linia 443.
            "valoare": valoare,
# [AUTO-COMMENT] Linia 444.
            "unitate": unitate,
# [AUTO-COMMENT] Linia 445.
            "etichete": ["extern", "open-meteo", "nominatim", cheie_api],
# [AUTO-COMMENT] Linia 446.
        }
# [AUTO-COMMENT] Linia 447.
        payloaduri.append(payload)
# [AUTO-COMMENT] Linia 448: linie goală.

# [AUTO-COMMENT] Linia 449.
    return payloaduri
# [AUTO-COMMENT] Linia 450: linie goală.

# [AUTO-COMMENT] Linia 451: linie goală.

# [AUTO-COMMENT] Linia 452.
def text_normalizat(valoare):
# [AUTO-COMMENT] Linia 453.
    if not isinstance(valoare, str):
# [AUTO-COMMENT] Linia 454.
        return ""
# [AUTO-COMMENT] Linia 455: linie goală.

# [AUTO-COMMENT] Linia 456.
    baza = unicodedata.normalize("NFD", valoare.lower())
# [AUTO-COMMENT] Linia 457.
    fara_diacritice = "".join(caracter for caracter in baza if unicodedata.category(caracter) != "Mn")
# [AUTO-COMMENT] Linia 458.
    return " ".join(fara_diacritice.split())
# [AUTO-COMMENT] Linia 459: linie goală.

# [AUTO-COMMENT] Linia 460: linie goală.

# [AUTO-COMMENT] Linia 461.
def extrage_payload_obiect_din_request():
# [AUTO-COMMENT] Linia 462.
    payload = request.get_json(silent=True)
# [AUTO-COMMENT] Linia 463.
    if payload is None:
# [AUTO-COMMENT] Linia 464.
        return {}, None
# [AUTO-COMMENT] Linia 465.
    if not isinstance(payload, dict):
# [AUTO-COMMENT] Linia 466.
        return None, raspuns_eroare("Body trebuie să fie obiect JSON.", 400)
# [AUTO-COMMENT] Linia 467.
    return payload, None
# [AUTO-COMMENT] Linia 468: linie goală.

# [AUTO-COMMENT] Linia 469: linie goală.

# [AUTO-COMMENT] Linia 470.
def extrage_localizare(payload):
# [AUTO-COMMENT] Linia 471.
    oras = text_scurt(prima_valoare(payload, ["oras", "city"])) or "Iasi"
# [AUTO-COMMENT] Linia 472.
    judet = text_scurt(prima_valoare(payload, ["judet", "county", "state"]))
# [AUTO-COMMENT] Linia 473.
    tara = text_scurt(prima_valoare(payload, ["tara", "country"])) or "Romania"
# [AUTO-COMMENT] Linia 474.
    return oras, judet, tara
# [AUTO-COMMENT] Linia 475: linie goală.

# [AUTO-COMMENT] Linia 476: linie goală.

# [AUTO-COMMENT] Linia 477.
def pregateste_date_externe(payload):
# [AUTO-COMMENT] Linia 478.
    oras, judet, tara = extrage_localizare(payload)
# [AUTO-COMMENT] Linia 479.
    info_geo = geocode_oras_nominatim(oras, judet, tara)
# [AUTO-COMMENT] Linia 480.
    meteo = citeste_open_meteo(info_geo["latitude"], info_geo["longitude"])
# [AUTO-COMMENT] Linia 481.
    candidati = payloaduri_din_open_meteo(info_geo, meteo)
# [AUTO-COMMENT] Linia 482: linie goală.

# [AUTO-COMMENT] Linia 483.
    elemente_validate = []
# [AUTO-COMMENT] Linia 484.
    elemente_ignorate = []
# [AUTO-COMMENT] Linia 485.
    for candidat in candidati:
# [AUTO-COMMENT] Linia 486.
        element, mesaj = valideaza_payload(candidat)
# [AUTO-COMMENT] Linia 487.
        if mesaj:
# [AUTO-COMMENT] Linia 488.
            elemente_ignorate.append({
# [AUTO-COMMENT] Linia 489.
                "indicator": candidat.get("indicator"),
# [AUTO-COMMENT] Linia 490.
                "motiv": mesaj,
# [AUTO-COMMENT] Linia 491.
            })
# [AUTO-COMMENT] Linia 492.
            continue
# [AUTO-COMMENT] Linia 493: linie goală.

# [AUTO-COMMENT] Linia 494.
        elemente_validate.append(element)
# [AUTO-COMMENT] Linia 495: linie goală.

# [AUTO-COMMENT] Linia 496.
    return {
# [AUTO-COMMENT] Linia 497.
        "oras_cerut": oras,
# [AUTO-COMMENT] Linia 498.
        "info_geo": info_geo,
# [AUTO-COMMENT] Linia 499.
        "elemente_validate": elemente_validate,
# [AUTO-COMMENT] Linia 500.
        "elemente_ignorate": elemente_ignorate,
# [AUTO-COMMENT] Linia 501.
    }
# [AUTO-COMMENT] Linia 502: linie goală.

# [AUTO-COMMENT] Linia 503: linie goală.

# [AUTO-COMMENT] Linia 504.
def extrage_date_externe_din_request():
# [AUTO-COMMENT] Linia 505.
    payload, raspuns_eroare_payload = extrage_payload_obiect_din_request()
# [AUTO-COMMENT] Linia 506.
    if raspuns_eroare_payload:
# [AUTO-COMMENT] Linia 507.
        return None, None, raspuns_eroare_payload
# [AUTO-COMMENT] Linia 508: linie goală.

# [AUTO-COMMENT] Linia 509.
    try:
# [AUTO-COMMENT] Linia 510.
        date_externe = pregateste_date_externe(payload)
# [AUTO-COMMENT] Linia 511.
    except ValueError as eroare:
# [AUTO-COMMENT] Linia 512.
        return payload, None, raspuns_eroare(str(eroare), 400)
# [AUTO-COMMENT] Linia 513.
    except (HTTPError, URLError, TimeoutError, OSError):
# [AUTO-COMMENT] Linia 514.
        return payload, None, raspuns_eroare("Sursa externă este indisponibilă momentan.", 502)
# [AUTO-COMMENT] Linia 515: linie goală.

# [AUTO-COMMENT] Linia 516.
    return payload, date_externe, None
# [AUTO-COMMENT] Linia 517: linie goală.

# [AUTO-COMMENT] Linia 518: linie goală.

# [AUTO-COMMENT] Linia 519.
def selecteaza_element_extern(elemente_validate, payload_client):
# [AUTO-COMMENT] Linia 520.
    if not elemente_validate:
# [AUTO-COMMENT] Linia 521.
        return None
# [AUTO-COMMENT] Linia 522: linie goală.

# [AUTO-COMMENT] Linia 523.
    indicator_cerut = text_scurt(prima_valoare(payload_client, ["indicator", "metric", "parametru"]))
# [AUTO-COMMENT] Linia 524.
    if not indicator_cerut:
# [AUTO-COMMENT] Linia 525.
        return elemente_validate[0]
# [AUTO-COMMENT] Linia 526: linie goală.

# [AUTO-COMMENT] Linia 527.
    indicator_cerut_normalizat = text_normalizat(indicator_cerut)
# [AUTO-COMMENT] Linia 528: linie goală.

# [AUTO-COMMENT] Linia 529.
    for element in elemente_validate:
# [AUTO-COMMENT] Linia 530.
        metric = element.get("metric")
# [AUTO-COMMENT] Linia 531.
        metric_normalizat = text_normalizat(metric)
# [AUTO-COMMENT] Linia 532.
        if (
# [AUTO-COMMENT] Linia 533.
            metric_normalizat == indicator_cerut_normalizat
# [AUTO-COMMENT] Linia 534.
            or indicator_cerut_normalizat in metric_normalizat
# [AUTO-COMMENT] Linia 535.
            or metric_normalizat in indicator_cerut_normalizat
# [AUTO-COMMENT] Linia 536.
        ):
# [AUTO-COMMENT] Linia 537.
            return element
# [AUTO-COMMENT] Linia 538: linie goală.

# [AUTO-COMMENT] Linia 539.
    return elemente_validate[0]
# [AUTO-COMMENT] Linia 540: linie goală.

# [AUTO-COMMENT] Linia 541: linie goală.

# [AUTO-COMMENT] Linia 542.
def selectie_element_extern_sau_eroare(date_externe, payload_client, actiune, mesaj_eroare, extra=None):
# [AUTO-COMMENT] Linia 543.
    element = selecteaza_element_extern(date_externe["elemente_validate"], payload_client)
# [AUTO-COMMENT] Linia 544.
    if element is not None:
# [AUTO-COMMENT] Linia 545.
        return element, None
# [AUTO-COMMENT] Linia 546: linie goală.

# [AUTO-COMMENT] Linia 547.
    payload_eroare = {
# [AUTO-COMMENT] Linia 548.
        "eroare": mesaj_eroare,
# [AUTO-COMMENT] Linia 549.
        "actiune": actiune,
# [AUTO-COMMENT] Linia 550.
        "numar_ignorate": len(date_externe["elemente_ignorate"]),
# [AUTO-COMMENT] Linia 551.
        "elemente_ignorate": date_externe["elemente_ignorate"],
# [AUTO-COMMENT] Linia 552.
    }
# [AUTO-COMMENT] Linia 553.
    if extra:
# [AUTO-COMMENT] Linia 554.
        payload_eroare.update(extra)
# [AUTO-COMMENT] Linia 555: linie goală.

# [AUTO-COMMENT] Linia 556.
    return None, make_response(jsonify(payload_eroare), 502)
# [AUTO-COMMENT] Linia 557: linie goală.

# [AUTO-COMMENT] Linia 558: linie goală.

# [AUTO-COMMENT] Linia 559.
def gaseste_id_dupa_metric_si_oras(metric_cautat, oras_cautat):
# [AUTO-COMMENT] Linia 560.
    metric_normalizat = text_normalizat(metric_cautat)
# [AUTO-COMMENT] Linia 561.
    oras_normalizat = text_normalizat(oras_cautat)
# [AUTO-COMMENT] Linia 562: linie goală.

# [AUTO-COMMENT] Linia 563.
    if not metric_normalizat:
# [AUTO-COMMENT] Linia 564.
        return None
# [AUTO-COMMENT] Linia 565: linie goală.

# [AUTO-COMMENT] Linia 566.
    for item_id in sorted(baza_masuratori.keys()):
# [AUTO-COMMENT] Linia 567.
        element = baza_masuratori[item_id]
# [AUTO-COMMENT] Linia 568.
        metric_curent = text_normalizat(element.get("metric"))
# [AUTO-COMMENT] Linia 569.
        if metric_curent != metric_normalizat:
# [AUTO-COMMENT] Linia 570.
            continue
# [AUTO-COMMENT] Linia 571: linie goală.

# [AUTO-COMMENT] Linia 572.
        oras_curent = text_normalizat(element.get("city"))
# [AUTO-COMMENT] Linia 573.
        if oras_normalizat:
# [AUTO-COMMENT] Linia 574.
            if oras_curent == oras_normalizat:
# [AUTO-COMMENT] Linia 575.
                return item_id
# [AUTO-COMMENT] Linia 576.
        else:
# [AUTO-COMMENT] Linia 577.
            return item_id
# [AUTO-COMMENT] Linia 578: linie goală.

# [AUTO-COMMENT] Linia 579.
    return None
# [AUTO-COMMENT] Linia 580: linie goală.

# [AUTO-COMMENT] Linia 581: linie goală.

# [AUTO-COMMENT] Linia 582.
def salveaza_element(element, item_id=None):
# [AUTO-COMMENT] Linia 583.
    global urmatorul_id
# [AUTO-COMMENT] Linia 584: linie goală.

# [AUTO-COMMENT] Linia 585.
    if item_id is None:
# [AUTO-COMMENT] Linia 586.
        item_id = urmatorul_id
# [AUTO-COMMENT] Linia 587: linie goală.

# [AUTO-COMMENT] Linia 588.
    if item_id >= urmatorul_id:
# [AUTO-COMMENT] Linia 589.
        urmatorul_id = item_id + 1
# [AUTO-COMMENT] Linia 590: linie goală.

# [AUTO-COMMENT] Linia 591.
    creat = {"id": item_id, **element}
# [AUTO-COMMENT] Linia 592.
    baza_masuratori[item_id] = creat
# [AUTO-COMMENT] Linia 593.
    return creat
# [AUTO-COMMENT] Linia 594: linie goală.

# [AUTO-COMMENT] Linia 595: linie goală.

# [AUTO-COMMENT] Linia 596.
def aplica_patch_element(element_baza, campuri_noi):
# [AUTO-COMMENT] Linia 597.
    element_actualizat = {**element_baza}
# [AUTO-COMMENT] Linia 598.
    campuri_actualizate = []
# [AUTO-COMMENT] Linia 599: linie goală.

# [AUTO-COMMENT] Linia 600.
    for camp, valoare in campuri_noi.items():
# [AUTO-COMMENT] Linia 601.
        if element_actualizat.get(camp) != valoare:
# [AUTO-COMMENT] Linia 602.
            element_actualizat[camp] = valoare
# [AUTO-COMMENT] Linia 603.
            campuri_actualizate.append(camp)
# [AUTO-COMMENT] Linia 604: linie goală.

# [AUTO-COMMENT] Linia 605.
    return element_actualizat, sorted(campuri_actualizate)
# [AUTO-COMMENT] Linia 606: linie goală.

# [AUTO-COMMENT] Linia 607: linie goală.

# [AUTO-COMMENT] Linia 608.
def raspuns_creare(payload, item_id):
# [AUTO-COMMENT] Linia 609.
    raspuns = make_response(jsonify(payload), 201)
# [AUTO-COMMENT] Linia 610.
    raspuns.headers["Location"] = f"/masuratori/{item_id}"
# [AUTO-COMMENT] Linia 611.
    return raspuns
# [AUTO-COMMENT] Linia 612: linie goală.

# [AUTO-COMMENT] Linia 613: linie goală.

# [AUTO-COMMENT] Linia 614.
def extrage_element_extern_din_request(actiune, mesaj_eroare, extra=None, adauga_oras_cerut=False):
# [AUTO-COMMENT] Linia 615.
    payload, date_externe, raspuns_eroare_externa = extrage_date_externe_din_request()
# [AUTO-COMMENT] Linia 616.
    if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 617.
        return None, None, raspuns_eroare_externa
# [AUTO-COMMENT] Linia 618: linie goală.

# [AUTO-COMMENT] Linia 619.
    extra_final = dict(extra or {})
# [AUTO-COMMENT] Linia 620.
    if adauga_oras_cerut:
# [AUTO-COMMENT] Linia 621.
        extra_final["oras_cerut"] = date_externe["oras_cerut"]
# [AUTO-COMMENT] Linia 622: linie goală.

# [AUTO-COMMENT] Linia 623.
    element, raspuns_selectie = selectie_element_extern_sau_eroare(
# [AUTO-COMMENT] Linia 624.
        date_externe,
# [AUTO-COMMENT] Linia 625.
        payload,
# [AUTO-COMMENT] Linia 626.
        actiune,
# [AUTO-COMMENT] Linia 627.
        mesaj_eroare,
# [AUTO-COMMENT] Linia 628.
        extra=extra_final or None,
# [AUTO-COMMENT] Linia 629.
    )
# [AUTO-COMMENT] Linia 630.
    if raspuns_selectie:
# [AUTO-COMMENT] Linia 631.
        return None, None, raspuns_selectie
# [AUTO-COMMENT] Linia 632: linie goală.

# [AUTO-COMMENT] Linia 633.
    return element, date_externe, None
# [AUTO-COMMENT] Linia 634: linie goală.

# [AUTO-COMMENT] Linia 635: linie goală.

# [AUTO-COMMENT] Linia 636.
@app.route("/", methods=["GET"])
# [AUTO-COMMENT] Linia 637.
def acasa():
# [AUTO-COMMENT] Linia 638.
    return render_template("panou_masuratori.html")
# [AUTO-COMMENT] Linia 639: linie goală.

# [AUTO-COMMENT] Linia 640: linie goală.

# [AUTO-COMMENT] Linia 641.
@app.route("/measurements/trace/collection", methods=["POST"])
# [AUTO-COMMENT] Linia 642.
@app.route("/masuratori/trace/colectie", methods=["POST"])
# [AUTO-COMMENT] Linia 643.
def endpoint_trace_ui_colectie():
# [AUTO-COMMENT] Linia 644.
    return raspuns_trace("/masuratori", "colectie_masuratori", METODE_COLECTIE, simulat_ui=True)
# [AUTO-COMMENT] Linia 645: linie goală.

# [AUTO-COMMENT] Linia 646: linie goală.

# [AUTO-COMMENT] Linia 647.
@app.route("/measurements/trace/item/<int:item_id>", methods=["POST"])
# [AUTO-COMMENT] Linia 648.
@app.route("/masuratori/trace/element/<int:item_id>", methods=["POST"])
# [AUTO-COMMENT] Linia 649.
def endpoint_trace_ui_element(item_id):
# [AUTO-COMMENT] Linia 650.
    if item_id <= 0:
# [AUTO-COMMENT] Linia 651.
        return raspuns_eroare("item_id trebuie să fie pozitiv.", 400)
# [AUTO-COMMENT] Linia 652.
    return raspuns_trace(f"/masuratori/{item_id}", f"element_masurare_{item_id}", METODE_ELEMENT, simulat_ui=True)
# [AUTO-COMMENT] Linia 653: linie goală.

# [AUTO-COMMENT] Linia 654: linie goală.

# [AUTO-COMMENT] Linia 655.
@app.route("/measurements/external-preview", methods=["POST"])
# [AUTO-COMMENT] Linia 656.
@app.route("/masuratori/preview-extern", methods=["POST"])
# [AUTO-COMMENT] Linia 657.
def endpoint_preview_extern():
# [AUTO-COMMENT] Linia 658.
    _, date_externe, raspuns_eroare_externa = extrage_date_externe_din_request()
# [AUTO-COMMENT] Linia 659.
    if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 660.
        return raspuns_eroare_externa
# [AUTO-COMMENT] Linia 661: linie goală.

# [AUTO-COMMENT] Linia 662.
    elemente_preview = [
# [AUTO-COMMENT] Linia 663.
        {"id_preview": index, **element}
# [AUTO-COMMENT] Linia 664.
        for index, element in enumerate(date_externe["elemente_validate"], start=1)
# [AUTO-COMMENT] Linia 665.
    ]
# [AUTO-COMMENT] Linia 666: linie goală.

# [AUTO-COMMENT] Linia 667.
    return jsonify({
# [AUTO-COMMENT] Linia 668.
        "mesaj": "Preview date externe generat.",
# [AUTO-COMMENT] Linia 669.
        "actiune": "preview_date_externe",
# [AUTO-COMMENT] Linia 670.
        "sursa": "open-meteo",
# [AUTO-COMMENT] Linia 671.
        "oras_cerut": date_externe["oras_cerut"],
# [AUTO-COMMENT] Linia 672.
        "oras_rezolvat": date_externe["info_geo"].get("city"),
# [AUTO-COMMENT] Linia 673.
        "numar_preview": len(elemente_preview),
# [AUTO-COMMENT] Linia 674.
        "numar_ignorate": len(date_externe["elemente_ignorate"]),
# [AUTO-COMMENT] Linia 675.
        "elemente_preview": elemente_preview,
# [AUTO-COMMENT] Linia 676.
        "elemente_ignorate": date_externe["elemente_ignorate"],
# [AUTO-COMMENT] Linia 677.
    }), 200
# [AUTO-COMMENT] Linia 678: linie goală.

# [AUTO-COMMENT] Linia 679: linie goală.

# [AUTO-COMMENT] Linia 680.
@app.route("/measurements/synchronize", methods=["POST"])
# [AUTO-COMMENT] Linia 681.
@app.route("/masuratori/sincronizeaza", methods=["POST"])
# [AUTO-COMMENT] Linia 682.
def endpoint_sincronizare_externa():
# [AUTO-COMMENT] Linia 683.
    _, date_externe, raspuns_eroare_externa = extrage_date_externe_din_request()
# [AUTO-COMMENT] Linia 684.
    if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 685.
        return raspuns_eroare_externa
# [AUTO-COMMENT] Linia 686: linie goală.

# [AUTO-COMMENT] Linia 687.
    elemente_adaugate = [
# [AUTO-COMMENT] Linia 688.
        salveaza_element(element)
# [AUTO-COMMENT] Linia 689.
        for element in date_externe["elemente_validate"]
# [AUTO-COMMENT] Linia 690.
    ]
# [AUTO-COMMENT] Linia 691.
    elemente_ignorate = date_externe["elemente_ignorate"]
# [AUTO-COMMENT] Linia 692: linie goală.

# [AUTO-COMMENT] Linia 693.
    if not elemente_adaugate:
# [AUTO-COMMENT] Linia 694.
        return jsonify({
# [AUTO-COMMENT] Linia 695.
            "eroare": "Nu am putut importa măsurători valide din sursa externă.",
# [AUTO-COMMENT] Linia 696.
            "actiune": "sincronizeaza_din_open_meteo",
# [AUTO-COMMENT] Linia 697.
            "oras_cerut": date_externe["oras_cerut"],
# [AUTO-COMMENT] Linia 698.
            "numar_ignorate": len(elemente_ignorate),
# [AUTO-COMMENT] Linia 699.
            "elemente_ignorate": elemente_ignorate,
# [AUTO-COMMENT] Linia 700.
        }), 502
# [AUTO-COMMENT] Linia 701: linie goală.

# [AUTO-COMMENT] Linia 702.
    return jsonify({
# [AUTO-COMMENT] Linia 703.
        "mesaj": "Sincronizare externă finalizată.",
# [AUTO-COMMENT] Linia 704.
        "actiune": "sincronizeaza_din_open_meteo",
# [AUTO-COMMENT] Linia 705.
        "sursa": "open-meteo",
# [AUTO-COMMENT] Linia 706.
        "oras_cerut": date_externe["oras_cerut"],
# [AUTO-COMMENT] Linia 707.
        "oras_rezolvat": date_externe["info_geo"].get("city"),
# [AUTO-COMMENT] Linia 708.
        "numar_adaugate": len(elemente_adaugate),
# [AUTO-COMMENT] Linia 709.
        "numar_ignorate": len(elemente_ignorate),
# [AUTO-COMMENT] Linia 710.
        "ids_generate": [element["id"] for element in elemente_adaugate],
# [AUTO-COMMENT] Linia 711.
        "elemente_adaugate": elemente_adaugate,
# [AUTO-COMMENT] Linia 712.
        "elemente_ignorate": elemente_ignorate,
# [AUTO-COMMENT] Linia 713.
    }), 201
# [AUTO-COMMENT] Linia 714: linie goală.

# [AUTO-COMMENT] Linia 715: linie goală.

# [AUTO-COMMENT] Linia 716.
@app.route("/measurements", methods=METODE_COLECTIE)
# [AUTO-COMMENT] Linia 717.
@app.route("/masuratori", methods=METODE_COLECTIE)
# [AUTO-COMMENT] Linia 718.
def endpoint_colectie():
# [AUTO-COMMENT] Linia 719.
    global baza_masuratori
# [AUTO-COMMENT] Linia 720.
    global urmatorul_id
# [AUTO-COMMENT] Linia 721: linie goală.

# [AUTO-COMMENT] Linia 722.
    if request.method == "OPTIONS":
# [AUTO-COMMENT] Linia 723.
        return raspuns_options("/masuratori", METODE_COLECTIE, "colectie_masuratori")
# [AUTO-COMMENT] Linia 724: linie goală.

# [AUTO-COMMENT] Linia 725.
    if request.method == "TRACE":
# [AUTO-COMMENT] Linia 726.
        return raspuns_trace("/masuratori", "colectie_masuratori", METODE_COLECTIE)
# [AUTO-COMMENT] Linia 727: linie goală.

# [AUTO-COMMENT] Linia 728.
    if request.method == "HEAD":
# [AUTO-COMMENT] Linia 729.
        raspuns = make_response("", 200)
# [AUTO-COMMENT] Linia 730.
        raspuns.headers["Allow"] = header_allow_pentru(METODE_COLECTIE)
# [AUTO-COMMENT] Linia 731.
        raspuns.headers["X-Numar-Elemente"] = str(len(baza_masuratori))
# [AUTO-COMMENT] Linia 732.
        return raspuns
# [AUTO-COMMENT] Linia 733: linie goală.

# [AUTO-COMMENT] Linia 734.
    if request.method == "GET":
# [AUTO-COMMENT] Linia 735.
        return jsonify(raspuns_colectie()), 200
# [AUTO-COMMENT] Linia 736: linie goală.

# [AUTO-COMMENT] Linia 737.
    if request.method == "POST":
# [AUTO-COMMENT] Linia 738.
        element, date_externe, raspuns_eroare_externa = extrage_element_extern_din_request(
# [AUTO-COMMENT] Linia 739.
            "post_colectie_din_api_extern",
# [AUTO-COMMENT] Linia 740.
            "Nu am putut extrage niciun element valid din sursa externă.",
# [AUTO-COMMENT] Linia 741.
            adauga_oras_cerut=True,
# [AUTO-COMMENT] Linia 742.
        )
# [AUTO-COMMENT] Linia 743.
        if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 744.
            return raspuns_eroare_externa
# [AUTO-COMMENT] Linia 745: linie goală.

# [AUTO-COMMENT] Linia 746.
        creat = salveaza_element(element)
# [AUTO-COMMENT] Linia 747: linie goală.

# [AUTO-COMMENT] Linia 748.
        return raspuns_creare(
# [AUTO-COMMENT] Linia 749.
            {
# [AUTO-COMMENT] Linia 750.
                **creat,
# [AUTO-COMMENT] Linia 751.
                "actiune": "post_colectie_din_api_extern",
# [AUTO-COMMENT] Linia 752.
                "sursa": "open-meteo",
# [AUTO-COMMENT] Linia 753.
                "oras_rezolvat": date_externe["info_geo"].get("city"),
# [AUTO-COMMENT] Linia 754.
            },
# [AUTO-COMMENT] Linia 755.
            creat["id"],
# [AUTO-COMMENT] Linia 756.
        )
# [AUTO-COMMENT] Linia 757: linie goală.

# [AUTO-COMMENT] Linia 758.
    if request.method == "PUT":
# [AUTO-COMMENT] Linia 759.
        _, date_externe, raspuns_eroare_externa = extrage_date_externe_din_request()
# [AUTO-COMMENT] Linia 760.
        if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 761.
            return raspuns_eroare_externa
# [AUTO-COMMENT] Linia 762: linie goală.

# [AUTO-COMMENT] Linia 763.
        if not date_externe["elemente_validate"]:
# [AUTO-COMMENT] Linia 764.
            return jsonify({
# [AUTO-COMMENT] Linia 765.
                "eroare": "Nu am putut importa măsurători valide pentru înlocuirea colecției.",
# [AUTO-COMMENT] Linia 766.
                "actiune": "put_colectie_din_api_extern",
# [AUTO-COMMENT] Linia 767.
                "oras_cerut": date_externe["oras_cerut"],
# [AUTO-COMMENT] Linia 768.
                "numar_ignorate": len(date_externe["elemente_ignorate"]),
# [AUTO-COMMENT] Linia 769.
                "elemente_ignorate": date_externe["elemente_ignorate"],
# [AUTO-COMMENT] Linia 770.
            }), 502
# [AUTO-COMMENT] Linia 771: linie goală.

# [AUTO-COMMENT] Linia 772.
        date_noi = {
# [AUTO-COMMENT] Linia 773.
            index: {"id": index, **element}
# [AUTO-COMMENT] Linia 774.
            for index, element in enumerate(date_externe["elemente_validate"], start=1)
# [AUTO-COMMENT] Linia 775.
        }
# [AUTO-COMMENT] Linia 776: linie goală.

# [AUTO-COMMENT] Linia 777.
        baza_masuratori = date_noi
# [AUTO-COMMENT] Linia 778.
        urmatorul_id = len(baza_masuratori) + 1
# [AUTO-COMMENT] Linia 779: linie goală.

# [AUTO-COMMENT] Linia 780.
        raspuns = raspuns_colectie()
# [AUTO-COMMENT] Linia 781.
        raspuns["actiune"] = "put_colectie_din_api_extern"
# [AUTO-COMMENT] Linia 782.
        raspuns["sursa"] = "open-meteo"
# [AUTO-COMMENT] Linia 783.
        raspuns["oras_rezolvat"] = date_externe["info_geo"].get("city")
# [AUTO-COMMENT] Linia 784.
        raspuns["numar_ignorate"] = len(date_externe["elemente_ignorate"])
# [AUTO-COMMENT] Linia 785.
        raspuns["elemente_ignorate"] = date_externe["elemente_ignorate"]
# [AUTO-COMMENT] Linia 786.
        return jsonify(raspuns), 200
# [AUTO-COMMENT] Linia 787: linie goală.

# [AUTO-COMMENT] Linia 788.
    if request.method == "PATCH":
# [AUTO-COMMENT] Linia 789.
        element_nou, date_externe, raspuns_eroare_externa = extrage_element_extern_din_request(
# [AUTO-COMMENT] Linia 790.
            "patch_colectie_din_api_extern",
# [AUTO-COMMENT] Linia 791.
            "Nu am putut extrage niciun element valid pentru patch din sursa externă.",
# [AUTO-COMMENT] Linia 792.
            adauga_oras_cerut=True,
# [AUTO-COMMENT] Linia 793.
        )
# [AUTO-COMMENT] Linia 794.
        if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 795.
            return raspuns_eroare_externa
# [AUTO-COMMENT] Linia 796.
        id_tinta = gaseste_id_dupa_metric_si_oras(element_nou.get("metric"), element_nou.get("city"))
# [AUTO-COMMENT] Linia 797: linie goală.

# [AUTO-COMMENT] Linia 798.
        status_patch = "adaugat"
# [AUTO-COMMENT] Linia 799.
        cod_status = 201
# [AUTO-COMMENT] Linia 800.
        campuri_actualizate = []
# [AUTO-COMMENT] Linia 801: linie goală.

# [AUTO-COMMENT] Linia 802.
        if id_tinta is None:
# [AUTO-COMMENT] Linia 803.
            element_final = salveaza_element(element_nou)
# [AUTO-COMMENT] Linia 804.
            id_tinta = element_final["id"]
# [AUTO-COMMENT] Linia 805.
            campuri_actualizate = sorted(list(element_nou.keys()))
# [AUTO-COMMENT] Linia 806.
        else:
# [AUTO-COMMENT] Linia 807.
            element_actualizat, campuri_actualizate = aplica_patch_element(baza_masuratori[id_tinta], element_nou)
# [AUTO-COMMENT] Linia 808.
            baza_masuratori[id_tinta] = element_actualizat
# [AUTO-COMMENT] Linia 809.
            status_patch = "actualizat"
# [AUTO-COMMENT] Linia 810.
            cod_status = 200
# [AUTO-COMMENT] Linia 811: linie goală.

# [AUTO-COMMENT] Linia 812.
        element_final = baza_masuratori[id_tinta]
# [AUTO-COMMENT] Linia 813.
        payload_raspuns = {
# [AUTO-COMMENT] Linia 814.
            "actiune": "patch_colectie_din_api_extern",
# [AUTO-COMMENT] Linia 815.
            "status_patch": status_patch,
# [AUTO-COMMENT] Linia 816.
            "id_tinta": id_tinta,
# [AUTO-COMMENT] Linia 817.
            "campuri_actualizate": campuri_actualizate,
# [AUTO-COMMENT] Linia 818.
            "sursa": "open-meteo",
# [AUTO-COMMENT] Linia 819.
            "oras_rezolvat": date_externe["info_geo"].get("city"),
# [AUTO-COMMENT] Linia 820.
            "element": element_final,
# [AUTO-COMMENT] Linia 821.
        }
# [AUTO-COMMENT] Linia 822: linie goală.

# [AUTO-COMMENT] Linia 823.
        if cod_status == 201:
# [AUTO-COMMENT] Linia 824.
            return raspuns_creare(payload_raspuns, id_tinta)
# [AUTO-COMMENT] Linia 825: linie goală.

# [AUTO-COMMENT] Linia 826.
        return jsonify(payload_raspuns), 200
# [AUTO-COMMENT] Linia 827: linie goală.

# [AUTO-COMMENT] Linia 828.
    if request.method == "DELETE":
# [AUTO-COMMENT] Linia 829.
        sterse = len(baza_masuratori)
# [AUTO-COMMENT] Linia 830.
        baza_masuratori = {}
# [AUTO-COMMENT] Linia 831.
        urmatorul_id = 1
# [AUTO-COMMENT] Linia 832.
        return jsonify({
# [AUTO-COMMENT] Linia 833.
            "mesaj": "Toate măsurătorile din colecție au fost șterse.",
# [AUTO-COMMENT] Linia 834.
            "numar_sterse": sterse,
# [AUTO-COMMENT] Linia 835.
            "colectie_curenta": [],
# [AUTO-COMMENT] Linia 836.
        }), 200
# [AUTO-COMMENT] Linia 837: linie goală.

# [AUTO-COMMENT] Linia 838.
    return raspuns_eroare("Metodă HTTP neacceptată pe colecție.", 405)
# [AUTO-COMMENT] Linia 839: linie goală.

# [AUTO-COMMENT] Linia 840: linie goală.

# [AUTO-COMMENT] Linia 841.
@app.route("/measurements/<int:item_id>", methods=METODE_ELEMENT)
# [AUTO-COMMENT] Linia 842.
@app.route("/masuratori/<int:item_id>", methods=METODE_ELEMENT)
# [AUTO-COMMENT] Linia 843.
def endpoint_element(item_id):
# [AUTO-COMMENT] Linia 844.
    if item_id <= 0:
# [AUTO-COMMENT] Linia 845.
        return raspuns_eroare("item_id trebuie să fie pozitiv.", 400)
# [AUTO-COMMENT] Linia 846: linie goală.

# [AUTO-COMMENT] Linia 847.
    if request.method == "OPTIONS":
# [AUTO-COMMENT] Linia 848.
        return raspuns_options(f"/masuratori/{item_id}", METODE_ELEMENT, f"element_masurare_{item_id}")
# [AUTO-COMMENT] Linia 849: linie goală.

# [AUTO-COMMENT] Linia 850.
    if request.method == "TRACE":
# [AUTO-COMMENT] Linia 851.
        return raspuns_trace(f"/masuratori/{item_id}", f"element_masurare_{item_id}", METODE_ELEMENT)
# [AUTO-COMMENT] Linia 852: linie goală.

# [AUTO-COMMENT] Linia 853.
    if request.method == "HEAD":
# [AUTO-COMMENT] Linia 854.
        element = baza_masuratori.get(item_id)
# [AUTO-COMMENT] Linia 855.
        exista = element is not None
# [AUTO-COMMENT] Linia 856.
        cod = 200 if exista else 404
# [AUTO-COMMENT] Linia 857: linie goală.

# [AUTO-COMMENT] Linia 858.
        raspuns = make_response("", cod)
# [AUTO-COMMENT] Linia 859.
        raspuns.headers["Allow"] = header_allow_pentru(METODE_ELEMENT)
# [AUTO-COMMENT] Linia 860.
        raspuns.headers["X-Item-Id"] = str(item_id)
# [AUTO-COMMENT] Linia 861.
        raspuns.headers["X-Item-Exists"] = "true" if exista else "false"
# [AUTO-COMMENT] Linia 862.
        if exista:
# [AUTO-COMMENT] Linia 863.
            raspuns.headers["X-Item-Metric"] = str(element.get("metric", ""))
# [AUTO-COMMENT] Linia 864.
        return raspuns
# [AUTO-COMMENT] Linia 865: linie goală.

# [AUTO-COMMENT] Linia 866.
    if request.method == "GET":
# [AUTO-COMMENT] Linia 867.
        element = baza_masuratori.get(item_id)
# [AUTO-COMMENT] Linia 868.
        if element is None:
# [AUTO-COMMENT] Linia 869.
            return raspuns_eroare("Elementul cerut nu există.", 404)
# [AUTO-COMMENT] Linia 870.
        return jsonify(element), 200
# [AUTO-COMMENT] Linia 871: linie goală.

# [AUTO-COMMENT] Linia 872.
    if request.method == "POST":
# [AUTO-COMMENT] Linia 873.
        if item_id in baza_masuratori:
# [AUTO-COMMENT] Linia 874.
            return raspuns_eroare("Elementul există deja pentru acest id.", 409)
# [AUTO-COMMENT] Linia 875: linie goală.

# [AUTO-COMMENT] Linia 876.
        element, _, raspuns_eroare_externa = extrage_element_extern_din_request(
# [AUTO-COMMENT] Linia 877.
            "post_element_din_api_extern",
# [AUTO-COMMENT] Linia 878.
            "Nu am putut extrage un element valid pentru acest id din sursa externă.",
# [AUTO-COMMENT] Linia 879.
            extra={"id_cerut": item_id},
# [AUTO-COMMENT] Linia 880.
        )
# [AUTO-COMMENT] Linia 881.
        if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 882.
            return raspuns_eroare_externa
# [AUTO-COMMENT] Linia 883: linie goală.

# [AUTO-COMMENT] Linia 884.
        creat = salveaza_element(element, item_id=item_id)
# [AUTO-COMMENT] Linia 885: linie goală.

# [AUTO-COMMENT] Linia 886.
        return raspuns_creare(creat, item_id)
# [AUTO-COMMENT] Linia 887: linie goală.

# [AUTO-COMMENT] Linia 888.
    if request.method == "PUT":
# [AUTO-COMMENT] Linia 889.
        element, _, raspuns_eroare_externa = extrage_element_extern_din_request(
# [AUTO-COMMENT] Linia 890.
            "put_element_din_api_extern",
# [AUTO-COMMENT] Linia 891.
            "Nu am putut extrage un element valid pentru actualizare din sursa externă.",
# [AUTO-COMMENT] Linia 892.
            extra={"id_cerut": item_id},
# [AUTO-COMMENT] Linia 893.
        )
# [AUTO-COMMENT] Linia 894.
        if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 895.
            return raspuns_eroare_externa
# [AUTO-COMMENT] Linia 896: linie goală.

# [AUTO-COMMENT] Linia 897.
        exista = item_id in baza_masuratori
# [AUTO-COMMENT] Linia 898.
        actualizat = salveaza_element(element, item_id=item_id)
# [AUTO-COMMENT] Linia 899: linie goală.

# [AUTO-COMMENT] Linia 900.
        if exista:
# [AUTO-COMMENT] Linia 901.
            return jsonify(actualizat), 200
# [AUTO-COMMENT] Linia 902: linie goală.

# [AUTO-COMMENT] Linia 903.
        return raspuns_creare(actualizat, item_id)
# [AUTO-COMMENT] Linia 904: linie goală.

# [AUTO-COMMENT] Linia 905.
    if request.method == "PATCH":
# [AUTO-COMMENT] Linia 906.
        element_existent = baza_masuratori.get(item_id)
# [AUTO-COMMENT] Linia 907.
        if element_existent is None:
# [AUTO-COMMENT] Linia 908.
            return raspuns_eroare("Elementul cerut nu există pentru patch.", 404)
# [AUTO-COMMENT] Linia 909: linie goală.

# [AUTO-COMMENT] Linia 910.
        element_nou, date_externe, raspuns_eroare_externa = extrage_element_extern_din_request(
# [AUTO-COMMENT] Linia 911.
            "patch_element_din_api_extern",
# [AUTO-COMMENT] Linia 912.
            "Nu am putut extrage un element valid pentru patch din sursa externă.",
# [AUTO-COMMENT] Linia 913.
            extra={"id_cerut": item_id},
# [AUTO-COMMENT] Linia 914.
        )
# [AUTO-COMMENT] Linia 915.
        if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 916.
            return raspuns_eroare_externa
# [AUTO-COMMENT] Linia 917.
        element_actualizat, campuri_actualizate = aplica_patch_element(element_existent, element_nou)
# [AUTO-COMMENT] Linia 918: linie goală.

# [AUTO-COMMENT] Linia 919.
        baza_masuratori[item_id] = element_actualizat
# [AUTO-COMMENT] Linia 920: linie goală.

# [AUTO-COMMENT] Linia 921.
        return jsonify({
# [AUTO-COMMENT] Linia 922.
            "actiune": "patch_element_din_api_extern",
# [AUTO-COMMENT] Linia 923.
            "id_actualizat": item_id,
# [AUTO-COMMENT] Linia 924.
            "campuri_actualizate": campuri_actualizate,
# [AUTO-COMMENT] Linia 925.
            "sursa": "open-meteo",
# [AUTO-COMMENT] Linia 926.
            "oras_rezolvat": date_externe["info_geo"].get("city"),
# [AUTO-COMMENT] Linia 927.
            "element": element_actualizat,
# [AUTO-COMMENT] Linia 928.
        }), 200
# [AUTO-COMMENT] Linia 929: linie goală.

# [AUTO-COMMENT] Linia 930.
    if request.method == "DELETE":
# [AUTO-COMMENT] Linia 931.
        element = baza_masuratori.get(item_id)
# [AUTO-COMMENT] Linia 932.
        if element is None:
# [AUTO-COMMENT] Linia 933.
            return raspuns_eroare("Elementul cerut nu există.", 404)
# [AUTO-COMMENT] Linia 934: linie goală.

# [AUTO-COMMENT] Linia 935.
        del baza_masuratori[item_id]
# [AUTO-COMMENT] Linia 936.
        return jsonify({
# [AUTO-COMMENT] Linia 937.
            "mesaj": "Elementul selectat a fost șters.",
# [AUTO-COMMENT] Linia 938.
            "id_sters": item_id,
# [AUTO-COMMENT] Linia 939.
        }), 200
# [AUTO-COMMENT] Linia 940: linie goală.

# [AUTO-COMMENT] Linia 941.
    return raspuns_eroare("Metodă HTTP neacceptată pe element.", 405)
# [AUTO-COMMENT] Linia 942: linie goală.

# [AUTO-COMMENT] Linia 943: linie goală.

# [AUTO-COMMENT] Linia 944.
if __name__ == "__main__":
# [AUTO-COMMENT] Linia 945.
    app.run(host="127.0.0.1", port=5000, debug=True)
