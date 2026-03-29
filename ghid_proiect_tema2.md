# Ghid proiect Tema 2 TAD 2026

Implementare REST în Flask pentru măsurători, cu client web local pentru testare manuală.

## Fișiere principale

- `serviciu_masuratori.py`
- `templates/panou_masuratori.html`
- `static/client_masuratori.js`
- `requirements.txt`

## Ce oferă API-ul

- răspunsuri JSON
- verbe GET, HEAD, POST, PUT, PATCH, DELETE, OPTIONS, TRACE pe colecție și pe element
- surse externe reale de date prin Nominatim + Open-Meteo
- operațiile de scriere folosesc exclusiv date externe (fără payload manual de măsurătoare)
- endpoint semantic pentru sincronizare: `POST /masuratori/sincronizeaza`
- endpoint de preview extern: `POST /masuratori/preview-extern`
- coduri de răspuns folosite: 200, 201, 400, 404, 409, 502
- două variante de rută: în engleză (`/measurements`) și în română (`/masuratori`)
- butoanele din UI afișează explicit metoda + endpoint (ex: `GET /masuratori`, `PATCH /masuratori/{id}`)
- butoane dedicate pentru `HEAD`, `PATCH`, `OPTIONS` (capabilități) și `TRACE` (diagnostic)
- acțiunile duplicate au fost eliminate (nu există două butoane cu același request)
- pentru browser, `TRACE` este expus și prin endpointuri helper cu `POST`

## Rute disponibile

### Colecție

- `GET /masuratori` (alias: `GET /measurements`) — întoarce toată colecția de măsurători, împreună cu metadatele utile.
- `HEAD /masuratori` (alias: `HEAD /measurements`) — întoarce doar antetele (fără body), util pentru verificare rapidă.
- `POST /masuratori` (alias: `POST /measurements`) — creează o măsurătoare nouă în colecție folosind date din API extern (Open-Meteo), cu `id` generat automat.
- `PUT /masuratori` (alias: `PUT /measurements`) — înlocuiește complet colecția curentă cu setul curent de date externe.
- `PATCH /masuratori` (alias: `PATCH /measurements`) — actualizare parțială pe colecție (actualizează un element existent după metric+city sau adaugă unul nou).
- `DELETE /masuratori` (alias: `DELETE /measurements`) — golește întreaga colecție și confirmă câte elemente au fost șterse.
- `OPTIONS /masuratori` (alias: `OPTIONS /measurements`) — descrie metodele permise pentru resursa colecție.
- `TRACE /masuratori` (alias: `TRACE /measurements`) — reflectă detalii diagnostice ale requestului pentru colecție.

### Preview date externe

- `POST /masuratori/preview-extern` (alias: `POST /measurements/external-preview`) — aduce datele externe, le normalizează și le întoarce pentru verificare, fără a le salva.

### Acțiune semantică externă

- `POST /masuratori/sincronizeaza` (alias: `POST /measurements/synchronize`) — sincronizează date externe reale din Open-Meteo, folosind geocodare Nominatim.

Body exemplu:

```json
{
	"oras": "Iasi",
	"tara": "Romania"
}
```

Răspuns exemplu (scurtat):

```json
{
	"mesaj": "Sincronizare externă finalizată.",
	"actiune": "sincronizeaza_din_open_meteo",
	"sursa": "open-meteo",
	"numar_adaugate": 4,
	"ids_generate": [1, 2, 3, 4]
}
```

Notă: dacă localitatea nu poate fi geocodată sau sursa externă nu răspunde, API-ul întoarce eroare explicită (`400` sau `502`).

### Element individual

- `GET /masuratori/<id>` (alias: `GET /measurements/<id>`) — citește un singur element după identificator.
- `HEAD /masuratori/<id>` (alias: `HEAD /measurements/<id>`) — întoarce antete pentru verificare existență element.
- `POST /masuratori/<id>` (alias: `POST /measurements/<id>`) — creează explicit un element pe `id`-ul dat din date externe, dacă acel `id` nu există deja.
- `PUT /masuratori/<id>` (alias: `PUT /measurements/<id>`) — actualizează (sau creează) elementul din date externe pentru `id`.
- `PATCH /masuratori/<id>` (alias: `PATCH /measurements/<id>`) — actualizare parțială a unui element existent din date externe.
- `DELETE /masuratori/<id>` (alias: `DELETE /measurements/<id>`) — șterge elementul selectat și întoarce confirmarea operației.
- `OPTIONS /masuratori/<id>` (alias: `OPTIONS /measurements/<id>`) — descrie metodele permise pentru resursa element.
- `TRACE /masuratori/<id>` (alias: `TRACE /measurements/<id>`) — reflectă detalii diagnostice ale requestului pentru element.

### Endpointuri helper TRACE pentru UI

- `POST /masuratori/trace/colectie` (alias: `POST /measurements/trace/collection`) — simulare TRACE pentru colecție, compatibilă cu browserul.
- `POST /masuratori/trace/element/<id>` (alias: `POST /measurements/trace/item/<id>`) — simulare TRACE pentru un element, compatibilă cu browserul.

## Payload de control pentru scriere externă

Pentru operațiile de scriere (`POST`/`PUT`/`PATCH`) nu se trimit direct valori de măsurare; se trimit doar câmpuri de control pentru API-ul extern:

- `oras` / `city`
- `tara` / `country` (opțional)
- `indicator` / `metric` / `parametru` (opțional, pentru alegerea unui metric preferat)

## Schema de ieșire a măsurătorilor

Măsurătorile salvate în API respectă în continuare schema internă și folosesc cheile de mai jos:

- stație: `station` sau `statie` sau `punct_masurare`
- indicator: `metric` sau `indicator` sau `parametru`
- valoare: `value` sau `valoare` sau `valoare_masurata`
- unitate: `unit` sau `unitate` sau `unitate_masura`

## Câmpuri opționale acceptate

- timp: `timestamp` / `moment` / `moment_inregistrare`
- locație: `location` / `locatie` / `pozitie_instalare`
- descriere: `description` / `descriere` / `detalii`
- categorie: `category` / `categorie` / `domeniu`
- senzor: `sensor_name`, `sensor_model`, `sensor_manufacturer`
- responsabil: `operator_name` / `responsabil` / `persoana_responsabila`
- zonă: `city` / `oras`, `county` / `judet`
- sursă: `source_system` / `sursa_date` / `platforma_sursa`
- listă etichete: `tags` / `etichete` / `cuvinte_cheie`
- frecvență: `sampling_interval_seconds` / `frecventa_secunde` / `interval_esantionare`

## Rulare locală

Instalare:

python -m pip install -r requirements.txt

Pornire server:

python serviciu_masuratori.py

Interfață testare:

http://127.0.0.1:5000

## Stilul proiectului

- implementare simplă, directă
- fără fișiere de teste automate
