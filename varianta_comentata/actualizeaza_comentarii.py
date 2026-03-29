from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path


AUTO_TAG = "[AUTO-COMMENT]"

FISIERE_COD = [
    "serviciu_masuratori.py",
    "static/client_masuratori.js",
    "templates/panou_masuratori.html",
    "requirements.txt",
]

CONFIG_COMENTARII = {
    ".py": ("# ", ""),
    ".js": ("// ", ""),
    ".html": ("<!-- ", " -->"),
    ".txt": ("# ", ""),
}


def comentariu_auto(extensie: str, numar_linie: int, linie_originala: str) -> str:
    inceput, final = CONFIG_COMENTARII[extensie]
    mesaj = f"{AUTO_TAG} Linia {numar_linie}."
    if not linie_originala.strip():
        mesaj = f"{AUTO_TAG} Linia {numar_linie}: linie goală."
    return f"{inceput}{mesaj}{final}\n"


def este_comentariu_auto(extensie: str, linie: str) -> bool:
    linie_curata = linie.strip()
    if extensie == ".html":
        return linie_curata.startswith(f"<!-- {AUTO_TAG}")

    inceput, _ = CONFIG_COMENTARII[extensie]
    return linie_curata.startswith(f"{inceput.strip()} {AUTO_TAG}")


def scrie_varianta_comentata(cale_destinatie: Path, extensie: str, linii_cod: list[str]) -> None:
    continut_final = []
    for index, linie_cod in enumerate(linii_cod, start=1):
        continut_final.append(comentariu_auto(extensie, index, linie_cod))
        continut_final.append(linie_cod)

    cale_destinatie.parent.mkdir(parents=True, exist_ok=True)
    cale_destinatie.write_text("".join(continut_final), encoding="utf-8")


def scrie_varianta_necomentata(cale_destinatie: Path, linii_cod: list[str]) -> None:
    cale_destinatie.parent.mkdir(parents=True, exist_ok=True)
    cale_destinatie.write_text("".join(linii_cod), encoding="utf-8")


def extrage_linii_cod_din_fisier_comentat(cale: Path, extensie: str) -> list[str]:
    linii = cale.read_text(encoding="utf-8").splitlines(keepends=True)
    return [linie for linie in linii if not este_comentariu_auto(extensie, linie)]


def init_din_originale(radacina_proiect: Path, radacina_varianta_comentata: Path) -> None:
    for fisier_relativ in FISIERE_COD:
        sursa = radacina_proiect / fisier_relativ
        extensie = sursa.suffix.lower()
        if extensie not in CONFIG_COMENTARII:
            continue

        linii_cod = sursa.read_text(encoding="utf-8").splitlines(keepends=True)
        destinatie = radacina_varianta_comentata / fisier_relativ
        scrie_varianta_comentata(destinatie, extensie, linii_cod)
        print(f"[INIT] Generat: {destinatie}")


def refresh_si_sync_in_place(radacina_proiect: Path, radacina_varianta_comentata: Path) -> None:
    for fisier_relativ in FISIERE_COD:
        cale_comentata = radacina_varianta_comentata / fisier_relativ
        if not cale_comentata.exists():
            print(f"[SKIP] Lipsește varianta comentată: {cale_comentata}")
            continue

        extensie = cale_comentata.suffix.lower()
        if extensie not in CONFIG_COMENTARII:
            continue

        linii_cod = extrage_linii_cod_din_fisier_comentat(cale_comentata, extensie)

        cale_necomentata = radacina_proiect / fisier_relativ
        scrie_varianta_necomentata(cale_necomentata, linii_cod)
        print(f"[SYNC] Actualizat original: {cale_necomentata}")

        scrie_varianta_comentata(cale_comentata, extensie, linii_cod)
        print(f"[REFRESH] Actualizat comentat: {cale_comentata}")


def verifica_sincronizare(radacina_proiect: Path, radacina_varianta_comentata: Path) -> bool:
    toate_sunt_sync = True

    for fisier_relativ in FISIERE_COD:
        cale_necomentata = radacina_proiect / fisier_relativ
        cale_comentata = radacina_varianta_comentata / fisier_relativ

        if not cale_necomentata.exists() or not cale_comentata.exists():
            toate_sunt_sync = False
            print(
                f"[DIFF] Lipsește fișier: original={cale_necomentata.exists()} comentat={cale_comentata.exists()} ({fisier_relativ})"
            )
            continue

        extensie = cale_comentata.suffix.lower()
        if extensie not in CONFIG_COMENTARII:
            continue

        linii_necomentate = cale_necomentata.read_text(encoding="utf-8").splitlines(keepends=True)
        linii_din_comentat = extrage_linii_cod_din_fisier_comentat(cale_comentata, extensie)

        if linii_necomentate != linii_din_comentat:
            toate_sunt_sync = False
            print(f"[DIFF] Conținut diferit: {fisier_relativ}")
        else:
            print(f"[OK] Sincronizat: {fisier_relativ}")

    return toate_sunt_sync


def main() -> None:
    parser = ArgumentParser(description="Generează și actualizează varianta comentată pentru toate fișierele de cod.")
    parser.add_argument(
        "mod",
        nargs="?",
        default="refresh",
        choices=["init", "refresh", "sync", "check"],
        help=(
            "init = copiază din fișierele originale; "
            "refresh/sync = extrage codul din varianta comentată, actualizează originalele și regenerează comentariile; "
            "check = verifică dacă cele două variante au exact același cod."
        ),
    )
    args = parser.parse_args()

    radacina_varianta_comentata = Path(__file__).resolve().parent
    radacina_proiect = radacina_varianta_comentata.parent

    if args.mod == "init":
        init_din_originale(radacina_proiect, radacina_varianta_comentata)
        return

    if args.mod == "check":
        sunt_sync = verifica_sincronizare(radacina_proiect, radacina_varianta_comentata)
        if not sunt_sync:
            raise SystemExit(1)
        return

    refresh_si_sync_in_place(radacina_proiect, radacina_varianta_comentata)


if __name__ == "__main__":
    main()