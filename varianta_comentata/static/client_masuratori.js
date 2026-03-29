// [AUTO-COMMENT] Linia 1.
const element = (id) => document.getElementById(id)
// [AUTO-COMMENT] Linia 2: linie goală.

// [AUTO-COMMENT] Linia 3.
const statusElement = element("status")
// [AUTO-COMMENT] Linia 4.
const outputElement = element("output")
// [AUTO-COMMENT] Linia 5: linie goală.

// [AUTO-COMMENT] Linia 6.
const OPTIUNI_INDICATOR = [
// [AUTO-COMMENT] Linia 7.
  {
// [AUTO-COMMENT] Linia 8.
    value: "umiditate relativă",
// [AUTO-COMMENT] Linia 9.
    text: "umiditate relativă (relative_humidity_2m)",
// [AUTO-COMMENT] Linia 10.
  },
// [AUTO-COMMENT] Linia 11.
  {
// [AUTO-COMMENT] Linia 12.
    value: "viteză vânt la 10m",
// [AUTO-COMMENT] Linia 13.
    text: "viteză vânt la 10m (wind_speed_10m)",
// [AUTO-COMMENT] Linia 14.
  },
// [AUTO-COMMENT] Linia 15.
  {
// [AUTO-COMMENT] Linia 16.
    value: "presiune atmosferică la nivelul mării",
// [AUTO-COMMENT] Linia 17.
    text: "presiune atmosferică la nivelul mării (pressure_msl)",
// [AUTO-COMMENT] Linia 18.
  },
// [AUTO-COMMENT] Linia 19.
  {
// [AUTO-COMMENT] Linia 20.
    value: "precipitații curente",
// [AUTO-COMMENT] Linia 21.
    text: "precipitații curente (precipitation)",
// [AUTO-COMMENT] Linia 22.
  },
// [AUTO-COMMENT] Linia 23.
  {
// [AUTO-COMMENT] Linia 24.
    value: "temperatură aer exterior",
// [AUTO-COMMENT] Linia 25.
    text: "temperatură aer exterior (temperature_2m)",
// [AUTO-COMMENT] Linia 26.
  },
// [AUTO-COMMENT] Linia 27.
]
// [AUTO-COMMENT] Linia 28: linie goală.

// [AUTO-COMMENT] Linia 29.
function populeazaSelectIndicator(idSelect) {
// [AUTO-COMMENT] Linia 30.
  const select = element(idSelect)
// [AUTO-COMMENT] Linia 31.
  if (!select) {
// [AUTO-COMMENT] Linia 32.
    return
// [AUTO-COMMENT] Linia 33.
  }
// [AUTO-COMMENT] Linia 34: linie goală.

// [AUTO-COMMENT] Linia 35.
  for (const optiune of OPTIUNI_INDICATOR) {
// [AUTO-COMMENT] Linia 36.
    const option = document.createElement("option")
// [AUTO-COMMENT] Linia 37.
    option.value = optiune.value
// [AUTO-COMMENT] Linia 38.
    option.textContent = optiune.text
// [AUTO-COMMENT] Linia 39.
    select.appendChild(option)
// [AUTO-COMMENT] Linia 40.
  }
// [AUTO-COMMENT] Linia 41.
}
// [AUTO-COMMENT] Linia 42: linie goală.

// [AUTO-COMMENT] Linia 43.
function afiseazaRezultat(response, payload) {
// [AUTO-COMMENT] Linia 44.
  const location = response.headers.get("Location")
// [AUTO-COMMENT] Linia 45.
  const status = `Status: ${response.status} ${response.statusText}`
// [AUTO-COMMENT] Linia 46.
  statusElement.textContent = location ? `${status} | Location: ${location}` : status
// [AUTO-COMMENT] Linia 47.
  outputElement.textContent = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2)
// [AUTO-COMMENT] Linia 48.
}
// [AUTO-COMMENT] Linia 49: linie goală.

// [AUTO-COMMENT] Linia 50.
function afiseazaEroare(error) {
// [AUTO-COMMENT] Linia 51.
  statusElement.textContent = "Status: request eșuat"
// [AUTO-COMMENT] Linia 52.
  outputElement.textContent = error.message
// [AUTO-COMMENT] Linia 53.
}
// [AUTO-COMMENT] Linia 54: linie goală.

// [AUTO-COMMENT] Linia 55.
function idPozitiv(valoare) {
// [AUTO-COMMENT] Linia 56.
  const id = Number.parseInt(String(valoare), 10)
// [AUTO-COMMENT] Linia 57.
  return Number.isInteger(id) && id > 0 ? id : null
// [AUTO-COMMENT] Linia 58.
}
// [AUTO-COMMENT] Linia 59: linie goală.

// [AUTO-COMMENT] Linia 60.
function seteazaItemIdDacaValid(idPotential) {
// [AUTO-COMMENT] Linia 61.
  const input = element("itemId")
// [AUTO-COMMENT] Linia 62.
  const id = idPozitiv(idPotential)
// [AUTO-COMMENT] Linia 63.
  if (!input || id === null) {
// [AUTO-COMMENT] Linia 64.
    return false
// [AUTO-COMMENT] Linia 65.
  }
// [AUTO-COMMENT] Linia 66: linie goală.

// [AUTO-COMMENT] Linia 67.
  input.value = String(id)
// [AUTO-COMMENT] Linia 68.
  return true
// [AUTO-COMMENT] Linia 69.
}
// [AUTO-COMMENT] Linia 70: linie goală.

// [AUTO-COMMENT] Linia 71.
function sincronizeazaItemIdDinRaspuns(path, payload) {
// [AUTO-COMMENT] Linia 72.
  if (typeof path !== "string" || !path.startsWith("/masuratori") || !payload || typeof payload !== "object") {
// [AUTO-COMMENT] Linia 73.
    return
// [AUTO-COMMENT] Linia 74.
  }
// [AUTO-COMMENT] Linia 75: linie goală.

// [AUTO-COMMENT] Linia 76.
  const idPosibile = [
// [AUTO-COMMENT] Linia 77.
    ...(Array.isArray(payload.ids_generate) ? payload.ids_generate : []),
// [AUTO-COMMENT] Linia 78.
    payload.id,
// [AUTO-COMMENT] Linia 79.
    payload.id_tinta,
// [AUTO-COMMENT] Linia 80.
    payload.id_actualizat,
// [AUTO-COMMENT] Linia 81.
  ]
// [AUTO-COMMENT] Linia 82: linie goală.

// [AUTO-COMMENT] Linia 83.
  for (const id of idPosibile) {
// [AUTO-COMMENT] Linia 84.
    if (seteazaItemIdDacaValid(id)) {
// [AUTO-COMMENT] Linia 85.
      return
// [AUTO-COMMENT] Linia 86.
    }
// [AUTO-COMMENT] Linia 87.
  }
// [AUTO-COMMENT] Linia 88.
}
// [AUTO-COMMENT] Linia 89: linie goală.

// [AUTO-COMMENT] Linia 90.
async function apeleazaApi(metoda, ruta, body) {
// [AUTO-COMMENT] Linia 91.
  const options = { method: metoda }
// [AUTO-COMMENT] Linia 92.
  if (body !== undefined) {
// [AUTO-COMMENT] Linia 93.
    options.headers = { "Content-Type": "application/json" }
// [AUTO-COMMENT] Linia 94.
    options.body = JSON.stringify(body)
// [AUTO-COMMENT] Linia 95.
  }
// [AUTO-COMMENT] Linia 96: linie goală.

// [AUTO-COMMENT] Linia 97.
  const response = await fetch(ruta, options)
// [AUTO-COMMENT] Linia 98.
  const contentType = response.headers.get("content-type") || ""
// [AUTO-COMMENT] Linia 99.
  const payload = contentType.includes("application/json") ? await response.json() : await response.text()
// [AUTO-COMMENT] Linia 100: linie goală.

// [AUTO-COMMENT] Linia 101.
  sincronizeazaItemIdDinRaspuns(ruta, payload)
// [AUTO-COMMENT] Linia 102.
  afiseazaRezultat(response, payload)
// [AUTO-COMMENT] Linia 103.
}
// [AUTO-COMMENT] Linia 104: linie goală.

// [AUTO-COMMENT] Linia 105.
function caleaElement() {
// [AUTO-COMMENT] Linia 106.
  const input = element("itemId")
// [AUTO-COMMENT] Linia 107.
  const id = idPozitiv(input?.value.trim())
// [AUTO-COMMENT] Linia 108.
  if (id === null) {
// [AUTO-COMMENT] Linia 109.
    throw new Error("ID-ul trebuie să fie un număr întreg pozitiv")
// [AUTO-COMMENT] Linia 110.
  }
// [AUTO-COMMENT] Linia 111.
  return `/masuratori/${id}`
// [AUTO-COMMENT] Linia 112.
}
// [AUTO-COMMENT] Linia 113: linie goală.

// [AUTO-COMMENT] Linia 114.
function construiestePayloadExtern(idIndicator) {
// [AUTO-COMMENT] Linia 115.
  const mapari = [
// [AUTO-COMMENT] Linia 116.
    ["externalCity", "oras"],
// [AUTO-COMMENT] Linia 117.
    ["externalCountry", "tara"],
// [AUTO-COMMENT] Linia 118.
    [idIndicator, "indicator"],
// [AUTO-COMMENT] Linia 119.
  ]
// [AUTO-COMMENT] Linia 120: linie goală.

// [AUTO-COMMENT] Linia 121.
  const body = {}
// [AUTO-COMMENT] Linia 122.
  for (const [idInput, camp] of mapari) {
// [AUTO-COMMENT] Linia 123.
    if (!idInput) {
// [AUTO-COMMENT] Linia 124.
      continue
// [AUTO-COMMENT] Linia 125.
    }
// [AUTO-COMMENT] Linia 126: linie goală.

// [AUTO-COMMENT] Linia 127.
    const valoare = element(idInput)?.value.trim() || ""
// [AUTO-COMMENT] Linia 128.
    if (valoare) {
// [AUTO-COMMENT] Linia 129.
      body[camp] = valoare
// [AUTO-COMMENT] Linia 130.
    }
// [AUTO-COMMENT] Linia 131.
  }
// [AUTO-COMMENT] Linia 132.
  return body
// [AUTO-COMMENT] Linia 133.
}
// [AUTO-COMMENT] Linia 134: linie goală.

// [AUTO-COMMENT] Linia 135.
function leagaButon(idButon, actiuneAsync) {
// [AUTO-COMMENT] Linia 136.
  const buton = element(idButon)
// [AUTO-COMMENT] Linia 137.
  if (!buton) {
// [AUTO-COMMENT] Linia 138.
    return
// [AUTO-COMMENT] Linia 139.
  }
// [AUTO-COMMENT] Linia 140: linie goală.

// [AUTO-COMMENT] Linia 141.
  buton.addEventListener("click", async () => {
// [AUTO-COMMENT] Linia 142.
    try {
// [AUTO-COMMENT] Linia 143.
      await actiuneAsync()
// [AUTO-COMMENT] Linia 144.
    } catch (error) {
// [AUTO-COMMENT] Linia 145.
      afiseazaEroare(error)
// [AUTO-COMMENT] Linia 146.
    }
// [AUTO-COMMENT] Linia 147.
  })
// [AUTO-COMMENT] Linia 148.
}
// [AUTO-COMMENT] Linia 149: linie goală.

// [AUTO-COMMENT] Linia 150.
const RUTA_COLECTIE = "/masuratori"
// [AUTO-COMMENT] Linia 151.
const METODE_COLECTIE_FARA_BODY = {
// [AUTO-COMMENT] Linia 152.
  getCollection: "GET",
// [AUTO-COMMENT] Linia 153.
  headCollection: "HEAD",
// [AUTO-COMMENT] Linia 154.
  deleteCollection: "DELETE",
// [AUTO-COMMENT] Linia 155.
  optionsCollection: "OPTIONS",
// [AUTO-COMMENT] Linia 156.
}
// [AUTO-COMMENT] Linia 157.
const METODE_ITEM_FARA_BODY = {
// [AUTO-COMMENT] Linia 158.
  getItem: "GET",
// [AUTO-COMMENT] Linia 159.
  headItem: "HEAD",
// [AUTO-COMMENT] Linia 160.
  deleteItem: "DELETE",
// [AUTO-COMMENT] Linia 161.
  optionsItem: "OPTIONS",
// [AUTO-COMMENT] Linia 162.
}
// [AUTO-COMMENT] Linia 163.
const METODE_COLECTIE_CU_BODY = {
// [AUTO-COMMENT] Linia 164.
  postCollection: "POST",
// [AUTO-COMMENT] Linia 165.
  putCollection: "PUT",
// [AUTO-COMMENT] Linia 166.
  patchCollection: "PATCH",
// [AUTO-COMMENT] Linia 167.
}
// [AUTO-COMMENT] Linia 168.
const METODE_ITEM_CU_BODY = {
// [AUTO-COMMENT] Linia 169.
  postItem: "POST",
// [AUTO-COMMENT] Linia 170.
  putItem: "PUT",
// [AUTO-COMMENT] Linia 171.
  patchItem: "PATCH",
// [AUTO-COMMENT] Linia 172.
}
// [AUTO-COMMENT] Linia 173: linie goală.

// [AUTO-COMMENT] Linia 174.
for (const [idButon, metoda] of Object.entries(METODE_COLECTIE_FARA_BODY)) {
// [AUTO-COMMENT] Linia 175.
  leagaButon(idButon, () => apeleazaApi(metoda, RUTA_COLECTIE))
// [AUTO-COMMENT] Linia 176.
}
// [AUTO-COMMENT] Linia 177.
for (const [idButon, metoda] of Object.entries(METODE_COLECTIE_CU_BODY)) {
// [AUTO-COMMENT] Linia 178.
  leagaButon(idButon, () => apeleazaApi(metoda, RUTA_COLECTIE, construiestePayloadExtern("externalMetric")))
// [AUTO-COMMENT] Linia 179.
}
// [AUTO-COMMENT] Linia 180.
for (const [idButon, metoda] of Object.entries(METODE_ITEM_FARA_BODY)) {
// [AUTO-COMMENT] Linia 181.
  leagaButon(idButon, () => apeleazaApi(metoda, caleaElement()))
// [AUTO-COMMENT] Linia 182.
}
// [AUTO-COMMENT] Linia 183.
for (const [idButon, metoda] of Object.entries(METODE_ITEM_CU_BODY)) {
// [AUTO-COMMENT] Linia 184.
  leagaButon(idButon, () => apeleazaApi(metoda, caleaElement(), construiestePayloadExtern("itemMetric")))
// [AUTO-COMMENT] Linia 185.
}
// [AUTO-COMMENT] Linia 186.
leagaButon("syncExternal", () => apeleazaApi("POST", "/masuratori/sincronizeaza", construiestePayloadExtern("externalMetric")))
// [AUTO-COMMENT] Linia 187.
leagaButon("previewExternal", () => apeleazaApi("POST", "/masuratori/preview-extern", construiestePayloadExtern("externalMetric")))
// [AUTO-COMMENT] Linia 188.
leagaButon("traceCollection", () => apeleazaApi("POST", "/masuratori/trace/colectie"))
// [AUTO-COMMENT] Linia 189.
leagaButon("traceItem", () => {
// [AUTO-COMMENT] Linia 190.
  const id = caleaElement().split("/").pop()
// [AUTO-COMMENT] Linia 191.
  return apeleazaApi("POST", `/masuratori/trace/element/${id}`)
// [AUTO-COMMENT] Linia 192.
})
// [AUTO-COMMENT] Linia 193: linie goală.

// [AUTO-COMMENT] Linia 194.
for (const idSelect of ["externalMetric", "itemMetric"]) {
// [AUTO-COMMENT] Linia 195.
  populeazaSelectIndicator(idSelect)
// [AUTO-COMMENT] Linia 196.
}
