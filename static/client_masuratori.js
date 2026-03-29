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

function caleaElement() {
  const input = element("itemId")
  const id = idPozitiv(input?.value.trim())
  if (id === null) {
    throw new Error("ID-ul trebuie să fie un număr întreg pozitiv")
  }
  return `/masuratori/${id}`
}

function construiestePayloadExtern(idIndicator) {
  const mapari = [
    ["externalCity", "oras"],
    ["externalCountry", "tara"],
    [idIndicator, "indicator"],
  ]

  const body = {}
  for (const [idInput, camp] of mapari) {
    if (!idInput) {
      continue
    }

    const valoare = element(idInput)?.value.trim() || ""
    if (valoare) {
      body[camp] = valoare
    }
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
const METODE_COLECTIE_FARA_BODY = {
  getCollection: "GET",
  headCollection: "HEAD",
  deleteCollection: "DELETE",
  optionsCollection: "OPTIONS",
}
const METODE_ITEM_FARA_BODY = {
  getItem: "GET",
  headItem: "HEAD",
  deleteItem: "DELETE",
  optionsItem: "OPTIONS",
}
const METODE_COLECTIE_CU_BODY = {
  postCollection: "POST",
  putCollection: "PUT",
  patchCollection: "PATCH",
}
const METODE_ITEM_CU_BODY = {
  postItem: "POST",
  putItem: "PUT",
  patchItem: "PATCH",
}

for (const [idButon, metoda] of Object.entries(METODE_COLECTIE_FARA_BODY)) {
  leagaButon(idButon, () => apeleazaApi(metoda, RUTA_COLECTIE))
}
for (const [idButon, metoda] of Object.entries(METODE_COLECTIE_CU_BODY)) {
  leagaButon(idButon, () => apeleazaApi(metoda, RUTA_COLECTIE, construiestePayloadExtern("externalMetric")))
}
for (const [idButon, metoda] of Object.entries(METODE_ITEM_FARA_BODY)) {
  leagaButon(idButon, () => apeleazaApi(metoda, caleaElement()))
}
for (const [idButon, metoda] of Object.entries(METODE_ITEM_CU_BODY)) {
  leagaButon(idButon, () => apeleazaApi(metoda, caleaElement(), construiestePayloadExtern("itemMetric")))
}
leagaButon("syncExternal", () => apeleazaApi("POST", "/masuratori/sincronizeaza", construiestePayloadExtern("externalMetric")))
leagaButon("previewExternal", () => apeleazaApi("POST", "/masuratori/preview-extern", construiestePayloadExtern("externalMetric")))
leagaButon("traceCollection", () => apeleazaApi("POST", "/masuratori/trace/colectie"))
leagaButon("traceItem", () => {
  const id = caleaElement().split("/").pop()
  return apeleazaApi("POST", `/masuratori/trace/element/${id}`)
})

for (const idSelect of ["externalMetric", "itemMetric"]) {
  populeazaSelectIndicator(idSelect)
}
