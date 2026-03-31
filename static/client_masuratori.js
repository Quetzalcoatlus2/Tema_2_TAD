const element = (id) => document.getElementById(id)

const statusElement = element("status")
const outputElement = element("output")

const OPTIUNI_INDICATOR = [
  {
    value: "umiditate relativă",
    text: "umiditate relativă (relative_humidity_2m)",
  },
  {
    value: "viteză vânt la 10m",
    text: "viteză vânt la 10m (wind_speed_10m)",
  },
  {
    value: "presiune atmosferică la nivelul mării",
    text: "presiune atmosferică la nivelul mării (pressure_msl)",
  },
  {
    value: "precipitații curente",
    text: "precipitații curente (precipitation)",
  },
  {
    value: "temperatură aer exterior",
    text: "temperatură aer exterior (temperature_2m)",
  },
]

function populeazaSelectIndicator(idSelect) {
  const select = element(idSelect)
  if (!select) {
    return
  }

  for (const optiune of OPTIUNI_INDICATOR) {
    const option = document.createElement("option")
    option.value = optiune.value
    option.textContent = optiune.text
    select.appendChild(option)
  }
}

function afiseazaRezultat(response, payload) {
  const location = response.headers.get("Location")
  const status = `Status: ${response.status} ${response.statusText}`
  statusElement.textContent = location ? `${status} | Location: ${location}` : status
  outputElement.textContent = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2)
}

function afiseazaEroare(error) {
  statusElement.textContent = "Status: request eșuat"
  outputElement.textContent = error.message
}

function idPozitiv(valoare) {
  const id = Number.parseInt(String(valoare), 10)
  return Number.isInteger(id) && id > 0 ? id : null
}

function seteazaItemIdDacaValid(idPotential) {
  const input = element("itemId")
  const id = idPozitiv(idPotential)
  if (!input || id === null) {
    return false
  }

  input.value = String(id)
  return true
}

function sincronizeazaItemIdDinRaspuns(path, payload) {
  if (typeof path !== "string" || !path.startsWith("/masuratori") || !payload || typeof payload !== "object") {
    return
  }

  const idPosibile = [
    ...(Array.isArray(payload.ids_generate) ? payload.ids_generate : []),
    payload.id,
    payload.id_tinta,
    payload.id_actualizat,
  ]

  for (const id of idPosibile) {
    if (seteazaItemIdDacaValid(id)) {
      return
    }
  }
}

async function apeleazaApi(metoda, ruta, body) {
  const options = { method: metoda }
  if (body !== undefined) {
    options.headers = { "Content-Type": "application/json" }
    options.body = JSON.stringify(body)
  }

  const response = await fetch(ruta, options)
  const contentType = response.headers.get("content-type") || ""
  const payload = contentType.includes("application/json") ? await response.json() : await response.text()

  sincronizeazaItemIdDinRaspuns(ruta, payload)
  afiseazaRezultat(response, payload)
}

function idElementCurent() {
  const input = element("itemId")
  const id = idPozitiv(input?.value.trim())
  if (id === null) {
    throw new Error("ID-ul trebuie să fie un număr întreg pozitiv")
  }
  return id
}

function caleaElement() {
  return `/masuratori/${idElementCurent()}`
}

function construiestePayloadExtern(idIndicator) {
  const body = {}
  const oras = element("externalCity")?.value.trim()
  const tara = element("externalCountry")?.value.trim()
  const indicator = idIndicator ? element(idIndicator)?.value.trim() : ""

  if (oras) {
    body.oras = oras
  }
  if (tara) {
    body.tara = tara
  }
  if (indicator) {
    body.indicator = indicator
  }

  return body
}

function leagaButon(idButon, actiuneAsync) {
  const buton = element(idButon)
  if (!buton) {
    return
  }

  buton.addEventListener("click", async () => {
    try {
      await actiuneAsync()
    } catch (error) {
      afiseazaEroare(error)
    }
  })
}

const RUTA_COLECTIE = "/masuratori"

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

for (const idSelect of ["externalMetric", "itemMetric"]) {
  populeazaSelectIndicator(idSelect)
}
