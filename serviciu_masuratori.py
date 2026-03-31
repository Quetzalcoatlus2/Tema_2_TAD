from datetime import datetime, timezone
import json
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, jsonify, make_response, render_template, request

app = Flask(__name__)

baza_masuratori = {}
urmatorul_id = 1

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
USER_AGENT_EXTERNE = "Tema2-TAD-Masuratori/1.0 (educational project)"
METODE_HTTP = ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE"]
METODE_COLECTIE = METODE_HTTP
METODE_ELEMENT = METODE_HTTP
CORS_ALLOW_HEADERS = "Content-Type, Authorization, Accept"

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


def acum_utc_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def lista_ordonata():
    return [baza_masuratori[item_id] for item_id in sorted(baza_masuratori.keys())]


def prima_valoare(payload, chei):
    for cheie in chei:
        if cheie in payload:
            return payload.get(cheie)
    return None


def valoare_numerica(brut):
    if isinstance(brut, bool):
        return None
    if isinstance(brut, (int, float)):
        valoare = float(brut)
    elif isinstance(brut, str):
        text = brut.strip()
        if not text:
            return None
        try:
            valoare = float(text)
        except ValueError:
            return None
    else:
        return None

    if valoare < 0:
        return None

    if valoare.is_integer():
        return int(valoare)
    return valoare


def text_scurt(valoare):
    if valoare is None:
        return None
    if not isinstance(valoare, str):
        return None
    curat = valoare.strip()
    return curat if curat else None


def valideaza_etichete(etichete):
    if etichete is None:
        return None, None
    if not isinstance(etichete, list):
        return None, "etichete/tags trebuie să fie listă de texte."

    rezultat = []
    for element in etichete:
        if not isinstance(element, str) or not element.strip():
            return None, "fiecare etichetă trebuie să fie text nevid."
        rezultat.append(element.strip())
    return rezultat, None


def valideaza_interval(interval):
    if interval is None:
        return None, None
    numeric = valoare_numerica(interval)
    if numeric is None or numeric == 0:
        return None, "sampling_interval_seconds/frecventa_secunde trebuie să fie numeric și > 0."
    return numeric, None


def valideaza_payload(payload):
    if not isinstance(payload, dict):
        return None, "Body trebuie să fie obiect JSON."

    statie = text_scurt(prima_valoare(payload, ["station", "statie", "punct_masurare"]))
    indicator = text_scurt(prima_valoare(payload, ["metric", "indicator", "parametru"]))
    unitate = text_scurt(prima_valoare(payload, ["unit", "unitate", "unitate_masura"]))
    valoare = valoare_numerica(prima_valoare(payload, ["value", "valoare", "valoare_masurata"]))

    if not statie:
        return None, "Lipsește station/statie/punct_masurare."
    if not indicator:
        return None, "Lipsește metric/indicator/parametru."
    if not unitate:
        return None, "Lipsește unit/unitate/unitate_masura."
    if valoare is None:
        return None, "value/valoare trebuie să fie numeric și >= 0."

    moment = prima_valoare(payload, ["timestamp", "moment", "moment_inregistrare"])
    if moment is None:
        moment = acum_utc_iso()
    else:
        moment = text_scurt(moment)
        if not moment:
            return None, "timestamp/moment trebuie să fie text nevid dacă este trimis."

    rezultat = {
        "station": statie,
        "metric": indicator,
        "value": valoare,
        "unit": unitate,
        "timestamp": moment,
    }

    for camp, aliasuri in CAMPURI_TEXT_OPTIONALE.items():
        valoare_text = text_scurt(prima_valoare(payload, aliasuri))
        if valoare_text:
            rezultat[camp] = valoare_text

    etichete, eroare_etichete = valideaza_etichete(prima_valoare(payload, ["tags", "etichete", "cuvinte_cheie"]))
    if eroare_etichete:
        return None, eroare_etichete
    if etichete:
        rezultat["tags"] = etichete

    interval, eroare_interval = valideaza_interval(prima_valoare(payload, ["sampling_interval_seconds", "frecventa_secunde", "interval_esantionare"]))
    if eroare_interval:
        return None, eroare_interval
    if interval is not None:
        rezultat["sampling_interval_seconds"] = interval

    rezumat = f"{indicator} măsurat la {statie}: {valoare} {unitate}"
    rezultat["measurement_summary"] = rezumat

    return rezultat, None


def raspuns_eroare(mesaj, cod=400):
    return jsonify({"eroare": mesaj}), cod


def header_allow_pentru(metode):
    return ", ".join(metode)


@app.after_request
def adauga_antete_cors(raspuns):
    raspuns.headers["Access-Control-Allow-Origin"] = "*"
    raspuns.headers["Access-Control-Allow-Methods"] = header_allow_pentru(METODE_HTTP)
    raspuns.headers["Access-Control-Allow-Headers"] = CORS_ALLOW_HEADERS
    return raspuns


def raspuns_options(ruta, metode, descriere_resursa):
    payload = {
        "tip_raspuns": "options",
        "ruta": ruta,
        "resursa": descriere_resursa,
        "metode_permise": metode,
        "nota": "Metoda OPTIONS descrie capabilitățile resursei.",
    }

    raspuns = make_response(jsonify(payload), 200)
    allow = header_allow_pentru(metode)
    raspuns.headers["Allow"] = allow
    raspuns.headers["Access-Control-Allow-Methods"] = allow
    raspuns.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return raspuns


def construieste_payload_trace(ruta, descriere_resursa, simulat_ui=False):
    payload = {
        "tip_raspuns": "trace",
        "ruta": ruta,
        "resursa": descriere_resursa,
        "metoda_reflectata": "TRACE",
        "metoda_transport": request.method,
        "query_params": request.args.to_dict(flat=True),
        "headers_primite": dict(request.headers),
        "body_primit": request.get_data(as_text=True),
        "simulare_ui": simulat_ui,
    }

    if simulat_ui:
        payload["nota"] = "Browserul blochează metoda TRACE direct; răspunsul este obținut prin endpoint helper POST."

    return payload


def raspuns_trace(ruta, descriere_resursa, metode, simulat_ui=False):
    payload = construieste_payload_trace(ruta, descriere_resursa, simulat_ui=simulat_ui)
    raspuns = make_response(jsonify(payload), 200)
    raspuns.headers["Allow"] = header_allow_pentru(metode)
    return raspuns


def raspuns_colectie():
    return {
        "tip_raspuns": "colectie_masuratori",
        "descriere": "Colecție completă de măsurători, cu metadate și elemente.",
        "operatii_colectie": METODE_COLECTIE,
        "operatii_element": METODE_ELEMENT,
        "operatii_ui": METODE_COLECTIE,
        "etichete_ui": ETICHETE_UI_OPERATII,
        "nota_operatii_ui": "În browser, TRACE este disponibil prin butoane helper care trimit POST către endpointuri dedicate.",
        "regula_date": "Operațiile de scriere folosesc exclusiv date externe (Nominatim + Open-Meteo).",
        "actiuni_semantice_colectie": ACTIUNI_SEMANTICE_COLECTIE,
        "actiuni_semantice_element": ACTIUNI_SEMANTICE_ELEMENT,
        "campuri_principale": ["id", "station", "metric", "value", "unit", "timestamp"],
        "campuri_optionale": CAMPURI_OPTIONALE,
        "numar_elemente": len(baza_masuratori),
        "elemente": lista_ordonata(),
    }


def preia_json(url, timeout_secunde=12, antete=None):
    antete_finale = {
        "User-Agent": USER_AGENT_EXTERNE,
        "Accept": "application/json",
    }
    if antete:
        antete_finale.update(antete)

    cerere = Request(url, headers=antete_finale, method="GET")
    with urlopen(cerere, timeout=timeout_secunde) as raspuns:
        continut = raspuns.read().decode("utf-8")
    return json.loads(continut)


def geocode_oras_nominatim(oras, judet=None, tara="Romania"):
    bucati = [oras]
    if judet:
        bucati.append(judet)
    if tara:
        bucati.append(tara)

    params = {
        "q": ", ".join(bucati),
        "format": "jsonv2",
        "limit": 1,
        "addressdetails": 1,
    }
    url = f"{NOMINATIM_SEARCH_URL}?{urlencode(params)}"
    rezultate = preia_json(url)

    if not isinstance(rezultate, list) or not rezultate:
        raise ValueError("Nu am găsit coordonate pentru localitatea cerută.")

    rezultat = rezultate[0]
    adresa = rezultat.get("address", {})

    try:
        latitudine = float(rezultat["lat"])
        longitudine = float(rezultat["lon"])
    except (KeyError, TypeError, ValueError) as eroare:
        raise ValueError("Răspuns invalid de la Nominatim pentru coordonate.") from eroare

    oras_rezolvat = (
        adresa.get("city")
        or adresa.get("town")
        or adresa.get("village")
        or adresa.get("municipality")
        or oras
    )
    judet_rezolvat = adresa.get("county") or adresa.get("state_district") or judet
    tara_rezolvata = adresa.get("country") or tara

    return {
        "latitude": latitudine,
        "longitude": longitudine,
        "city": oras_rezolvat,
        "county": judet_rezolvat,
        "country": tara_rezolvata,
        "display_name": rezultat.get("display_name") or oras_rezolvat,
    }


def citeste_open_meteo(latitudine, longitudine):
    parametri_curenti = ",".join([
        "temperature_2m",
        "apparent_temperature",
        "relative_humidity_2m",
        "wind_speed_10m",
        "pressure_msl",
        "precipitation",
    ])

    params = {
        "latitude": f"{latitudine:.6f}",
        "longitude": f"{longitudine:.6f}",
        "current": parametri_curenti,
        "timezone": "auto",
        "forecast_days": 1,
    }

    url = f"{OPEN_METEO_FORECAST_URL}?{urlencode(params)}"
    raspuns = preia_json(url)

    valori_curente = raspuns.get("current")
    unitati_curente = raspuns.get("current_units")
    if not isinstance(valori_curente, dict) or not isinstance(unitati_curente, dict):
        raise ValueError("Răspuns invalid de la Open-Meteo.")

    return {
        "current": valori_curente,
        "current_units": unitati_curente,
        "timezone": raspuns.get("timezone"),
    }


def payloaduri_din_open_meteo(info_geo, meteo):
    valori_curente = meteo.get("current", {})
    unitati_curente = meteo.get("current_units", {})
    moment = valori_curente.get("time") or acum_utc_iso()

    locatie_text = f"lat {info_geo['latitude']:.4f}, lon {info_geo['longitude']:.4f}"
    statie = info_geo.get("display_name") or info_geo.get("city") or "Open-Meteo"
    oras = info_geo.get("city")
    judet = info_geo.get("county")

    baza_payload = {
        "statie": statie,
        "oras": oras,
        "judet": judet,
        "locatie": locatie_text,
        "platforma_sursa": "open-meteo",
        "descriere": f"Import automat din Open-Meteo pentru {oras or 'localitatea selectată'}.",
        "moment_inregistrare": moment,
    }

    payloaduri = []
    for metrica in MAPARE_METRICI_OPEN_METEO:
        cheie_api = metrica["cheie"]
        valoare = valori_curente.get(cheie_api)
        if valoare is None:
            continue

        if metrica.get("fara_valori_negative"):
            if not isinstance(valoare, (int, float)) or valoare < 0:
                continue

        unitate = unitati_curente.get(cheie_api) or metrica["unitate_implicita"]
        payload = {
            **baza_payload,
            "indicator": metrica["indicator"],
            "valoare": valoare,
            "unitate": unitate,
            "etichete": ["extern", "open-meteo", "nominatim", cheie_api],
        }
        payloaduri.append(payload)

    return payloaduri


def text_normalizat(valoare):
    if not isinstance(valoare, str):
        return ""

    baza = unicodedata.normalize("NFD", valoare.lower())
    fara_diacritice = "".join(caracter for caracter in baza if unicodedata.category(caracter) != "Mn")
    return " ".join(fara_diacritice.split())


def extrage_localizare(payload):
    oras = text_scurt(prima_valoare(payload, ["oras", "city"])) or "Iasi"
    judet = text_scurt(prima_valoare(payload, ["judet", "county", "state"]))
    tara = text_scurt(prima_valoare(payload, ["tara", "country"])) or "Romania"
    return oras, judet, tara


def pregateste_date_externe(payload):
    oras, judet, tara = extrage_localizare(payload)
    info_geo = geocode_oras_nominatim(oras, judet, tara)
    meteo = citeste_open_meteo(info_geo["latitude"], info_geo["longitude"])
    candidati = payloaduri_din_open_meteo(info_geo, meteo)

    elemente_validate = []
    elemente_ignorate = []
    for candidat in candidati:
        element, mesaj = valideaza_payload(candidat)
        if mesaj:
            elemente_ignorate.append({
                "indicator": candidat.get("indicator"),
                "motiv": mesaj,
            })
            continue

        elemente_validate.append(element)

    return {
        "oras_cerut": oras,
        "info_geo": info_geo,
        "elemente_validate": elemente_validate,
        "elemente_ignorate": elemente_ignorate,
    }


def extrage_date_externe_din_request():
    payload = request.get_json(silent=True)
    if payload is None:
        payload = {}
    elif not isinstance(payload, dict):
        return None, None, raspuns_eroare("Body trebuie să fie obiect JSON.", 400)

    try:
        date_externe = pregateste_date_externe(payload)
    except ValueError as eroare:
        return payload, None, raspuns_eroare(str(eroare), 400)
    except (HTTPError, URLError, TimeoutError, OSError):
        return payload, None, raspuns_eroare("Sursa externă este indisponibilă momentan.", 502)

    return payload, date_externe, None


def selecteaza_element_extern(elemente_validate, payload_client):
    if not elemente_validate:
        return None

    indicator_cerut = text_scurt(prima_valoare(payload_client, ["indicator", "metric", "parametru"]))
    if not indicator_cerut:
        return elemente_validate[0]

    indicator_cerut_normalizat = text_normalizat(indicator_cerut)

    for element in elemente_validate:
        metric = element.get("metric")
        metric_normalizat = text_normalizat(metric)
        if (
            metric_normalizat == indicator_cerut_normalizat
            or indicator_cerut_normalizat in metric_normalizat
            or metric_normalizat in indicator_cerut_normalizat
        ):
            return element

    return elemente_validate[0]


def gaseste_id_dupa_metric_si_oras(metric_cautat, oras_cautat):
    metric_normalizat = text_normalizat(metric_cautat)
    oras_normalizat = text_normalizat(oras_cautat)

    if not metric_normalizat:
        return None

    for item_id in sorted(baza_masuratori.keys()):
        element = baza_masuratori[item_id]
        metric_curent = text_normalizat(element.get("metric"))
        if metric_curent != metric_normalizat:
            continue

        oras_curent = text_normalizat(element.get("city"))
        if oras_normalizat:
            if oras_curent == oras_normalizat:
                return item_id
        else:
            return item_id

    return None


def salveaza_element(element, item_id=None):
    global urmatorul_id

    if item_id is None:
        item_id = urmatorul_id

    if item_id >= urmatorul_id:
        urmatorul_id = item_id + 1

    creat = {"id": item_id, **element}
    baza_masuratori[item_id] = creat
    return creat


def aplica_patch_element(element_baza, campuri_noi):
    element_actualizat = {**element_baza}
    campuri_actualizate = []

    for camp, valoare in campuri_noi.items():
        if element_actualizat.get(camp) != valoare:
            element_actualizat[camp] = valoare
            campuri_actualizate.append(camp)

    return element_actualizat, sorted(campuri_actualizate)


def raspuns_creare(payload, item_id):
    raspuns = make_response(jsonify(payload), 201)
    raspuns.headers["Location"] = f"/masuratori/{item_id}"
    return raspuns


def extrage_element_extern_din_request(actiune, mesaj_eroare, extra=None, adauga_oras_cerut=False):
    payload, date_externe, raspuns_eroare_externa = extrage_date_externe_din_request()
    if raspuns_eroare_externa:
        return None, None, raspuns_eroare_externa

    element = selecteaza_element_extern(date_externe["elemente_validate"], payload)
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

    return element, date_externe, None


@app.route("/", methods=["GET"])
def acasa():
    return render_template("panou_masuratori.html")


@app.route("/measurements/trace/collection", methods=["POST"])
@app.route("/masuratori/trace/colectie", methods=["POST"])
def endpoint_trace_ui_colectie():
    return raspuns_trace("/masuratori", "colectie_masuratori", METODE_COLECTIE, simulat_ui=True)


@app.route("/measurements/trace/item/<int:item_id>", methods=["POST"])
@app.route("/masuratori/trace/element/<int:item_id>", methods=["POST"])
def endpoint_trace_ui_element(item_id):
    if item_id <= 0:
        return raspuns_eroare("item_id trebuie să fie pozitiv.", 400)
    return raspuns_trace(f"/masuratori/{item_id}", f"element_masurare_{item_id}", METODE_ELEMENT, simulat_ui=True)


@app.route("/measurements/external-preview", methods=["POST"])
@app.route("/masuratori/preview-extern", methods=["POST"])
def endpoint_preview_extern():
    _, date_externe, raspuns_eroare_externa = extrage_date_externe_din_request()
    if raspuns_eroare_externa:
        return raspuns_eroare_externa

    elemente_preview = [
        {"id_preview": index, **element}
        for index, element in enumerate(date_externe["elemente_validate"], start=1)
    ]

    return jsonify({
        "mesaj": "Preview date externe generat.",
        "actiune": "preview_date_externe",
        "sursa": "open-meteo",
        "oras_cerut": date_externe["oras_cerut"],
        "oras_rezolvat": date_externe["info_geo"].get("city"),
        "numar_preview": len(elemente_preview),
        "numar_ignorate": len(date_externe["elemente_ignorate"]),
        "elemente_preview": elemente_preview,
        "elemente_ignorate": date_externe["elemente_ignorate"],
    }), 200


@app.route("/measurements/synchronize", methods=["POST"])
@app.route("/masuratori/sincronizeaza", methods=["POST"])
def endpoint_sincronizare_externa():
    _, date_externe, raspuns_eroare_externa = extrage_date_externe_din_request()
    if raspuns_eroare_externa:
        return raspuns_eroare_externa

    elemente_adaugate = [
        salveaza_element(element)
        for element in date_externe["elemente_validate"]
    ]
    elemente_ignorate = date_externe["elemente_ignorate"]

    if not elemente_adaugate:
        return jsonify({
            "eroare": "Nu am putut importa măsurători valide din sursa externă.",
            "actiune": "sincronizeaza_din_open_meteo",
            "oras_cerut": date_externe["oras_cerut"],
            "numar_ignorate": len(elemente_ignorate),
            "elemente_ignorate": elemente_ignorate,
        }), 502

    return jsonify({
        "mesaj": "Sincronizare externă finalizată.",
        "actiune": "sincronizeaza_din_open_meteo",
        "sursa": "open-meteo",
        "oras_cerut": date_externe["oras_cerut"],
        "oras_rezolvat": date_externe["info_geo"].get("city"),
        "numar_adaugate": len(elemente_adaugate),
        "numar_ignorate": len(elemente_ignorate),
        "ids_generate": [element["id"] for element in elemente_adaugate],
        "elemente_adaugate": elemente_adaugate,
        "elemente_ignorate": elemente_ignorate,
    }), 201


@app.route("/measurements", methods=METODE_COLECTIE)
@app.route("/masuratori", methods=METODE_COLECTIE)
def endpoint_colectie():
    global baza_masuratori
    global urmatorul_id

    if request.method == "OPTIONS":
        return raspuns_options("/masuratori", METODE_COLECTIE, "colectie_masuratori")

    if request.method == "TRACE":
        return raspuns_trace("/masuratori", "colectie_masuratori", METODE_COLECTIE)

    if request.method == "HEAD":
        raspuns = make_response("", 200)
        raspuns.headers["Allow"] = header_allow_pentru(METODE_COLECTIE)
        raspuns.headers["X-Numar-Elemente"] = str(len(baza_masuratori))
        return raspuns

    if request.method == "GET":
        return jsonify(raspuns_colectie()), 200

    if request.method == "POST":
        element, date_externe, raspuns_eroare_externa = extrage_element_extern_din_request(
            "post_colectie_din_api_extern",
            "Nu am putut extrage niciun element valid din sursa externă.",
            adauga_oras_cerut=True,
        )
        if raspuns_eroare_externa:
            return raspuns_eroare_externa

        creat = salveaza_element(element)

        return raspuns_creare(
            {
                **creat,
                "actiune": "post_colectie_din_api_extern",
                "sursa": "open-meteo",
                "oras_rezolvat": date_externe["info_geo"].get("city"),
            },
            creat["id"],
        )

    if request.method == "PUT":
        _, date_externe, raspuns_eroare_externa = extrage_date_externe_din_request()
        if raspuns_eroare_externa:
            return raspuns_eroare_externa

        if not date_externe["elemente_validate"]:
            return jsonify({
                "eroare": "Nu am putut importa măsurători valide pentru înlocuirea colecției.",
                "actiune": "put_colectie_din_api_extern",
                "oras_cerut": date_externe["oras_cerut"],
                "numar_ignorate": len(date_externe["elemente_ignorate"]),
                "elemente_ignorate": date_externe["elemente_ignorate"],
            }), 502

        date_noi = {
            index: {"id": index, **element}
            for index, element in enumerate(date_externe["elemente_validate"], start=1)
        }

        baza_masuratori = date_noi
        urmatorul_id = len(baza_masuratori) + 1

        raspuns = raspuns_colectie()
        raspuns["actiune"] = "put_colectie_din_api_extern"
        raspuns["sursa"] = "open-meteo"
        raspuns["oras_rezolvat"] = date_externe["info_geo"].get("city")
        raspuns["numar_ignorate"] = len(date_externe["elemente_ignorate"])
        raspuns["elemente_ignorate"] = date_externe["elemente_ignorate"]
        return jsonify(raspuns), 200

    if request.method == "PATCH":
        element_nou, date_externe, raspuns_eroare_externa = extrage_element_extern_din_request(
            "patch_colectie_din_api_extern",
            "Nu am putut extrage niciun element valid pentru patch din sursa externă.",
            adauga_oras_cerut=True,
        )
        if raspuns_eroare_externa:
            return raspuns_eroare_externa
        id_tinta = gaseste_id_dupa_metric_si_oras(element_nou.get("metric"), element_nou.get("city"))

        status_patch = "adaugat"
        cod_status = 201
        campuri_actualizate = []

        if id_tinta is None:
            element_final = salveaza_element(element_nou)
            id_tinta = element_final["id"]
            campuri_actualizate = sorted(list(element_nou.keys()))
        else:
            element_actualizat, campuri_actualizate = aplica_patch_element(baza_masuratori[id_tinta], element_nou)
            baza_masuratori[id_tinta] = element_actualizat
            status_patch = "actualizat"
            cod_status = 200

        element_final = baza_masuratori[id_tinta]
        payload_raspuns = {
            "actiune": "patch_colectie_din_api_extern",
            "status_patch": status_patch,
            "id_tinta": id_tinta,
            "campuri_actualizate": campuri_actualizate,
            "sursa": "open-meteo",
            "oras_rezolvat": date_externe["info_geo"].get("city"),
            "element": element_final,
        }

        if cod_status == 201:
            return raspuns_creare(payload_raspuns, id_tinta)

        return jsonify(payload_raspuns), 200

    if request.method == "DELETE":
        sterse = len(baza_masuratori)
        baza_masuratori = {}
        urmatorul_id = 1
        return jsonify({
            "mesaj": "Toate măsurătorile din colecție au fost șterse.",
            "numar_sterse": sterse,
            "colectie_curenta": [],
        }), 200

    return raspuns_eroare("Metodă HTTP neacceptată pe colecție.", 405)


@app.route("/measurements/<int:item_id>", methods=METODE_ELEMENT)
@app.route("/masuratori/<int:item_id>", methods=METODE_ELEMENT)
def endpoint_element(item_id):
    if item_id <= 0:
        return raspuns_eroare("item_id trebuie să fie pozitiv.", 400)

    if request.method == "OPTIONS":
        return raspuns_options(f"/masuratori/{item_id}", METODE_ELEMENT, f"element_masurare_{item_id}")

    if request.method == "TRACE":
        return raspuns_trace(f"/masuratori/{item_id}", f"element_masurare_{item_id}", METODE_ELEMENT)

    if request.method == "HEAD":
        element = baza_masuratori.get(item_id)
        exista = element is not None
        cod = 200 if exista else 404

        raspuns = make_response("", cod)
        raspuns.headers["Allow"] = header_allow_pentru(METODE_ELEMENT)
        raspuns.headers["X-Item-Id"] = str(item_id)
        raspuns.headers["X-Item-Exists"] = "true" if exista else "false"
        if exista:
            raspuns.headers["X-Item-Metric"] = str(element.get("metric", ""))
        return raspuns

    if request.method == "GET":
        element = baza_masuratori.get(item_id)
        if element is None:
            return raspuns_eroare("Elementul cerut nu există.", 404)
        return jsonify(element), 200

    if request.method == "POST":
        if item_id in baza_masuratori:
            return raspuns_eroare("Elementul există deja pentru acest id.", 409)

        element, _, raspuns_eroare_externa = extrage_element_extern_din_request(
            "post_element_din_api_extern",
            "Nu am putut extrage un element valid pentru acest id din sursa externă.",
            extra={"id_cerut": item_id},
        )
        if raspuns_eroare_externa:
            return raspuns_eroare_externa

        creat = salveaza_element(element, item_id=item_id)

        return raspuns_creare(creat, item_id)

    if request.method == "PUT":
        element, _, raspuns_eroare_externa = extrage_element_extern_din_request(
            "put_element_din_api_extern",
            "Nu am putut extrage un element valid pentru actualizare din sursa externă.",
            extra={"id_cerut": item_id},
        )
        if raspuns_eroare_externa:
            return raspuns_eroare_externa

        exista = item_id in baza_masuratori
        actualizat = salveaza_element(element, item_id=item_id)

        if exista:
            return jsonify(actualizat), 200

        return raspuns_creare(actualizat, item_id)

    if request.method == "PATCH":
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
        element_actualizat, campuri_actualizate = aplica_patch_element(element_existent, element_nou)

        baza_masuratori[item_id] = element_actualizat

        return jsonify({
            "actiune": "patch_element_din_api_extern",
            "id_actualizat": item_id,
            "campuri_actualizate": campuri_actualizate,
            "sursa": "open-meteo",
            "oras_rezolvat": date_externe["info_geo"].get("city"),
            "element": element_actualizat,
        }), 200

    if request.method == "DELETE":
        element = baza_masuratori.get(item_id)
        if element is None:
            return raspuns_eroare("Elementul cerut nu există.", 404)

        del baza_masuratori[item_id]
        return jsonify({
            "mesaj": "Elementul selectat a fost șters.",
            "id_sters": item_id,
        }), 200

    return raspuns_eroare("Metodă HTTP neacceptată pe element.", 405)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
