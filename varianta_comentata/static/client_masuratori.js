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

// Extrage id-ul curent din input și validează că este întreg pozitiv.
function idElementCurent() {
  const input = element("itemId") // Obține controlul numeric cu id-ul elementului.
  const id = idPozitiv(input?.value.trim()) // Normalizează valoarea la un id valid.
  if (id === null) {
    throw new Error("ID-ul trebuie să fie un număr întreg pozitiv") // Aruncă eroare controlată pentru handlerul global.
  }
  return id // Returnează id-ul numeric valid.
}

// Construiește ruta /masuratori/{id} pe baza inputului de id.
function caleaElement() {
  return `/masuratori/${idElementCurent()}` // Template literal pentru ruta finală.
}

// Construiește body pentru endpointurile care cer localizare + indicator.
function construiestePayloadExtern(idIndicator) {
  const body = {} // Obiectul JSON care va fi trimis la backend.
  const oras = element("externalCity")?.value.trim() // Citește orașul din input.
  const tara = element("externalCountry")?.value.trim() // Citește țara din input.
  const indicator = idIndicator ? element(idIndicator)?.value.trim() : "" // Citește indicatorul selectat.

  if (oras) {
    body.oras = oras // Scrie doar dacă valoarea este nevidă.
  }
  if (tara) {
    body.tara = tara // Scrie doar dacă valoarea este nevidă.
  }
  if (indicator) {
    body.indicator = indicator // Scrie doar dacă valoarea este nevidă.
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

// Leagă toate acțiunile API printr-un singur tablou declarativ.
function leagaActiuniApi() {
  const actiuni = [
    { idButon: "getCollection", metoda: "GET", ruta: () => RUTA_COLECTIE },
    { idButon: "headCollection", metoda: "HEAD", ruta: () => RUTA_COLECTIE },
    { idButon: "deleteCollection", metoda: "DELETE", ruta: () => RUTA_COLECTIE },
    { idButon: "optionsCollection", metoda: "OPTIONS", ruta: () => RUTA_COLECTIE },

    { idButon: "postCollection", metoda: "POST", ruta: () => RUTA_COLECTIE, indicator: "externalMetric" },
    { idButon: "putCollection", metoda: "PUT", ruta: () => RUTA_COLECTIE, indicator: "externalMetric" },
    { idButon: "patchCollection", metoda: "PATCH", ruta: () => RUTA_COLECTIE, indicator: "externalMetric" },

    { idButon: "getItem", metoda: "GET", ruta: caleaElement },
    { idButon: "headItem", metoda: "HEAD", ruta: caleaElement },
    { idButon: "deleteItem", metoda: "DELETE", ruta: caleaElement },
    { idButon: "optionsItem", metoda: "OPTIONS", ruta: caleaElement },

    { idButon: "postItem", metoda: "POST", ruta: caleaElement, indicator: "itemMetric" },
    { idButon: "putItem", metoda: "PUT", ruta: caleaElement, indicator: "itemMetric" },
    { idButon: "patchItem", metoda: "PATCH", ruta: caleaElement, indicator: "itemMetric" },

    { idButon: "syncExternal", metoda: "POST", ruta: () => "/masuratori/sincronizeaza", indicator: "externalMetric" },
    { idButon: "previewExternal", metoda: "POST", ruta: () => "/masuratori/preview-extern", indicator: "externalMetric" },
    { idButon: "traceCollection", metoda: "POST", ruta: () => "/masuratori/trace/colectie" },
    { idButon: "traceItem", metoda: "POST", ruta: () => `/masuratori/trace/element/${idElementCurent()}` },
  ]

  for (const actiune of actiuni) {
    leagaButon(actiune.idButon, () => {
      const body = actiune.indicator ? construiestePayloadExtern(actiune.indicator) : undefined
      return apeleazaApi(actiune.metoda, actiune.ruta(), body)
    })
  }
}

leagaActiuniApi()

// Populează cele două dropdown-uri cu aceeași listă de indicatori.
for (const idSelect of ["externalMetric", "itemMetric"]) {
  populeazaSelectIndicator(idSelect) // Populează fiecare dropdown cu lista standard de indicatori.
}
