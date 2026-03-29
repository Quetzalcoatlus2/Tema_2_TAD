# Varianta comentată (folder separat)

Acest folder conține varianta de cod cu comentarii automate pe fiecare linie de cod.

## Reguli de lucru

1. Fișierele originale din rădăcina proiectului rămân fără comentarii.
2. Modificările de cod se fac în fișierele din acest folder (`varianta_comentata/`).
3. După orice modificare, rulează refresh/sync ca să păstrezi ambele versiuni cu același cod:

   `python varianta_comentata/actualizeaza_comentarii.py refresh`

4. Comanda `refresh` actualizează simultan:
  - varianta originală (fără comentarii) din rădăcina proiectului;
  - varianta comentată (regenerează comentariile per linie).

## Comenzi utile

- Inițializare (copiere din fișierele originale + comentarii pe fiecare linie):

  `python varianta_comentata/actualizeaza_comentarii.py init`

- Reîmprospătare comentarii pentru fișierele deja comentate:

  `python varianta_comentata/actualizeaza_comentarii.py refresh`

- Alias explicit pentru sincronizare completă (același comportament ca `refresh`):

  `python varianta_comentata/actualizeaza_comentarii.py sync`

- Verificare că varianta comentată și necomentată au același cod:

  `python varianta_comentata/actualizeaza_comentarii.py check`

## Fișiere incluse

- `serviciu_masuratori.py`
- `static/client_masuratori.js`
- `templates/panou_masuratori.html`
- `requirements.txt`