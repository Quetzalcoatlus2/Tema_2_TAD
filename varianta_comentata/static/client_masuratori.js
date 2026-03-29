// Helper pentru acces rapid la elemente din DOM după id.
// Sintaxă: funcție săgeată (arrow function) cu return implicit.
const element = (id) => document.getElementById(id) // Primește id-ul și întoarce elementul DOM corespunzător.

// Referințe reutilizate pentru zona de status și zona de output JSON/text.
const statusElement = element("status") // Cache pentru zona unde afișăm statusul HTTP.
const outputElement = element("output") // Cache pentru zona unde afișăm payload-ul răspunsului.

// Lista de indicatori afișați în dropdown-uri.
// Fiecare element este un obiect literal { value, text }.
const OPTIUNI_INDICATOR = [
  {
    value: "umiditate relativă", // Valoarea trimisă în body-ul API.
    text: "umiditate relativă (relative_humidity_2m)", // Textul afișat în UI pentru utilizator.
  },
  {
    value: "viteză vânt la 10m", // Cheie semantică folosită la selecție.
    text: "viteză vânt la 10m (wind_speed_10m)", // Etichetă prietenoasă + cod meteo.
  },
  {
    value: "presiune atmosferică la nivelul mării", // Indicatorul canonic pentru presiune.
    text: "presiune atmosferică la nivelul mării (pressure_msl)", // Eticheta din dropdown.
  },
  {
    value: "precipitații curente", // Alias intern pentru precipitații.
    text: "precipitații curente (precipitation)", // Label explicativ + cheie API.
  },
  {
    value: "temperatură aer exterior", // Numele intern al metricii de temperatură.
    text: "temperatură aer exterior (temperature_2m)", // Text explicit afișat în listă.
  },
]

// Populează un <select> pe baza listei OPTIUNI_INDICATOR.
function populeazaSelectIndicator(idSelect) {
  const select = element(idSelect) // Caută elementul <select> după id.
  if (!select) {
    return // Iese dacă id-ul nu există în DOM.
  }

  // for...of iterează direct valorile din array.
  for (const optiune of OPTIUNI_INDICATOR) {
    const option = document.createElement("option") // Creează nod <option> nou.
    option.value = optiune.value // Setează valoarea care va fi trimisă în request.
    option.textContent = optiune.text // Setează textul vizibil pentru utilizator.
    select.appendChild(option) // Atașează opțiunea la dropdown.
  }
}

// Afișează sumarul răspunsului HTTP.
// Operatorul ternar alege formatul statusului în funcție de existența headerului Location.
function afiseazaRezultat(response, payload) {
  const location = response.headers.get("Location") // Citește header-ul Location dacă există.
  const status = `Status: ${response.status} ${response.statusText}` // Formatează codul + mesajul HTTP.
  statusElement.textContent = location ? `${status} | Location: ${location}` : status // Ternar: cu/fără Location.

  // Dacă payload-ul e string, îl afișăm direct; altfel serializăm JSON cu indentare 2 spații.
  outputElement.textContent = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2) // Afișează text brut sau JSON pretty.
}

function afiseazaEroare(error) {
  statusElement.textContent = "Status: request eșuat" // Mesaj generic de eșec în zona de status.
  outputElement.textContent = error.message // Mesajul efectiv al excepției.
}

// Normalizează orice input la id pozitiv:
// - parseInt(..., 10) = parse decimal explicit;
// - returnează null dacă nu e întreg > 0.
function idPozitiv(valoare) {
  const id = Number.parseInt(String(valoare), 10) // Conversie explicită la întreg în baza 10.
  return Number.isInteger(id) && id > 0 ? id : null // Ternar: returnează id valid sau null.
}

// Dacă id-ul primit este valid, actualizează inputul itemId.
function seteazaItemIdDacaValid(idPotential) {
  const input = element("itemId") // Referința la input-ul de id.
  const id = idPozitiv(idPotential) // Normalizează candidatul la id valid.
  if (!input || id === null) {
    return false // Semnalizează că nu s-a putut actualiza input-ul.
  }

  input.value = String(id) // Scrie id-ul valid în input.
  return true // Semnalizează succesul actualizării.
}

// După un răspuns de la /masuratori..., încearcă să actualizeze automat id-ul curent.
function sincronizeazaItemIdDinRaspuns(path, payload) {
  if (typeof path !== "string" || !path.startsWith("/masuratori") || !payload || typeof payload !== "object") {
    return // Iese dacă răspunsul nu aparține endpoint-urilor țintă.
  }

  // Spread (...) extinde array-ul ids_generate în lista de candidați.
  const idPosibile = [
    ...(Array.isArray(payload.ids_generate) ? payload.ids_generate : []), // Spread pentru lista ids_generate (dacă există).
    payload.id, // Caz create simplu.
    payload.id_tinta, // Caz patch colecție.
    payload.id_actualizat, // Caz patch element.
  ]

  for (const id of idPosibile) {
    if (seteazaItemIdDacaValid(id)) {
      return // Se oprește la primul id valid setat cu succes.
    }
  }
}

// Wrapper generic pentru apel API.
// async/await simplifică lucrul cu promisiuni (Promises).
async function apeleazaApi(metoda, ruta, body) {
  const options = { method: metoda } // Inițializează obiectul options pentru fetch.
  if (body !== undefined) {
    options.headers = { "Content-Type": "application/json" } // Setează tipul body-ului.
    options.body = JSON.stringify(body) // Serializează body-ul JS în JSON text.
  }

  const response = await fetch(ruta, options) // Trimite request-ul HTTP către backend.
  const contentType = response.headers.get("content-type") || "" // Citește content-type-ul răspunsului.
  const payload = contentType.includes("application/json") ? await response.json() : await response.text() // Parsează dinamic JSON/text.

  sincronizeazaItemIdDinRaspuns(ruta, payload) // Dacă se găsește id relevant, îl sincronizează în input.
  afiseazaRezultat(response, payload) // Afișează răspunsul în UI.
}

// Construiește ruta /masuratori/{id} pe baza inputului de id.
function caleaElement() {
  const input = element("itemId") // Obține controlul numeric cu id-ul elementului.
  // Optional chaining (?.) evită eroare dacă input e null.
  const id = idPozitiv(input?.value.trim()) // Preia valoarea, face trim și validează numeric.
  if (id === null) {
    throw new Error("ID-ul trebuie să fie un număr întreg pozitiv") // Aruncă eroare controlată pentru handlerul global.
  }
  return `/masuratori/${id}` // Template literal pentru ruta finală.
}

// Construiește body pentru endpointurile care cer localizare + indicator.
function construiestePayloadExtern(idIndicator) {
  const mapari = [
    ["externalCity", "oras"], // Mapează input UI -> cheie JSON `oras`.
    ["externalCountry", "tara"], // Mapează input UI -> cheie JSON `tara`.
    [idIndicator, "indicator"], // Mapează select-ul curent -> `indicator`.
  ]

  const body = {} // Obiectul JSON care va fi trimis la backend.
  // Destructuring în for...of: [idInput, camp]
  for (const [idInput, camp] of mapari) {
    if (!idInput) {
      continue // Salt defensiv dacă idInput e gol/null.
    }

    const valoare = element(idInput)?.value.trim() || "" // Citește și normalizează valoarea inputului.
    if (valoare) {
      body[camp] = valoare // Setează dinamic proprietatea obiectului prin indexare body[camp].
    }
  }
  return body // Returnează payload-ul completat parțial.
}

// Leagă un buton la o acțiune async și centralizează tratarea erorilor.
function leagaButon(idButon, actiuneAsync) {
  const buton = element(idButon) // Caută butonul după id în DOM.
  if (!buton) {
    return // Iese dacă butonul lipsește din template.
  }

  buton.addEventListener("click", async () => {
    try {
      await actiuneAsync() // Rulează acțiunea asincronă asociată butonului.
    } catch (error) {
      afiseazaEroare(error) // Afișează eroarea în UI, fără crash în consolă.
    }
  })
}

// Config declarativ pentru acțiuni de colecție/item.
const RUTA_COLECTIE = "/masuratori" // Rută de bază pentru operații pe colecție.
const METODE_COLECTIE_FARA_BODY = {
  getCollection: "GET", // Buton citire colecție.
  headCollection: "HEAD", // Buton antete colecție.
  deleteCollection: "DELETE", // Buton ștergere colecție.
  optionsCollection: "OPTIONS", // Buton introspecție metode permise.
}
const METODE_ITEM_FARA_BODY = {
  getItem: "GET", // Buton citire item.
  headItem: "HEAD", // Buton antete item.
  deleteItem: "DELETE", // Buton ștergere item.
  optionsItem: "OPTIONS", // Buton metode permise item.
}
const METODE_COLECTIE_CU_BODY = {
  postCollection: "POST", // Buton create în colecție.
  putCollection: "PUT", // Buton înlocuire colecție.
  patchCollection: "PATCH", // Buton patch colecție.
}
const METODE_ITEM_CU_BODY = {
  postItem: "POST", // Buton create pe id fix.
  putItem: "PUT", // Buton upsert pe id.
  patchItem: "PATCH", // Buton patch pe id.
}

// Object.entries(...) transformă obiectul într-un array de perechi [cheie, valoare].
for (const [idButon, metoda] of Object.entries(METODE_COLECTIE_FARA_BODY)) {
  leagaButon(idButon, () => apeleazaApi(metoda, RUTA_COLECTIE)) // Leagă acțiunile GET/HEAD/DELETE/OPTIONS pe colecție.
}
for (const [idButon, metoda] of Object.entries(METODE_COLECTIE_CU_BODY)) {
  leagaButon(idButon, () => apeleazaApi(metoda, RUTA_COLECTIE, construiestePayloadExtern("externalMetric"))) // Leagă POST/PUT/PATCH cu body extern.
}
for (const [idButon, metoda] of Object.entries(METODE_ITEM_FARA_BODY)) {
  leagaButon(idButon, () => apeleazaApi(metoda, caleaElement())) // Leagă GET/HEAD/DELETE/OPTIONS pe item.
}
for (const [idButon, metoda] of Object.entries(METODE_ITEM_CU_BODY)) {
  leagaButon(idButon, () => apeleazaApi(metoda, caleaElement(), construiestePayloadExtern("itemMetric"))) // Leagă POST/PUT/PATCH pe item cu body.
}

leagaButon("syncExternal", () => apeleazaApi("POST", "/masuratori/sincronizeaza", construiestePayloadExtern("externalMetric"))) // Importă în colecție din surse externe.
leagaButon("previewExternal", () => apeleazaApi("POST", "/masuratori/preview-extern", construiestePayloadExtern("externalMetric"))) // Preview fără persistare.
leagaButon("traceCollection", () => apeleazaApi("POST", "/masuratori/trace/colectie")) // TRACE helper pentru colecție.
leagaButon("traceItem", () => {
  const id = caleaElement().split("/").pop() // Extrage segmentul final (id) din ruta item.
  return apeleazaApi("POST", `/masuratori/trace/element/${id}`) // Apelează TRACE helper pentru item.
})

// Populează cele două dropdown-uri cu aceeași listă de indicatori.
for (const idSelect of ["externalMetric", "itemMetric"]) {
  populeazaSelectIndicator(idSelect) // Populează fiecare dropdown cu lista standard de indicatori.
}
