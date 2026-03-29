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
# [AUTO-COMMENT] Linia 21.
CORS_ALLOW_HEADERS = "Content-Type, Authorization, Accept"
# [AUTO-COMMENT] Linia 22: linie goală.

# [AUTO-COMMENT] Linia 23: linie goală.

# [AUTO-COMMENT] Linia 24.
def acum_utc_iso():
# [AUTO-COMMENT] Linia 25.
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
# [AUTO-COMMENT] Linia 26: linie goală.

# [AUTO-COMMENT] Linia 27: linie goală.

# [AUTO-COMMENT] Linia 28.
def lista_ordonata():
# [AUTO-COMMENT] Linia 29.
    return [baza_masuratori[item_id] for item_id in sorted(baza_masuratori.keys())]
# [AUTO-COMMENT] Linia 30: linie goală.

# [AUTO-COMMENT] Linia 31: linie goală.

# [AUTO-COMMENT] Linia 32.
def prima_valoare(payload, chei):
# [AUTO-COMMENT] Linia 33.
    for cheie in chei:
# [AUTO-COMMENT] Linia 34.
        if cheie in payload:
# [AUTO-COMMENT] Linia 35.
            return payload.get(cheie)
# [AUTO-COMMENT] Linia 36.
    return None
# [AUTO-COMMENT] Linia 37: linie goală.

# [AUTO-COMMENT] Linia 38: linie goală.

# [AUTO-COMMENT] Linia 39.
def valoare_numerica(brut):
# [AUTO-COMMENT] Linia 40.
    if isinstance(brut, bool):
# [AUTO-COMMENT] Linia 41.
        return None
# [AUTO-COMMENT] Linia 42.
    if isinstance(brut, (int, float)):
# [AUTO-COMMENT] Linia 43.
        valoare = float(brut)
# [AUTO-COMMENT] Linia 44.
    elif isinstance(brut, str):
# [AUTO-COMMENT] Linia 45.
        text = brut.strip()
# [AUTO-COMMENT] Linia 46.
        if not text:
# [AUTO-COMMENT] Linia 47.
            return None
# [AUTO-COMMENT] Linia 48.
        try:
# [AUTO-COMMENT] Linia 49.
            valoare = float(text)
# [AUTO-COMMENT] Linia 50.
        except ValueError:
# [AUTO-COMMENT] Linia 51.
            return None
# [AUTO-COMMENT] Linia 52.
    else:
# [AUTO-COMMENT] Linia 53.
        return None
# [AUTO-COMMENT] Linia 54: linie goală.

# [AUTO-COMMENT] Linia 55.
    if valoare < 0:
# [AUTO-COMMENT] Linia 56.
        return None
# [AUTO-COMMENT] Linia 57: linie goală.

# [AUTO-COMMENT] Linia 58.
    if valoare.is_integer():
# [AUTO-COMMENT] Linia 59.
        return int(valoare)
# [AUTO-COMMENT] Linia 60.
    return valoare
# [AUTO-COMMENT] Linia 61: linie goală.

# [AUTO-COMMENT] Linia 62: linie goală.

# [AUTO-COMMENT] Linia 63.
def text_scurt(valoare):
# [AUTO-COMMENT] Linia 64.
    if valoare is None:
# [AUTO-COMMENT] Linia 65.
        return None
# [AUTO-COMMENT] Linia 66.
    if not isinstance(valoare, str):
# [AUTO-COMMENT] Linia 67.
        return None
# [AUTO-COMMENT] Linia 68.
    curat = valoare.strip()
# [AUTO-COMMENT] Linia 69.
    return curat if curat else None
# [AUTO-COMMENT] Linia 70: linie goală.

# [AUTO-COMMENT] Linia 71: linie goală.

# [AUTO-COMMENT] Linia 72.
def valideaza_etichete(etichete):
# [AUTO-COMMENT] Linia 73.
    if etichete is None:
# [AUTO-COMMENT] Linia 74.
        return None, None
# [AUTO-COMMENT] Linia 75.
    if not isinstance(etichete, list):
# [AUTO-COMMENT] Linia 76.
        return None, "etichete/tags trebuie să fie listă de texte."
# [AUTO-COMMENT] Linia 77: linie goală.

# [AUTO-COMMENT] Linia 78.
    rezultat = []
# [AUTO-COMMENT] Linia 79.
    for element in etichete:
# [AUTO-COMMENT] Linia 80.
        if not isinstance(element, str) or not element.strip():
# [AUTO-COMMENT] Linia 81.
            return None, "fiecare etichetă trebuie să fie text nevid."
# [AUTO-COMMENT] Linia 82.
        rezultat.append(element.strip())
# [AUTO-COMMENT] Linia 83.
    return rezultat, None
# [AUTO-COMMENT] Linia 84: linie goală.

# [AUTO-COMMENT] Linia 85: linie goală.

# [AUTO-COMMENT] Linia 86.
def valideaza_interval(interval):
# [AUTO-COMMENT] Linia 87.
    if interval is None:
# [AUTO-COMMENT] Linia 88.
        return None, None
# [AUTO-COMMENT] Linia 89.
    numeric = valoare_numerica(interval)
# [AUTO-COMMENT] Linia 90.
    if numeric is None or numeric == 0:
# [AUTO-COMMENT] Linia 91.
        return None, "sampling_interval_seconds/frecventa_secunde trebuie să fie numeric și > 0."
# [AUTO-COMMENT] Linia 92.
    return numeric, None
# [AUTO-COMMENT] Linia 93: linie goală.

# [AUTO-COMMENT] Linia 94: linie goală.

# [AUTO-COMMENT] Linia 95.
def valideaza_payload(payload):
# [AUTO-COMMENT] Linia 96.
    if not isinstance(payload, dict):
# [AUTO-COMMENT] Linia 97.
        return None, "Body trebuie să fie obiect JSON."
# [AUTO-COMMENT] Linia 98: linie goală.

# [AUTO-COMMENT] Linia 99.
    statie = text_scurt(prima_valoare(payload, ["station", "statie", "punct_masurare"]))
# [AUTO-COMMENT] Linia 100.
    indicator = text_scurt(prima_valoare(payload, ["metric", "indicator", "parametru"]))
# [AUTO-COMMENT] Linia 101.
    unitate = text_scurt(prima_valoare(payload, ["unit", "unitate", "unitate_masura"]))
# [AUTO-COMMENT] Linia 102.
    valoare = valoare_numerica(prima_valoare(payload, ["value", "valoare", "valoare_masurata"]))
# [AUTO-COMMENT] Linia 103: linie goală.

# [AUTO-COMMENT] Linia 104.
    if not statie:
# [AUTO-COMMENT] Linia 105.
        return None, "Lipsește station/statie/punct_masurare."
# [AUTO-COMMENT] Linia 106.
    if not indicator:
# [AUTO-COMMENT] Linia 107.
        return None, "Lipsește metric/indicator/parametru."
# [AUTO-COMMENT] Linia 108.
    if not unitate:
# [AUTO-COMMENT] Linia 109.
        return None, "Lipsește unit/unitate/unitate_masura."
# [AUTO-COMMENT] Linia 110.
    if valoare is None:
# [AUTO-COMMENT] Linia 111.
        return None, "value/valoare trebuie să fie numeric și >= 0."
# [AUTO-COMMENT] Linia 112: linie goală.

# [AUTO-COMMENT] Linia 113.
    moment = prima_valoare(payload, ["timestamp", "moment", "moment_inregistrare"])
# [AUTO-COMMENT] Linia 114.
    if moment is None:
# [AUTO-COMMENT] Linia 115.
        moment = acum_utc_iso()
# [AUTO-COMMENT] Linia 116.
    else:
# [AUTO-COMMENT] Linia 117.
        moment = text_scurt(moment)
# [AUTO-COMMENT] Linia 118.
        if not moment:
# [AUTO-COMMENT] Linia 119.
            return None, "timestamp/moment trebuie să fie text nevid dacă este trimis."
# [AUTO-COMMENT] Linia 120: linie goală.

# [AUTO-COMMENT] Linia 121.
    campuri_text_optionale = {
# [AUTO-COMMENT] Linia 122.
        "location": ["location", "locatie", "pozitie_instalare"],
# [AUTO-COMMENT] Linia 123.
        "description": ["description", "descriere", "detalii"],
# [AUTO-COMMENT] Linia 124.
        "category": ["category", "categorie", "domeniu"],
# [AUTO-COMMENT] Linia 125.
        "sensor_name": ["sensor_name", "nume_senzor"],
# [AUTO-COMMENT] Linia 126.
        "sensor_model": ["sensor_model", "model_senzor"],
# [AUTO-COMMENT] Linia 127.
        "sensor_manufacturer": ["sensor_manufacturer", "producator_senzor"],
# [AUTO-COMMENT] Linia 128.
        "operator_name": ["operator_name", "responsabil", "persoana_responsabila"],
# [AUTO-COMMENT] Linia 129.
        "city": ["city", "oras"],
# [AUTO-COMMENT] Linia 130.
        "county": ["county", "judet"],
# [AUTO-COMMENT] Linia 131.
        "source_system": ["source_system", "sursa_date", "platforma_sursa"],
# [AUTO-COMMENT] Linia 132.
    }
# [AUTO-COMMENT] Linia 133: linie goală.

# [AUTO-COMMENT] Linia 134.
    rezultat = {
# [AUTO-COMMENT] Linia 135.
        "station": statie,
# [AUTO-COMMENT] Linia 136.
        "metric": indicator,
# [AUTO-COMMENT] Linia 137.
        "value": valoare,
# [AUTO-COMMENT] Linia 138.
        "unit": unitate,
# [AUTO-COMMENT] Linia 139.
        "timestamp": moment,
# [AUTO-COMMENT] Linia 140.
    }
# [AUTO-COMMENT] Linia 141: linie goală.

# [AUTO-COMMENT] Linia 142.
    for camp, aliasuri in campuri_text_optionale.items():
# [AUTO-COMMENT] Linia 143.
        valoare_text = text_scurt(prima_valoare(payload, aliasuri))
# [AUTO-COMMENT] Linia 144.
        if valoare_text:
# [AUTO-COMMENT] Linia 145.
            rezultat[camp] = valoare_text
# [AUTO-COMMENT] Linia 146: linie goală.

# [AUTO-COMMENT] Linia 147.
    etichete, eroare_etichete = valideaza_etichete(prima_valoare(payload, ["tags", "etichete", "cuvinte_cheie"]))
# [AUTO-COMMENT] Linia 148.
    if eroare_etichete:
# [AUTO-COMMENT] Linia 149.
        return None, eroare_etichete
# [AUTO-COMMENT] Linia 150.
    if etichete:
# [AUTO-COMMENT] Linia 151.
        rezultat["tags"] = etichete
# [AUTO-COMMENT] Linia 152: linie goală.

# [AUTO-COMMENT] Linia 153.
    interval, eroare_interval = valideaza_interval(prima_valoare(payload, ["sampling_interval_seconds", "frecventa_secunde", "interval_esantionare"]))
# [AUTO-COMMENT] Linia 154.
    if eroare_interval:
# [AUTO-COMMENT] Linia 155.
        return None, eroare_interval
# [AUTO-COMMENT] Linia 156.
    if interval is not None:
# [AUTO-COMMENT] Linia 157.
        rezultat["sampling_interval_seconds"] = interval
# [AUTO-COMMENT] Linia 158: linie goală.

# [AUTO-COMMENT] Linia 159.
    rezumat = f"{indicator} măsurat la {statie}: {valoare} {unitate}"
# [AUTO-COMMENT] Linia 160.
    rezultat["measurement_summary"] = rezumat
# [AUTO-COMMENT] Linia 161: linie goală.

# [AUTO-COMMENT] Linia 162.
    return rezultat, None
# [AUTO-COMMENT] Linia 163: linie goală.

# [AUTO-COMMENT] Linia 164: linie goală.

# [AUTO-COMMENT] Linia 165.
def raspuns_eroare(mesaj, cod=400):
# [AUTO-COMMENT] Linia 166.
    return jsonify({"eroare": mesaj}), cod
# [AUTO-COMMENT] Linia 167: linie goală.

# [AUTO-COMMENT] Linia 168: linie goală.

# [AUTO-COMMENT] Linia 169.
def metode_cu_head_unice(metode):
# [AUTO-COMMENT] Linia 170.
    return list(dict.fromkeys([*metode, "HEAD"]))
# [AUTO-COMMENT] Linia 171: linie goală.

# [AUTO-COMMENT] Linia 172: linie goală.

# [AUTO-COMMENT] Linia 173.
def header_allow_pentru(metode):
# [AUTO-COMMENT] Linia 174.
    return ", ".join(metode_cu_head_unice(metode))
# [AUTO-COMMENT] Linia 175: linie goală.

# [AUTO-COMMENT] Linia 176: linie goală.

# [AUTO-COMMENT] Linia 177.
@app.after_request
# [AUTO-COMMENT] Linia 178.
def adauga_antete_cors(raspuns):
# [AUTO-COMMENT] Linia 179.
    raspuns.headers["Access-Control-Allow-Origin"] = "*"
# [AUTO-COMMENT] Linia 180.
    raspuns.headers["Access-Control-Allow-Methods"] = header_allow_pentru(METODE_HTTP)
# [AUTO-COMMENT] Linia 181.
    raspuns.headers["Access-Control-Allow-Headers"] = CORS_ALLOW_HEADERS
# [AUTO-COMMENT] Linia 182.
    return raspuns
# [AUTO-COMMENT] Linia 183: linie goală.

# [AUTO-COMMENT] Linia 184: linie goală.

# [AUTO-COMMENT] Linia 185.
def raspuns_options(ruta, metode, descriere_resursa):
# [AUTO-COMMENT] Linia 186.
    metode_permise = metode_cu_head_unice(metode)
# [AUTO-COMMENT] Linia 187.
    payload = {
# [AUTO-COMMENT] Linia 188.
        "tip_raspuns": "options",
# [AUTO-COMMENT] Linia 189.
        "ruta": ruta,
# [AUTO-COMMENT] Linia 190.
        "resursa": descriere_resursa,
# [AUTO-COMMENT] Linia 191.
        "metode_permise": metode_permise,
# [AUTO-COMMENT] Linia 192.
        "nota": "Metoda OPTIONS descrie capabilitățile resursei.",
# [AUTO-COMMENT] Linia 193.
    }
# [AUTO-COMMENT] Linia 194: linie goală.

# [AUTO-COMMENT] Linia 195.
    raspuns = make_response(jsonify(payload), 200)
# [AUTO-COMMENT] Linia 196.
    allow = header_allow_pentru(metode)
# [AUTO-COMMENT] Linia 197.
    raspuns.headers["Allow"] = allow
# [AUTO-COMMENT] Linia 198.
    raspuns.headers["Access-Control-Allow-Methods"] = allow
# [AUTO-COMMENT] Linia 199.
    raspuns.headers["Access-Control-Allow-Headers"] = "Content-Type"
# [AUTO-COMMENT] Linia 200.
    return raspuns
# [AUTO-COMMENT] Linia 201: linie goală.

# [AUTO-COMMENT] Linia 202: linie goală.

# [AUTO-COMMENT] Linia 203.
def construieste_payload_trace(ruta, descriere_resursa, simulat_ui=False):
# [AUTO-COMMENT] Linia 204.
    payload = {
# [AUTO-COMMENT] Linia 205.
        "tip_raspuns": "trace",
# [AUTO-COMMENT] Linia 206.
        "ruta": ruta,
# [AUTO-COMMENT] Linia 207.
        "resursa": descriere_resursa,
# [AUTO-COMMENT] Linia 208.
        "metoda_reflectata": "TRACE",
# [AUTO-COMMENT] Linia 209.
        "metoda_transport": request.method,
# [AUTO-COMMENT] Linia 210.
        "query_params": request.args.to_dict(flat=True),
# [AUTO-COMMENT] Linia 211.
        "headers_primite": dict(request.headers),
# [AUTO-COMMENT] Linia 212.
        "body_primit": request.get_data(as_text=True),
# [AUTO-COMMENT] Linia 213.
        "simulare_ui": simulat_ui,
# [AUTO-COMMENT] Linia 214.
    }
# [AUTO-COMMENT] Linia 215: linie goală.

# [AUTO-COMMENT] Linia 216.
    if simulat_ui:
# [AUTO-COMMENT] Linia 217.
        payload["nota"] = "Browserul blochează metoda TRACE direct; răspunsul este obținut prin endpoint helper POST."
# [AUTO-COMMENT] Linia 218: linie goală.

# [AUTO-COMMENT] Linia 219.
    return payload
# [AUTO-COMMENT] Linia 220: linie goală.

# [AUTO-COMMENT] Linia 221: linie goală.

# [AUTO-COMMENT] Linia 222.
def raspuns_trace(ruta, descriere_resursa, metode, simulat_ui=False):
# [AUTO-COMMENT] Linia 223.
    payload = construieste_payload_trace(ruta, descriere_resursa, simulat_ui=simulat_ui)
# [AUTO-COMMENT] Linia 224.
    raspuns = make_response(jsonify(payload), 200)
# [AUTO-COMMENT] Linia 225.
    raspuns.headers["Allow"] = header_allow_pentru(metode)
# [AUTO-COMMENT] Linia 226.
    return raspuns
# [AUTO-COMMENT] Linia 227: linie goală.

# [AUTO-COMMENT] Linia 228: linie goală.

# [AUTO-COMMENT] Linia 229.
def raspuns_colectie():
# [AUTO-COMMENT] Linia 230.
    return {
# [AUTO-COMMENT] Linia 231.
        "tip_raspuns": "colectie_masuratori",
# [AUTO-COMMENT] Linia 232.
        "descriere": "Colecție completă de măsurători, cu metadate și elemente.",
# [AUTO-COMMENT] Linia 233.
        "operatii_colectie": METODE_COLECTIE,
# [AUTO-COMMENT] Linia 234.
        "operatii_element": METODE_ELEMENT,
# [AUTO-COMMENT] Linia 235.
        "operatii_ui": METODE_COLECTIE,
# [AUTO-COMMENT] Linia 236.
        "etichete_ui": {
# [AUTO-COMMENT] Linia 237.
            "GET": "preia / vezi",
# [AUTO-COMMENT] Linia 238.
            "HEAD": "verifică antete / existență",
# [AUTO-COMMENT] Linia 239.
            "POST": "adaugă / creează",
# [AUTO-COMMENT] Linia 240.
            "PUT": "înlocuiește / salvează",
# [AUTO-COMMENT] Linia 241.
            "PATCH": "actualizare parțială",
# [AUTO-COMMENT] Linia 242.
            "DELETE": "șterge",
# [AUTO-COMMENT] Linia 243.
            "OPTIONS": "capacități / metode permise",
# [AUTO-COMMENT] Linia 244.
            "TRACE": "diagnostic trasabilitate",
# [AUTO-COMMENT] Linia 245.
        },
# [AUTO-COMMENT] Linia 246.
        "nota_operatii_ui": "În browser, TRACE este disponibil prin butoane helper care trimit POST către endpointuri dedicate.",
# [AUTO-COMMENT] Linia 247.
        "regula_date": "Operațiile de scriere folosesc exclusiv date externe (Nominatim + Open-Meteo).",
# [AUTO-COMMENT] Linia 248.
        "actiuni_semantice_colectie": [
# [AUTO-COMMENT] Linia 249.
            {"nume": "preia_masuratori", "metoda": "GET", "ruta": "/masuratori"},
# [AUTO-COMMENT] Linia 250.
            {"nume": "verifica_antete_colectie", "metoda": "HEAD", "ruta": "/masuratori"},
# [AUTO-COMMENT] Linia 251.
            {"nume": "adauga_masurare", "metoda": "POST", "ruta": "/masuratori"},
# [AUTO-COMMENT] Linia 252.
            {"nume": "inlocuieste_colectia", "metoda": "PUT", "ruta": "/masuratori"},
# [AUTO-COMMENT] Linia 253.
            {"nume": "actualizeaza_partial_colectia", "metoda": "PATCH", "ruta": "/masuratori"},
# [AUTO-COMMENT] Linia 254.
            {"nume": "goleste_colectia", "metoda": "DELETE", "ruta": "/masuratori"},
# [AUTO-COMMENT] Linia 255.
            {"nume": "capabilitati_colectie", "metoda": "OPTIONS", "ruta": "/masuratori"},
# [AUTO-COMMENT] Linia 256.
            {"nume": "trace_colectie", "metoda": "TRACE", "ruta": "/masuratori"},
# [AUTO-COMMENT] Linia 257.
            {"nume": "trace_colectie_ui", "metoda": "POST", "ruta": "/masuratori/trace/colectie"},
# [AUTO-COMMENT] Linia 258.
            {"nume": "preview_date_externe", "metoda": "POST", "ruta": "/masuratori/preview-extern"},
# [AUTO-COMMENT] Linia 259.
            {"nume": "sincronizeaza_din_open_meteo", "metoda": "POST", "ruta": "/masuratori/sincronizeaza"},
# [AUTO-COMMENT] Linia 260.
        ],
# [AUTO-COMMENT] Linia 261.
        "actiuni_semantice_element": [
# [AUTO-COMMENT] Linia 262.
            {"nume": "vezi_masurare", "metoda": "GET", "ruta": "/masuratori/<id>"},
# [AUTO-COMMENT] Linia 263.
            {"nume": "verifica_antete_element", "metoda": "HEAD", "ruta": "/masuratori/<id>"},
# [AUTO-COMMENT] Linia 264.
            {"nume": "creeaza_masurare_la_id", "metoda": "POST", "ruta": "/masuratori/<id>"},
# [AUTO-COMMENT] Linia 265.
            {"nume": "salveaza_masurare", "metoda": "PUT", "ruta": "/masuratori/<id>"},
# [AUTO-COMMENT] Linia 266.
            {"nume": "actualizeaza_partial_element", "metoda": "PATCH", "ruta": "/masuratori/<id>"},
# [AUTO-COMMENT] Linia 267.
            {"nume": "sterge_masurare", "metoda": "DELETE", "ruta": "/masuratori/<id>"},
# [AUTO-COMMENT] Linia 268.
            {"nume": "capabilitati_element", "metoda": "OPTIONS", "ruta": "/masuratori/<id>"},
# [AUTO-COMMENT] Linia 269.
            {"nume": "trace_element", "metoda": "TRACE", "ruta": "/masuratori/<id>"},
# [AUTO-COMMENT] Linia 270.
            {"nume": "trace_element_ui", "metoda": "POST", "ruta": "/masuratori/trace/element/<id>"},
# [AUTO-COMMENT] Linia 271.
        ],
# [AUTO-COMMENT] Linia 272.
        "campuri_principale": ["id", "station", "metric", "value", "unit", "timestamp"],
# [AUTO-COMMENT] Linia 273.
        "campuri_optionale": [
# [AUTO-COMMENT] Linia 274.
            "location",
# [AUTO-COMMENT] Linia 275.
            "description",
# [AUTO-COMMENT] Linia 276.
            "category",
# [AUTO-COMMENT] Linia 277.
            "sensor_name",
# [AUTO-COMMENT] Linia 278.
            "sensor_model",
# [AUTO-COMMENT] Linia 279.
            "sensor_manufacturer",
# [AUTO-COMMENT] Linia 280.
            "operator_name",
# [AUTO-COMMENT] Linia 281.
            "city",
# [AUTO-COMMENT] Linia 282.
            "county",
# [AUTO-COMMENT] Linia 283.
            "source_system",
# [AUTO-COMMENT] Linia 284.
            "tags",
# [AUTO-COMMENT] Linia 285.
            "sampling_interval_seconds",
# [AUTO-COMMENT] Linia 286.
            "measurement_summary",
# [AUTO-COMMENT] Linia 287.
        ],
# [AUTO-COMMENT] Linia 288.
        "numar_elemente": len(baza_masuratori),
# [AUTO-COMMENT] Linia 289.
        "elemente": lista_ordonata(),
# [AUTO-COMMENT] Linia 290.
    }
# [AUTO-COMMENT] Linia 291: linie goală.

# [AUTO-COMMENT] Linia 292: linie goală.

# [AUTO-COMMENT] Linia 293.
def preia_json(url, timeout_secunde=12, antete=None):
# [AUTO-COMMENT] Linia 294.
    antete_finale = {
# [AUTO-COMMENT] Linia 295.
        "User-Agent": USER_AGENT_EXTERNE,
# [AUTO-COMMENT] Linia 296.
        "Accept": "application/json",
# [AUTO-COMMENT] Linia 297.
    }
# [AUTO-COMMENT] Linia 298.
    if antete:
# [AUTO-COMMENT] Linia 299.
        antete_finale.update(antete)
# [AUTO-COMMENT] Linia 300: linie goală.

# [AUTO-COMMENT] Linia 301.
    cerere = Request(url, headers=antete_finale, method="GET")
# [AUTO-COMMENT] Linia 302.
    with urlopen(cerere, timeout=timeout_secunde) as raspuns:
# [AUTO-COMMENT] Linia 303.
        continut = raspuns.read().decode("utf-8")
# [AUTO-COMMENT] Linia 304.
    return json.loads(continut)
# [AUTO-COMMENT] Linia 305: linie goală.

# [AUTO-COMMENT] Linia 306: linie goală.

# [AUTO-COMMENT] Linia 307.
def geocode_oras_nominatim(oras, judet=None, tara="Romania"):
# [AUTO-COMMENT] Linia 308.
    bucati = [oras]
# [AUTO-COMMENT] Linia 309.
    if judet:
# [AUTO-COMMENT] Linia 310.
        bucati.append(judet)
# [AUTO-COMMENT] Linia 311.
    if tara:
# [AUTO-COMMENT] Linia 312.
        bucati.append(tara)
# [AUTO-COMMENT] Linia 313: linie goală.

# [AUTO-COMMENT] Linia 314.
    params = {
# [AUTO-COMMENT] Linia 315.
        "q": ", ".join(bucati),
# [AUTO-COMMENT] Linia 316.
        "format": "jsonv2",
# [AUTO-COMMENT] Linia 317.
        "limit": 1,
# [AUTO-COMMENT] Linia 318.
        "addressdetails": 1,
# [AUTO-COMMENT] Linia 319.
    }
# [AUTO-COMMENT] Linia 320.
    url = f"{NOMINATIM_SEARCH_URL}?{urlencode(params)}"
# [AUTO-COMMENT] Linia 321.
    rezultate = preia_json(url)
# [AUTO-COMMENT] Linia 322: linie goală.

# [AUTO-COMMENT] Linia 323.
    if not isinstance(rezultate, list) or not rezultate:
# [AUTO-COMMENT] Linia 324.
        raise ValueError("Nu am găsit coordonate pentru localitatea cerută.")
# [AUTO-COMMENT] Linia 325: linie goală.

# [AUTO-COMMENT] Linia 326.
    rezultat = rezultate[0]
# [AUTO-COMMENT] Linia 327.
    adresa = rezultat.get("address", {})
# [AUTO-COMMENT] Linia 328: linie goală.

# [AUTO-COMMENT] Linia 329.
    try:
# [AUTO-COMMENT] Linia 330.
        latitudine = float(rezultat["lat"])
# [AUTO-COMMENT] Linia 331.
        longitudine = float(rezultat["lon"])
# [AUTO-COMMENT] Linia 332.
    except (KeyError, TypeError, ValueError) as eroare:
# [AUTO-COMMENT] Linia 333.
        raise ValueError("Răspuns invalid de la Nominatim pentru coordonate.") from eroare
# [AUTO-COMMENT] Linia 334: linie goală.

# [AUTO-COMMENT] Linia 335.
    oras_rezolvat = (
# [AUTO-COMMENT] Linia 336.
        adresa.get("city")
# [AUTO-COMMENT] Linia 337.
        or adresa.get("town")
# [AUTO-COMMENT] Linia 338.
        or adresa.get("village")
# [AUTO-COMMENT] Linia 339.
        or adresa.get("municipality")
# [AUTO-COMMENT] Linia 340.
        or oras
# [AUTO-COMMENT] Linia 341.
    )
# [AUTO-COMMENT] Linia 342.
    judet_rezolvat = adresa.get("county") or adresa.get("state_district") or judet
# [AUTO-COMMENT] Linia 343.
    tara_rezolvata = adresa.get("country") or tara
# [AUTO-COMMENT] Linia 344: linie goală.

# [AUTO-COMMENT] Linia 345.
    return {
# [AUTO-COMMENT] Linia 346.
        "latitude": latitudine,
# [AUTO-COMMENT] Linia 347.
        "longitude": longitudine,
# [AUTO-COMMENT] Linia 348.
        "city": oras_rezolvat,
# [AUTO-COMMENT] Linia 349.
        "county": judet_rezolvat,
# [AUTO-COMMENT] Linia 350.
        "country": tara_rezolvata,
# [AUTO-COMMENT] Linia 351.
        "display_name": rezultat.get("display_name") or oras_rezolvat,
# [AUTO-COMMENT] Linia 352.
    }
# [AUTO-COMMENT] Linia 353: linie goală.

# [AUTO-COMMENT] Linia 354: linie goală.

# [AUTO-COMMENT] Linia 355.
def citeste_open_meteo(latitudine, longitudine):
# [AUTO-COMMENT] Linia 356.
    parametri_curenti = ",".join([
# [AUTO-COMMENT] Linia 357.
        "temperature_2m",
# [AUTO-COMMENT] Linia 358.
        "apparent_temperature",
# [AUTO-COMMENT] Linia 359.
        "relative_humidity_2m",
# [AUTO-COMMENT] Linia 360.
        "wind_speed_10m",
# [AUTO-COMMENT] Linia 361.
        "pressure_msl",
# [AUTO-COMMENT] Linia 362.
        "precipitation",
# [AUTO-COMMENT] Linia 363.
    ])
# [AUTO-COMMENT] Linia 364: linie goală.

# [AUTO-COMMENT] Linia 365.
    params = {
# [AUTO-COMMENT] Linia 366.
        "latitude": f"{latitudine:.6f}",
# [AUTO-COMMENT] Linia 367.
        "longitude": f"{longitudine:.6f}",
# [AUTO-COMMENT] Linia 368.
        "current": parametri_curenti,
# [AUTO-COMMENT] Linia 369.
        "timezone": "auto",
# [AUTO-COMMENT] Linia 370.
        "forecast_days": 1,
# [AUTO-COMMENT] Linia 371.
    }
# [AUTO-COMMENT] Linia 372: linie goală.

# [AUTO-COMMENT] Linia 373.
    url = f"{OPEN_METEO_FORECAST_URL}?{urlencode(params)}"
# [AUTO-COMMENT] Linia 374.
    raspuns = preia_json(url)
# [AUTO-COMMENT] Linia 375: linie goală.

# [AUTO-COMMENT] Linia 376.
    valori_curente = raspuns.get("current")
# [AUTO-COMMENT] Linia 377.
    unitati_curente = raspuns.get("current_units")
# [AUTO-COMMENT] Linia 378.
    if not isinstance(valori_curente, dict) or not isinstance(unitati_curente, dict):
# [AUTO-COMMENT] Linia 379.
        raise ValueError("Răspuns invalid de la Open-Meteo.")
# [AUTO-COMMENT] Linia 380: linie goală.

# [AUTO-COMMENT] Linia 381.
    return {
# [AUTO-COMMENT] Linia 382.
        "current": valori_curente,
# [AUTO-COMMENT] Linia 383.
        "current_units": unitati_curente,
# [AUTO-COMMENT] Linia 384.
        "timezone": raspuns.get("timezone"),
# [AUTO-COMMENT] Linia 385.
    }
# [AUTO-COMMENT] Linia 386: linie goală.

# [AUTO-COMMENT] Linia 387: linie goală.

# [AUTO-COMMENT] Linia 388.
def payloaduri_din_open_meteo(info_geo, meteo):
# [AUTO-COMMENT] Linia 389.
    valori_curente = meteo.get("current", {})
# [AUTO-COMMENT] Linia 390.
    unitati_curente = meteo.get("current_units", {})
# [AUTO-COMMENT] Linia 391.
    moment = valori_curente.get("time") or acum_utc_iso()
# [AUTO-COMMENT] Linia 392: linie goală.

# [AUTO-COMMENT] Linia 393.
    locatie_text = f"lat {info_geo['latitude']:.4f}, lon {info_geo['longitude']:.4f}"
# [AUTO-COMMENT] Linia 394.
    statie = info_geo.get("display_name") or info_geo.get("city") or "Open-Meteo"
# [AUTO-COMMENT] Linia 395.
    oras = info_geo.get("city")
# [AUTO-COMMENT] Linia 396.
    judet = info_geo.get("county")
# [AUTO-COMMENT] Linia 397: linie goală.

# [AUTO-COMMENT] Linia 398.
    baza_payload = {
# [AUTO-COMMENT] Linia 399.
        "statie": statie,
# [AUTO-COMMENT] Linia 400.
        "oras": oras,
# [AUTO-COMMENT] Linia 401.
        "judet": judet,
# [AUTO-COMMENT] Linia 402.
        "locatie": locatie_text,
# [AUTO-COMMENT] Linia 403.
        "platforma_sursa": "open-meteo",
# [AUTO-COMMENT] Linia 404.
        "descriere": f"Import automat din Open-Meteo pentru {oras or 'localitatea selectată'}.",
# [AUTO-COMMENT] Linia 405.
        "moment_inregistrare": moment,
# [AUTO-COMMENT] Linia 406.
    }
# [AUTO-COMMENT] Linia 407: linie goală.

# [AUTO-COMMENT] Linia 408.
    mapare_metrici = [
# [AUTO-COMMENT] Linia 409.
        {
# [AUTO-COMMENT] Linia 410.
            "cheie": "relative_humidity_2m",
# [AUTO-COMMENT] Linia 411.
            "indicator": "umiditate relativă",
# [AUTO-COMMENT] Linia 412.
            "unitate_implicita": "u.m.",
# [AUTO-COMMENT] Linia 413.
        },
# [AUTO-COMMENT] Linia 414.
        {
# [AUTO-COMMENT] Linia 415.
            "cheie": "wind_speed_10m",
# [AUTO-COMMENT] Linia 416.
            "indicator": "viteză vânt la 10m",
# [AUTO-COMMENT] Linia 417.
            "unitate_implicita": "u.m.",
# [AUTO-COMMENT] Linia 418.
        },
# [AUTO-COMMENT] Linia 419.
        {
# [AUTO-COMMENT] Linia 420.
            "cheie": "pressure_msl",
# [AUTO-COMMENT] Linia 421.
            "indicator": "presiune atmosferică la nivelul mării",
# [AUTO-COMMENT] Linia 422.
            "unitate_implicita": "u.m.",
# [AUTO-COMMENT] Linia 423.
        },
# [AUTO-COMMENT] Linia 424.
        {
# [AUTO-COMMENT] Linia 425.
            "cheie": "precipitation",
# [AUTO-COMMENT] Linia 426.
            "indicator": "precipitații curente",
# [AUTO-COMMENT] Linia 427.
            "unitate_implicita": "u.m.",
# [AUTO-COMMENT] Linia 428.
        },
# [AUTO-COMMENT] Linia 429.
        {
# [AUTO-COMMENT] Linia 430.
            "cheie": "temperature_2m",
# [AUTO-COMMENT] Linia 431.
            "indicator": "temperatură aer exterior",
# [AUTO-COMMENT] Linia 432.
            "unitate_implicita": "°C",
# [AUTO-COMMENT] Linia 433.
            "fara_valori_negative": True,
# [AUTO-COMMENT] Linia 434.
        },
# [AUTO-COMMENT] Linia 435.
    ]
# [AUTO-COMMENT] Linia 436: linie goală.

# [AUTO-COMMENT] Linia 437.
    payloaduri = []
# [AUTO-COMMENT] Linia 438.
    for metrica in mapare_metrici:
# [AUTO-COMMENT] Linia 439.
        cheie_api = metrica["cheie"]
# [AUTO-COMMENT] Linia 440.
        valoare = valori_curente.get(cheie_api)
# [AUTO-COMMENT] Linia 441.
        if valoare is None:
# [AUTO-COMMENT] Linia 442.
            continue
# [AUTO-COMMENT] Linia 443: linie goală.

# [AUTO-COMMENT] Linia 444.
        if metrica.get("fara_valori_negative"):
# [AUTO-COMMENT] Linia 445.
            if not isinstance(valoare, (int, float)) or valoare < 0:
# [AUTO-COMMENT] Linia 446.
                continue
# [AUTO-COMMENT] Linia 447: linie goală.

# [AUTO-COMMENT] Linia 448.
        unitate = unitati_curente.get(cheie_api) or metrica["unitate_implicita"]
# [AUTO-COMMENT] Linia 449.
        payload = {
# [AUTO-COMMENT] Linia 450.
            **baza_payload,
# [AUTO-COMMENT] Linia 451.
            "indicator": metrica["indicator"],
# [AUTO-COMMENT] Linia 452.
            "valoare": valoare,
# [AUTO-COMMENT] Linia 453.
            "unitate": unitate,
# [AUTO-COMMENT] Linia 454.
            "etichete": ["extern", "open-meteo", "nominatim", cheie_api],
# [AUTO-COMMENT] Linia 455.
        }
# [AUTO-COMMENT] Linia 456.
        payloaduri.append(payload)
# [AUTO-COMMENT] Linia 457: linie goală.

# [AUTO-COMMENT] Linia 458.
    return payloaduri
# [AUTO-COMMENT] Linia 459: linie goală.

# [AUTO-COMMENT] Linia 460: linie goală.

# [AUTO-COMMENT] Linia 461.
def text_normalizat(valoare):
# [AUTO-COMMENT] Linia 462.
    if not isinstance(valoare, str):
# [AUTO-COMMENT] Linia 463.
        return ""
# [AUTO-COMMENT] Linia 464: linie goală.

# [AUTO-COMMENT] Linia 465.
    baza = unicodedata.normalize("NFD", valoare.lower())
# [AUTO-COMMENT] Linia 466.
    fara_diacritice = "".join(caracter for caracter in baza if unicodedata.category(caracter) != "Mn")
# [AUTO-COMMENT] Linia 467.
    return " ".join(fara_diacritice.split())
# [AUTO-COMMENT] Linia 468: linie goală.

# [AUTO-COMMENT] Linia 469: linie goală.

# [AUTO-COMMENT] Linia 470.
def extrage_payload_obiect_din_request():
# [AUTO-COMMENT] Linia 471.
    payload = request.get_json(silent=True)
# [AUTO-COMMENT] Linia 472.
    if payload is None:
# [AUTO-COMMENT] Linia 473.
        return {}, None
# [AUTO-COMMENT] Linia 474.
    if not isinstance(payload, dict):
# [AUTO-COMMENT] Linia 475.
        return None, raspuns_eroare("Body trebuie să fie obiect JSON.", 400)
# [AUTO-COMMENT] Linia 476.
    return payload, None
# [AUTO-COMMENT] Linia 477: linie goală.

# [AUTO-COMMENT] Linia 478: linie goală.

# [AUTO-COMMENT] Linia 479.
def extrage_localizare(payload):
# [AUTO-COMMENT] Linia 480.
    oras = text_scurt(prima_valoare(payload, ["oras", "city"])) or "Iasi"
# [AUTO-COMMENT] Linia 481.
    judet = text_scurt(prima_valoare(payload, ["judet", "county", "state"]))
# [AUTO-COMMENT] Linia 482.
    tara = text_scurt(prima_valoare(payload, ["tara", "country"])) or "Romania"
# [AUTO-COMMENT] Linia 483.
    return oras, judet, tara
# [AUTO-COMMENT] Linia 484: linie goală.

# [AUTO-COMMENT] Linia 485: linie goală.

# [AUTO-COMMENT] Linia 486.
def pregateste_date_externe(payload):
# [AUTO-COMMENT] Linia 487.
    oras, judet, tara = extrage_localizare(payload)
# [AUTO-COMMENT] Linia 488.
    info_geo = geocode_oras_nominatim(oras, judet, tara)
# [AUTO-COMMENT] Linia 489.
    meteo = citeste_open_meteo(info_geo["latitude"], info_geo["longitude"])
# [AUTO-COMMENT] Linia 490.
    candidati = payloaduri_din_open_meteo(info_geo, meteo)
# [AUTO-COMMENT] Linia 491: linie goală.

# [AUTO-COMMENT] Linia 492.
    elemente_validate = []
# [AUTO-COMMENT] Linia 493.
    elemente_ignorate = []
# [AUTO-COMMENT] Linia 494.
    for candidat in candidati:
# [AUTO-COMMENT] Linia 495.
        element, mesaj = valideaza_payload(candidat)
# [AUTO-COMMENT] Linia 496.
        if mesaj:
# [AUTO-COMMENT] Linia 497.
            elemente_ignorate.append({
# [AUTO-COMMENT] Linia 498.
                "indicator": candidat.get("indicator"),
# [AUTO-COMMENT] Linia 499.
                "motiv": mesaj,
# [AUTO-COMMENT] Linia 500.
            })
# [AUTO-COMMENT] Linia 501.
            continue
# [AUTO-COMMENT] Linia 502: linie goală.

# [AUTO-COMMENT] Linia 503.
        elemente_validate.append(element)
# [AUTO-COMMENT] Linia 504: linie goală.

# [AUTO-COMMENT] Linia 505.
    return {
# [AUTO-COMMENT] Linia 506.
        "oras_cerut": oras,
# [AUTO-COMMENT] Linia 507.
        "info_geo": info_geo,
# [AUTO-COMMENT] Linia 508.
        "elemente_validate": elemente_validate,
# [AUTO-COMMENT] Linia 509.
        "elemente_ignorate": elemente_ignorate,
# [AUTO-COMMENT] Linia 510.
    }
# [AUTO-COMMENT] Linia 511: linie goală.

# [AUTO-COMMENT] Linia 512: linie goală.

# [AUTO-COMMENT] Linia 513.
def extrage_date_externe_din_request():
# [AUTO-COMMENT] Linia 514.
    payload, raspuns_eroare_payload = extrage_payload_obiect_din_request()
# [AUTO-COMMENT] Linia 515.
    if raspuns_eroare_payload:
# [AUTO-COMMENT] Linia 516.
        return None, None, raspuns_eroare_payload
# [AUTO-COMMENT] Linia 517: linie goală.

# [AUTO-COMMENT] Linia 518.
    try:
# [AUTO-COMMENT] Linia 519.
        date_externe = pregateste_date_externe(payload)
# [AUTO-COMMENT] Linia 520.
    except ValueError as eroare:
# [AUTO-COMMENT] Linia 521.
        return payload, None, raspuns_eroare(str(eroare), 400)
# [AUTO-COMMENT] Linia 522.
    except (HTTPError, URLError, TimeoutError, OSError):
# [AUTO-COMMENT] Linia 523.
        return payload, None, raspuns_eroare("Sursa externă este indisponibilă momentan.", 502)
# [AUTO-COMMENT] Linia 524: linie goală.

# [AUTO-COMMENT] Linia 525.
    return payload, date_externe, None
# [AUTO-COMMENT] Linia 526: linie goală.

# [AUTO-COMMENT] Linia 527: linie goală.

# [AUTO-COMMENT] Linia 528.
def selecteaza_element_extern(elemente_validate, payload_client):
# [AUTO-COMMENT] Linia 529.
    if not elemente_validate:
# [AUTO-COMMENT] Linia 530.
        return None
# [AUTO-COMMENT] Linia 531: linie goală.

# [AUTO-COMMENT] Linia 532.
    indicator_cerut = text_scurt(prima_valoare(payload_client, ["indicator", "metric", "parametru"]))
# [AUTO-COMMENT] Linia 533.
    if not indicator_cerut:
# [AUTO-COMMENT] Linia 534.
        return elemente_validate[0]
# [AUTO-COMMENT] Linia 535: linie goală.

# [AUTO-COMMENT] Linia 536.
    indicator_cerut_normalizat = text_normalizat(indicator_cerut)
# [AUTO-COMMENT] Linia 537: linie goală.

# [AUTO-COMMENT] Linia 538.
    for element in elemente_validate:
# [AUTO-COMMENT] Linia 539.
        metric = element.get("metric")
# [AUTO-COMMENT] Linia 540.
        metric_normalizat = text_normalizat(metric)
# [AUTO-COMMENT] Linia 541.
        if (
# [AUTO-COMMENT] Linia 542.
            metric_normalizat == indicator_cerut_normalizat
# [AUTO-COMMENT] Linia 543.
            or indicator_cerut_normalizat in metric_normalizat
# [AUTO-COMMENT] Linia 544.
            or metric_normalizat in indicator_cerut_normalizat
# [AUTO-COMMENT] Linia 545.
        ):
# [AUTO-COMMENT] Linia 546.
            return element
# [AUTO-COMMENT] Linia 547: linie goală.

# [AUTO-COMMENT] Linia 548.
    return elemente_validate[0]
# [AUTO-COMMENT] Linia 549: linie goală.

# [AUTO-COMMENT] Linia 550: linie goală.

# [AUTO-COMMENT] Linia 551.
def selectie_element_extern_sau_eroare(date_externe, payload_client, actiune, mesaj_eroare, extra=None):
# [AUTO-COMMENT] Linia 552.
    element = selecteaza_element_extern(date_externe["elemente_validate"], payload_client)
# [AUTO-COMMENT] Linia 553.
    if element is not None:
# [AUTO-COMMENT] Linia 554.
        return element, None
# [AUTO-COMMENT] Linia 555: linie goală.

# [AUTO-COMMENT] Linia 556.
    payload_eroare = {
# [AUTO-COMMENT] Linia 557.
        "eroare": mesaj_eroare,
# [AUTO-COMMENT] Linia 558.
        "actiune": actiune,
# [AUTO-COMMENT] Linia 559.
        "numar_ignorate": len(date_externe["elemente_ignorate"]),
# [AUTO-COMMENT] Linia 560.
        "elemente_ignorate": date_externe["elemente_ignorate"],
# [AUTO-COMMENT] Linia 561.
    }
# [AUTO-COMMENT] Linia 562.
    if extra:
# [AUTO-COMMENT] Linia 563.
        payload_eroare.update(extra)
# [AUTO-COMMENT] Linia 564: linie goală.

# [AUTO-COMMENT] Linia 565.
    return None, make_response(jsonify(payload_eroare), 502)
# [AUTO-COMMENT] Linia 566: linie goală.

# [AUTO-COMMENT] Linia 567: linie goală.

# [AUTO-COMMENT] Linia 568.
def gaseste_id_dupa_metric_si_oras(metric_cautat, oras_cautat):
# [AUTO-COMMENT] Linia 569.
    metric_normalizat = text_normalizat(metric_cautat)
# [AUTO-COMMENT] Linia 570.
    oras_normalizat = text_normalizat(oras_cautat)
# [AUTO-COMMENT] Linia 571: linie goală.

# [AUTO-COMMENT] Linia 572.
    if not metric_normalizat:
# [AUTO-COMMENT] Linia 573.
        return None
# [AUTO-COMMENT] Linia 574: linie goală.

# [AUTO-COMMENT] Linia 575.
    for item_id in sorted(baza_masuratori.keys()):
# [AUTO-COMMENT] Linia 576.
        element = baza_masuratori[item_id]
# [AUTO-COMMENT] Linia 577.
        metric_curent = text_normalizat(element.get("metric"))
# [AUTO-COMMENT] Linia 578.
        if metric_curent != metric_normalizat:
# [AUTO-COMMENT] Linia 579.
            continue
# [AUTO-COMMENT] Linia 580: linie goală.

# [AUTO-COMMENT] Linia 581.
        oras_curent = text_normalizat(element.get("city"))
# [AUTO-COMMENT] Linia 582.
        if oras_normalizat:
# [AUTO-COMMENT] Linia 583.
            if oras_curent == oras_normalizat:
# [AUTO-COMMENT] Linia 584.
                return item_id
# [AUTO-COMMENT] Linia 585.
        else:
# [AUTO-COMMENT] Linia 586.
            return item_id
# [AUTO-COMMENT] Linia 587: linie goală.

# [AUTO-COMMENT] Linia 588.
    return None
# [AUTO-COMMENT] Linia 589: linie goală.

# [AUTO-COMMENT] Linia 590: linie goală.

# [AUTO-COMMENT] Linia 591.
def salveaza_element(element, item_id=None):
# [AUTO-COMMENT] Linia 592.
    global urmatorul_id
# [AUTO-COMMENT] Linia 593: linie goală.

# [AUTO-COMMENT] Linia 594.
    if item_id is None:
# [AUTO-COMMENT] Linia 595.
        item_id = urmatorul_id
# [AUTO-COMMENT] Linia 596: linie goală.

# [AUTO-COMMENT] Linia 597.
    if item_id >= urmatorul_id:
# [AUTO-COMMENT] Linia 598.
        urmatorul_id = item_id + 1
# [AUTO-COMMENT] Linia 599: linie goală.

# [AUTO-COMMENT] Linia 600.
    creat = {"id": item_id, **element}
# [AUTO-COMMENT] Linia 601.
    baza_masuratori[item_id] = creat
# [AUTO-COMMENT] Linia 602.
    return creat
# [AUTO-COMMENT] Linia 603: linie goală.

# [AUTO-COMMENT] Linia 604: linie goală.

# [AUTO-COMMENT] Linia 605.
def aplica_patch_element(element_baza, campuri_noi):
# [AUTO-COMMENT] Linia 606.
    element_actualizat = {**element_baza}
# [AUTO-COMMENT] Linia 607.
    campuri_actualizate = []
# [AUTO-COMMENT] Linia 608: linie goală.

# [AUTO-COMMENT] Linia 609.
    for camp, valoare in campuri_noi.items():
# [AUTO-COMMENT] Linia 610.
        if element_actualizat.get(camp) != valoare:
# [AUTO-COMMENT] Linia 611.
            element_actualizat[camp] = valoare
# [AUTO-COMMENT] Linia 612.
            campuri_actualizate.append(camp)
# [AUTO-COMMENT] Linia 613: linie goală.

# [AUTO-COMMENT] Linia 614.
    return element_actualizat, sorted(campuri_actualizate)
# [AUTO-COMMENT] Linia 615: linie goală.

# [AUTO-COMMENT] Linia 616: linie goală.

# [AUTO-COMMENT] Linia 617.
def raspuns_creare(payload, item_id):
# [AUTO-COMMENT] Linia 618.
    raspuns = make_response(jsonify(payload), 201)
# [AUTO-COMMENT] Linia 619.
    raspuns.headers["Location"] = f"/masuratori/{item_id}"
# [AUTO-COMMENT] Linia 620.
    return raspuns
# [AUTO-COMMENT] Linia 621: linie goală.

# [AUTO-COMMENT] Linia 622: linie goală.

# [AUTO-COMMENT] Linia 623.
def extrage_element_extern_din_request(actiune, mesaj_eroare, extra=None, adauga_oras_cerut=False):
# [AUTO-COMMENT] Linia 624.
    payload, date_externe, raspuns_eroare_externa = extrage_date_externe_din_request()
# [AUTO-COMMENT] Linia 625.
    if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 626.
        return None, None, raspuns_eroare_externa
# [AUTO-COMMENT] Linia 627: linie goală.

# [AUTO-COMMENT] Linia 628.
    extra_final = dict(extra or {})
# [AUTO-COMMENT] Linia 629.
    if adauga_oras_cerut:
# [AUTO-COMMENT] Linia 630.
        extra_final["oras_cerut"] = date_externe["oras_cerut"]
# [AUTO-COMMENT] Linia 631: linie goală.

# [AUTO-COMMENT] Linia 632.
    element, raspuns_selectie = selectie_element_extern_sau_eroare(
# [AUTO-COMMENT] Linia 633.
        date_externe,
# [AUTO-COMMENT] Linia 634.
        payload,
# [AUTO-COMMENT] Linia 635.
        actiune,
# [AUTO-COMMENT] Linia 636.
        mesaj_eroare,
# [AUTO-COMMENT] Linia 637.
        extra=extra_final or None,
# [AUTO-COMMENT] Linia 638.
    )
# [AUTO-COMMENT] Linia 639.
    if raspuns_selectie:
# [AUTO-COMMENT] Linia 640.
        return None, None, raspuns_selectie
# [AUTO-COMMENT] Linia 641: linie goală.

# [AUTO-COMMENT] Linia 642.
    return element, date_externe, None
# [AUTO-COMMENT] Linia 643: linie goală.

# [AUTO-COMMENT] Linia 644: linie goală.

# [AUTO-COMMENT] Linia 645.
@app.route("/", methods=["GET"])
# [AUTO-COMMENT] Linia 646.
def acasa():
# [AUTO-COMMENT] Linia 647.
    return render_template("panou_masuratori.html")
# [AUTO-COMMENT] Linia 648: linie goală.

# [AUTO-COMMENT] Linia 649: linie goală.

# [AUTO-COMMENT] Linia 650.
@app.route("/measurements/trace/collection", methods=["POST"])
# [AUTO-COMMENT] Linia 651.
@app.route("/masuratori/trace/colectie", methods=["POST"])
# [AUTO-COMMENT] Linia 652.
def endpoint_trace_ui_colectie():
# [AUTO-COMMENT] Linia 653.
    return raspuns_trace("/masuratori", "colectie_masuratori", METODE_COLECTIE, simulat_ui=True)
# [AUTO-COMMENT] Linia 654: linie goală.

# [AUTO-COMMENT] Linia 655: linie goală.

# [AUTO-COMMENT] Linia 656.
@app.route("/measurements/trace/item/<int:item_id>", methods=["POST"])
# [AUTO-COMMENT] Linia 657.
@app.route("/masuratori/trace/element/<int:item_id>", methods=["POST"])
# [AUTO-COMMENT] Linia 658.
def endpoint_trace_ui_element(item_id):
# [AUTO-COMMENT] Linia 659.
    if item_id <= 0:
# [AUTO-COMMENT] Linia 660.
        return raspuns_eroare("item_id trebuie să fie pozitiv.", 400)
# [AUTO-COMMENT] Linia 661.
    return raspuns_trace(f"/masuratori/{item_id}", f"element_masurare_{item_id}", METODE_ELEMENT, simulat_ui=True)
# [AUTO-COMMENT] Linia 662: linie goală.

# [AUTO-COMMENT] Linia 663: linie goală.

# [AUTO-COMMENT] Linia 664.
@app.route("/measurements/external-preview", methods=["POST"])
# [AUTO-COMMENT] Linia 665.
@app.route("/masuratori/preview-extern", methods=["POST"])
# [AUTO-COMMENT] Linia 666.
def endpoint_preview_extern():
# [AUTO-COMMENT] Linia 667.
    _, date_externe, raspuns_eroare_externa = extrage_date_externe_din_request()
# [AUTO-COMMENT] Linia 668.
    if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 669.
        return raspuns_eroare_externa
# [AUTO-COMMENT] Linia 670: linie goală.

# [AUTO-COMMENT] Linia 671.
    elemente_preview = [
# [AUTO-COMMENT] Linia 672.
        {"id_preview": index, **element}
# [AUTO-COMMENT] Linia 673.
        for index, element in enumerate(date_externe["elemente_validate"], start=1)
# [AUTO-COMMENT] Linia 674.
    ]
# [AUTO-COMMENT] Linia 675: linie goală.

# [AUTO-COMMENT] Linia 676.
    return jsonify({
# [AUTO-COMMENT] Linia 677.
        "mesaj": "Preview date externe generat.",
# [AUTO-COMMENT] Linia 678.
        "actiune": "preview_date_externe",
# [AUTO-COMMENT] Linia 679.
        "sursa": "open-meteo",
# [AUTO-COMMENT] Linia 680.
        "oras_cerut": date_externe["oras_cerut"],
# [AUTO-COMMENT] Linia 681.
        "oras_rezolvat": date_externe["info_geo"].get("city"),
# [AUTO-COMMENT] Linia 682.
        "numar_preview": len(elemente_preview),
# [AUTO-COMMENT] Linia 683.
        "numar_ignorate": len(date_externe["elemente_ignorate"]),
# [AUTO-COMMENT] Linia 684.
        "elemente_preview": elemente_preview,
# [AUTO-COMMENT] Linia 685.
        "elemente_ignorate": date_externe["elemente_ignorate"],
# [AUTO-COMMENT] Linia 686.
    }), 200
# [AUTO-COMMENT] Linia 687: linie goală.

# [AUTO-COMMENT] Linia 688: linie goală.

# [AUTO-COMMENT] Linia 689.
@app.route("/measurements/synchronize", methods=["POST"])
# [AUTO-COMMENT] Linia 690.
@app.route("/masuratori/sincronizeaza", methods=["POST"])
# [AUTO-COMMENT] Linia 691.
def endpoint_sincronizare_externa():
# [AUTO-COMMENT] Linia 692.
    _, date_externe, raspuns_eroare_externa = extrage_date_externe_din_request()
# [AUTO-COMMENT] Linia 693.
    if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 694.
        return raspuns_eroare_externa
# [AUTO-COMMENT] Linia 695: linie goală.

# [AUTO-COMMENT] Linia 696.
    elemente_adaugate = [
# [AUTO-COMMENT] Linia 697.
        salveaza_element(element)
# [AUTO-COMMENT] Linia 698.
        for element in date_externe["elemente_validate"]
# [AUTO-COMMENT] Linia 699.
    ]
# [AUTO-COMMENT] Linia 700.
    elemente_ignorate = date_externe["elemente_ignorate"]
# [AUTO-COMMENT] Linia 701: linie goală.

# [AUTO-COMMENT] Linia 702.
    if not elemente_adaugate:
# [AUTO-COMMENT] Linia 703.
        return jsonify({
# [AUTO-COMMENT] Linia 704.
            "eroare": "Nu am putut importa măsurători valide din sursa externă.",
# [AUTO-COMMENT] Linia 705.
            "actiune": "sincronizeaza_din_open_meteo",
# [AUTO-COMMENT] Linia 706.
            "oras_cerut": date_externe["oras_cerut"],
# [AUTO-COMMENT] Linia 707.
            "numar_ignorate": len(elemente_ignorate),
# [AUTO-COMMENT] Linia 708.
            "elemente_ignorate": elemente_ignorate,
# [AUTO-COMMENT] Linia 709.
        }), 502
# [AUTO-COMMENT] Linia 710: linie goală.

# [AUTO-COMMENT] Linia 711.
    return jsonify({
# [AUTO-COMMENT] Linia 712.
        "mesaj": "Sincronizare externă finalizată.",
# [AUTO-COMMENT] Linia 713.
        "actiune": "sincronizeaza_din_open_meteo",
# [AUTO-COMMENT] Linia 714.
        "sursa": "open-meteo",
# [AUTO-COMMENT] Linia 715.
        "oras_cerut": date_externe["oras_cerut"],
# [AUTO-COMMENT] Linia 716.
        "oras_rezolvat": date_externe["info_geo"].get("city"),
# [AUTO-COMMENT] Linia 717.
        "numar_adaugate": len(elemente_adaugate),
# [AUTO-COMMENT] Linia 718.
        "numar_ignorate": len(elemente_ignorate),
# [AUTO-COMMENT] Linia 719.
        "ids_generate": [element["id"] for element in elemente_adaugate],
# [AUTO-COMMENT] Linia 720.
        "elemente_adaugate": elemente_adaugate,
# [AUTO-COMMENT] Linia 721.
        "elemente_ignorate": elemente_ignorate,
# [AUTO-COMMENT] Linia 722.
    }), 201
# [AUTO-COMMENT] Linia 723: linie goală.

# [AUTO-COMMENT] Linia 724: linie goală.

# [AUTO-COMMENT] Linia 725.
@app.route("/measurements", methods=METODE_COLECTIE)
# [AUTO-COMMENT] Linia 726.
@app.route("/masuratori", methods=METODE_COLECTIE)
# [AUTO-COMMENT] Linia 727.
def endpoint_colectie():
# [AUTO-COMMENT] Linia 728.
    global baza_masuratori
# [AUTO-COMMENT] Linia 729.
    global urmatorul_id
# [AUTO-COMMENT] Linia 730: linie goală.

# [AUTO-COMMENT] Linia 731.
    if request.method == "OPTIONS":
# [AUTO-COMMENT] Linia 732.
        return raspuns_options("/masuratori", METODE_COLECTIE, "colectie_masuratori")
# [AUTO-COMMENT] Linia 733: linie goală.

# [AUTO-COMMENT] Linia 734.
    if request.method == "TRACE":
# [AUTO-COMMENT] Linia 735.
        return raspuns_trace("/masuratori", "colectie_masuratori", METODE_COLECTIE)
# [AUTO-COMMENT] Linia 736: linie goală.

# [AUTO-COMMENT] Linia 737.
    if request.method == "HEAD":
# [AUTO-COMMENT] Linia 738.
        raspuns = make_response("", 200)
# [AUTO-COMMENT] Linia 739.
        raspuns.headers["Allow"] = header_allow_pentru(METODE_COLECTIE)
# [AUTO-COMMENT] Linia 740.
        raspuns.headers["X-Numar-Elemente"] = str(len(baza_masuratori))
# [AUTO-COMMENT] Linia 741.
        return raspuns
# [AUTO-COMMENT] Linia 742: linie goală.

# [AUTO-COMMENT] Linia 743.
    if request.method == "GET":
# [AUTO-COMMENT] Linia 744.
        return jsonify(raspuns_colectie()), 200
# [AUTO-COMMENT] Linia 745: linie goală.

# [AUTO-COMMENT] Linia 746.
    if request.method == "POST":
# [AUTO-COMMENT] Linia 747.
        element, date_externe, raspuns_eroare_externa = extrage_element_extern_din_request(
# [AUTO-COMMENT] Linia 748.
            "post_colectie_din_api_extern",
# [AUTO-COMMENT] Linia 749.
            "Nu am putut extrage niciun element valid din sursa externă.",
# [AUTO-COMMENT] Linia 750.
            adauga_oras_cerut=True,
# [AUTO-COMMENT] Linia 751.
        )
# [AUTO-COMMENT] Linia 752.
        if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 753.
            return raspuns_eroare_externa
# [AUTO-COMMENT] Linia 754: linie goală.

# [AUTO-COMMENT] Linia 755.
        creat = salveaza_element(element)
# [AUTO-COMMENT] Linia 756: linie goală.

# [AUTO-COMMENT] Linia 757.
        return raspuns_creare(
# [AUTO-COMMENT] Linia 758.
            {
# [AUTO-COMMENT] Linia 759.
                **creat,
# [AUTO-COMMENT] Linia 760.
                "actiune": "post_colectie_din_api_extern",
# [AUTO-COMMENT] Linia 761.
                "sursa": "open-meteo",
# [AUTO-COMMENT] Linia 762.
                "oras_rezolvat": date_externe["info_geo"].get("city"),
# [AUTO-COMMENT] Linia 763.
            },
# [AUTO-COMMENT] Linia 764.
            creat["id"],
# [AUTO-COMMENT] Linia 765.
        )
# [AUTO-COMMENT] Linia 766: linie goală.

# [AUTO-COMMENT] Linia 767.
    if request.method == "PUT":
# [AUTO-COMMENT] Linia 768.
        _, date_externe, raspuns_eroare_externa = extrage_date_externe_din_request()
# [AUTO-COMMENT] Linia 769.
        if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 770.
            return raspuns_eroare_externa
# [AUTO-COMMENT] Linia 771: linie goală.

# [AUTO-COMMENT] Linia 772.
        if not date_externe["elemente_validate"]:
# [AUTO-COMMENT] Linia 773.
            return jsonify({
# [AUTO-COMMENT] Linia 774.
                "eroare": "Nu am putut importa măsurători valide pentru înlocuirea colecției.",
# [AUTO-COMMENT] Linia 775.
                "actiune": "put_colectie_din_api_extern",
# [AUTO-COMMENT] Linia 776.
                "oras_cerut": date_externe["oras_cerut"],
# [AUTO-COMMENT] Linia 777.
                "numar_ignorate": len(date_externe["elemente_ignorate"]),
# [AUTO-COMMENT] Linia 778.
                "elemente_ignorate": date_externe["elemente_ignorate"],
# [AUTO-COMMENT] Linia 779.
            }), 502
# [AUTO-COMMENT] Linia 780: linie goală.

# [AUTO-COMMENT] Linia 781.
        date_noi = {
# [AUTO-COMMENT] Linia 782.
            index: {"id": index, **element}
# [AUTO-COMMENT] Linia 783.
            for index, element in enumerate(date_externe["elemente_validate"], start=1)
# [AUTO-COMMENT] Linia 784.
        }
# [AUTO-COMMENT] Linia 785: linie goală.

# [AUTO-COMMENT] Linia 786.
        baza_masuratori = date_noi
# [AUTO-COMMENT] Linia 787.
        urmatorul_id = len(baza_masuratori) + 1
# [AUTO-COMMENT] Linia 788: linie goală.

# [AUTO-COMMENT] Linia 789.
        raspuns = raspuns_colectie()
# [AUTO-COMMENT] Linia 790.
        raspuns["actiune"] = "put_colectie_din_api_extern"
# [AUTO-COMMENT] Linia 791.
        raspuns["sursa"] = "open-meteo"
# [AUTO-COMMENT] Linia 792.
        raspuns["oras_rezolvat"] = date_externe["info_geo"].get("city")
# [AUTO-COMMENT] Linia 793.
        raspuns["numar_ignorate"] = len(date_externe["elemente_ignorate"])
# [AUTO-COMMENT] Linia 794.
        raspuns["elemente_ignorate"] = date_externe["elemente_ignorate"]
# [AUTO-COMMENT] Linia 795.
        return jsonify(raspuns), 200
# [AUTO-COMMENT] Linia 796: linie goală.

# [AUTO-COMMENT] Linia 797.
    if request.method == "PATCH":
# [AUTO-COMMENT] Linia 798.
        element_nou, date_externe, raspuns_eroare_externa = extrage_element_extern_din_request(
# [AUTO-COMMENT] Linia 799.
            "patch_colectie_din_api_extern",
# [AUTO-COMMENT] Linia 800.
            "Nu am putut extrage niciun element valid pentru patch din sursa externă.",
# [AUTO-COMMENT] Linia 801.
            adauga_oras_cerut=True,
# [AUTO-COMMENT] Linia 802.
        )
# [AUTO-COMMENT] Linia 803.
        if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 804.
            return raspuns_eroare_externa
# [AUTO-COMMENT] Linia 805.
        id_tinta = gaseste_id_dupa_metric_si_oras(element_nou.get("metric"), element_nou.get("city"))
# [AUTO-COMMENT] Linia 806: linie goală.

# [AUTO-COMMENT] Linia 807.
        status_patch = "adaugat"
# [AUTO-COMMENT] Linia 808.
        cod_status = 201
# [AUTO-COMMENT] Linia 809.
        campuri_actualizate = []
# [AUTO-COMMENT] Linia 810: linie goală.

# [AUTO-COMMENT] Linia 811.
        if id_tinta is None:
# [AUTO-COMMENT] Linia 812.
            element_final = salveaza_element(element_nou)
# [AUTO-COMMENT] Linia 813.
            id_tinta = element_final["id"]
# [AUTO-COMMENT] Linia 814.
            campuri_actualizate = sorted(list(element_nou.keys()))
# [AUTO-COMMENT] Linia 815.
        else:
# [AUTO-COMMENT] Linia 816.
            element_actualizat, campuri_actualizate = aplica_patch_element(baza_masuratori[id_tinta], element_nou)
# [AUTO-COMMENT] Linia 817.
            baza_masuratori[id_tinta] = element_actualizat
# [AUTO-COMMENT] Linia 818.
            status_patch = "actualizat"
# [AUTO-COMMENT] Linia 819.
            cod_status = 200
# [AUTO-COMMENT] Linia 820: linie goală.

# [AUTO-COMMENT] Linia 821.
        element_final = baza_masuratori[id_tinta]
# [AUTO-COMMENT] Linia 822.
        payload_raspuns = {
# [AUTO-COMMENT] Linia 823.
            "actiune": "patch_colectie_din_api_extern",
# [AUTO-COMMENT] Linia 824.
            "status_patch": status_patch,
# [AUTO-COMMENT] Linia 825.
            "id_tinta": id_tinta,
# [AUTO-COMMENT] Linia 826.
            "campuri_actualizate": campuri_actualizate,
# [AUTO-COMMENT] Linia 827.
            "sursa": "open-meteo",
# [AUTO-COMMENT] Linia 828.
            "oras_rezolvat": date_externe["info_geo"].get("city"),
# [AUTO-COMMENT] Linia 829.
            "element": element_final,
# [AUTO-COMMENT] Linia 830.
        }
# [AUTO-COMMENT] Linia 831: linie goală.

# [AUTO-COMMENT] Linia 832.
        if cod_status == 201:
# [AUTO-COMMENT] Linia 833.
            return raspuns_creare(payload_raspuns, id_tinta)
# [AUTO-COMMENT] Linia 834: linie goală.

# [AUTO-COMMENT] Linia 835.
        return jsonify(payload_raspuns), 200
# [AUTO-COMMENT] Linia 836: linie goală.

# [AUTO-COMMENT] Linia 837.
    if request.method == "DELETE":
# [AUTO-COMMENT] Linia 838.
        sterse = len(baza_masuratori)
# [AUTO-COMMENT] Linia 839.
        baza_masuratori = {}
# [AUTO-COMMENT] Linia 840.
        urmatorul_id = 1
# [AUTO-COMMENT] Linia 841.
        return jsonify({
# [AUTO-COMMENT] Linia 842.
            "mesaj": "Toate măsurătorile din colecție au fost șterse.",
# [AUTO-COMMENT] Linia 843.
            "numar_sterse": sterse,
# [AUTO-COMMENT] Linia 844.
            "colectie_curenta": [],
# [AUTO-COMMENT] Linia 845.
        }), 200
# [AUTO-COMMENT] Linia 846: linie goală.

# [AUTO-COMMENT] Linia 847.
    return raspuns_eroare("Metodă HTTP neacceptată pe colecție.", 405)
# [AUTO-COMMENT] Linia 848: linie goală.

# [AUTO-COMMENT] Linia 849: linie goală.

# [AUTO-COMMENT] Linia 850.
@app.route("/measurements/<int:item_id>", methods=METODE_ELEMENT)
# [AUTO-COMMENT] Linia 851.
@app.route("/masuratori/<int:item_id>", methods=METODE_ELEMENT)
# [AUTO-COMMENT] Linia 852.
def endpoint_element(item_id):
# [AUTO-COMMENT] Linia 853.
    if item_id <= 0:
# [AUTO-COMMENT] Linia 854.
        return raspuns_eroare("item_id trebuie să fie pozitiv.", 400)
# [AUTO-COMMENT] Linia 855: linie goală.

# [AUTO-COMMENT] Linia 856.
    if request.method == "OPTIONS":
# [AUTO-COMMENT] Linia 857.
        return raspuns_options(f"/masuratori/{item_id}", METODE_ELEMENT, f"element_masurare_{item_id}")
# [AUTO-COMMENT] Linia 858: linie goală.

# [AUTO-COMMENT] Linia 859.
    if request.method == "TRACE":
# [AUTO-COMMENT] Linia 860.
        return raspuns_trace(f"/masuratori/{item_id}", f"element_masurare_{item_id}", METODE_ELEMENT)
# [AUTO-COMMENT] Linia 861: linie goală.

# [AUTO-COMMENT] Linia 862.
    if request.method == "HEAD":
# [AUTO-COMMENT] Linia 863.
        element = baza_masuratori.get(item_id)
# [AUTO-COMMENT] Linia 864.
        exista = element is not None
# [AUTO-COMMENT] Linia 865.
        cod = 200 if exista else 404
# [AUTO-COMMENT] Linia 866: linie goală.

# [AUTO-COMMENT] Linia 867.
        raspuns = make_response("", cod)
# [AUTO-COMMENT] Linia 868.
        raspuns.headers["Allow"] = header_allow_pentru(METODE_ELEMENT)
# [AUTO-COMMENT] Linia 869.
        raspuns.headers["X-Item-Id"] = str(item_id)
# [AUTO-COMMENT] Linia 870.
        raspuns.headers["X-Item-Exists"] = "true" if exista else "false"
# [AUTO-COMMENT] Linia 871.
        if exista:
# [AUTO-COMMENT] Linia 872.
            raspuns.headers["X-Item-Metric"] = str(element.get("metric", ""))
# [AUTO-COMMENT] Linia 873.
        return raspuns
# [AUTO-COMMENT] Linia 874: linie goală.

# [AUTO-COMMENT] Linia 875.
    if request.method == "GET":
# [AUTO-COMMENT] Linia 876.
        element = baza_masuratori.get(item_id)
# [AUTO-COMMENT] Linia 877.
        if element is None:
# [AUTO-COMMENT] Linia 878.
            return raspuns_eroare("Elementul cerut nu există.", 404)
# [AUTO-COMMENT] Linia 879.
        return jsonify(element), 200
# [AUTO-COMMENT] Linia 880: linie goală.

# [AUTO-COMMENT] Linia 881.
    if request.method == "POST":
# [AUTO-COMMENT] Linia 882.
        if item_id in baza_masuratori:
# [AUTO-COMMENT] Linia 883.
            return raspuns_eroare("Elementul există deja pentru acest id.", 409)
# [AUTO-COMMENT] Linia 884: linie goală.

# [AUTO-COMMENT] Linia 885.
        element, _, raspuns_eroare_externa = extrage_element_extern_din_request(
# [AUTO-COMMENT] Linia 886.
            "post_element_din_api_extern",
# [AUTO-COMMENT] Linia 887.
            "Nu am putut extrage un element valid pentru acest id din sursa externă.",
# [AUTO-COMMENT] Linia 888.
            extra={"id_cerut": item_id},
# [AUTO-COMMENT] Linia 889.
        )
# [AUTO-COMMENT] Linia 890.
        if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 891.
            return raspuns_eroare_externa
# [AUTO-COMMENT] Linia 892: linie goală.

# [AUTO-COMMENT] Linia 893.
        creat = salveaza_element(element, item_id=item_id)
# [AUTO-COMMENT] Linia 894: linie goală.

# [AUTO-COMMENT] Linia 895.
        return raspuns_creare(creat, item_id)
# [AUTO-COMMENT] Linia 896: linie goală.

# [AUTO-COMMENT] Linia 897.
    if request.method == "PUT":
# [AUTO-COMMENT] Linia 898.
        element, _, raspuns_eroare_externa = extrage_element_extern_din_request(
# [AUTO-COMMENT] Linia 899.
            "put_element_din_api_extern",
# [AUTO-COMMENT] Linia 900.
            "Nu am putut extrage un element valid pentru actualizare din sursa externă.",
# [AUTO-COMMENT] Linia 901.
            extra={"id_cerut": item_id},
# [AUTO-COMMENT] Linia 902.
        )
# [AUTO-COMMENT] Linia 903.
        if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 904.
            return raspuns_eroare_externa
# [AUTO-COMMENT] Linia 905: linie goală.

# [AUTO-COMMENT] Linia 906.
        exista = item_id in baza_masuratori
# [AUTO-COMMENT] Linia 907.
        actualizat = salveaza_element(element, item_id=item_id)
# [AUTO-COMMENT] Linia 908: linie goală.

# [AUTO-COMMENT] Linia 909.
        if exista:
# [AUTO-COMMENT] Linia 910.
            return jsonify(actualizat), 200
# [AUTO-COMMENT] Linia 911: linie goală.

# [AUTO-COMMENT] Linia 912.
        return raspuns_creare(actualizat, item_id)
# [AUTO-COMMENT] Linia 913: linie goală.

# [AUTO-COMMENT] Linia 914.
    if request.method == "PATCH":
# [AUTO-COMMENT] Linia 915.
        element_existent = baza_masuratori.get(item_id)
# [AUTO-COMMENT] Linia 916.
        if element_existent is None:
# [AUTO-COMMENT] Linia 917.
            return raspuns_eroare("Elementul cerut nu există pentru patch.", 404)
# [AUTO-COMMENT] Linia 918: linie goală.

# [AUTO-COMMENT] Linia 919.
        element_nou, date_externe, raspuns_eroare_externa = extrage_element_extern_din_request(
# [AUTO-COMMENT] Linia 920.
            "patch_element_din_api_extern",
# [AUTO-COMMENT] Linia 921.
            "Nu am putut extrage un element valid pentru patch din sursa externă.",
# [AUTO-COMMENT] Linia 922.
            extra={"id_cerut": item_id},
# [AUTO-COMMENT] Linia 923.
        )
# [AUTO-COMMENT] Linia 924.
        if raspuns_eroare_externa:
# [AUTO-COMMENT] Linia 925.
            return raspuns_eroare_externa
# [AUTO-COMMENT] Linia 926.
        element_actualizat, campuri_actualizate = aplica_patch_element(element_existent, element_nou)
# [AUTO-COMMENT] Linia 927: linie goală.

# [AUTO-COMMENT] Linia 928.
        baza_masuratori[item_id] = element_actualizat
# [AUTO-COMMENT] Linia 929: linie goală.

# [AUTO-COMMENT] Linia 930.
        return jsonify({
# [AUTO-COMMENT] Linia 931.
            "actiune": "patch_element_din_api_extern",
# [AUTO-COMMENT] Linia 932.
            "id_actualizat": item_id,
# [AUTO-COMMENT] Linia 933.
            "campuri_actualizate": campuri_actualizate,
# [AUTO-COMMENT] Linia 934.
            "sursa": "open-meteo",
# [AUTO-COMMENT] Linia 935.
            "oras_rezolvat": date_externe["info_geo"].get("city"),
# [AUTO-COMMENT] Linia 936.
            "element": element_actualizat,
# [AUTO-COMMENT] Linia 937.
        }), 200
# [AUTO-COMMENT] Linia 938: linie goală.

# [AUTO-COMMENT] Linia 939.
    if request.method == "DELETE":
# [AUTO-COMMENT] Linia 940.
        element = baza_masuratori.get(item_id)
# [AUTO-COMMENT] Linia 941.
        if element is None:
# [AUTO-COMMENT] Linia 942.
            return raspuns_eroare("Elementul cerut nu există.", 404)
# [AUTO-COMMENT] Linia 943: linie goală.

# [AUTO-COMMENT] Linia 944.
        del baza_masuratori[item_id]
# [AUTO-COMMENT] Linia 945.
        return jsonify({
# [AUTO-COMMENT] Linia 946.
            "mesaj": "Elementul selectat a fost șters.",
# [AUTO-COMMENT] Linia 947.
            "id_sters": item_id,
# [AUTO-COMMENT] Linia 948.
        }), 200
# [AUTO-COMMENT] Linia 949: linie goală.

# [AUTO-COMMENT] Linia 950.
    return raspuns_eroare("Metodă HTTP neacceptată pe element.", 405)
# [AUTO-COMMENT] Linia 951: linie goală.

# [AUTO-COMMENT] Linia 952: linie goală.

# [AUTO-COMMENT] Linia 953.
if __name__ == "__main__":
# [AUTO-COMMENT] Linia 954.
    app.run(host="127.0.0.1", port=5000, debug=True)
