# Harmonogramy odpadów – dane publiczne

Publiczna kopia danych zbieranych przez wątek danych. Z tego adresu czytają aplikacja i (później) strona www:

    https://funkygogo.github.io/harmonogramy-dane/v1/index.json
    https://funkygogo.github.io/harmonogramy-dane/v1/<TERYT>_<od>.json

Format: `wersja: 1` – opis w briefie „Harmonogramy odpadów – aplikacja i strona”, sekcja „Dane”.

## Zasady

- Pliki w `v1/` zmienia **tylko wątek danych**. Aplikacja ich nie poprawia; błędy zgłasza.
- W ramach `wersja: 1` nowe pola mogą dochodzić, istniejące się nie zmieniają. Zmiana formatu = nowy folder `v2/` i `wersja: 2`; `v1/` zostaje, dopóki działają stare wersje aplikacji.
- `sha256` w `index.json` musi zgadzać się z plikiem – aplikacja odrzuca plik o innej sumie, a publikacja na GitHubie się nie uda (kontrola w `.github/workflows/pages.yml`).
- Aplikacja pokazuje tylko gminy z `ok: true`.

## Jak publikować (wątek danych)

Po każdej zmianie w folderze `dane` (Pobrane\Harmonogramy\dane):

```
python narzedzia/publikuj.py "C:/Users/rfkon/Downloads/Harmonogramy/dane"
```

Skrypt sprawdza dane, kopiuje je do `v1/`, robi commit i push. GitHub Pages publikuje w ok. minutę; aplikacja pobiera zmiany przy następnym otwarciu (najczęściej raz na 6 godzin).

Bez gita na komputerze: na github.com w repozytorium wejdź w `v1/` → „Add file” → „Upload files”, przeciągnij `index.json` i zmienione pliki gmin, „Commit changes”.

## Stan (4.11.2026)

Repozytorium: https://github.com/FunkyGogo/harmonogramy-dane (GitHub Pages z gałęzi `main`, katalog główny).
Lista źródeł dla Google Play: https://funkygogo.github.io/harmonogramy-dane/zrodla.html – po zmianie danych wygeneruj ją ponownie (`python narzedzia/zrodla.py`) i wgraj razem z plikami.
Codzienne zadanie Claude porównuje index.json z Dysku Google z v1/, pobiera nowe/zmienione pliki (`narzedzia/aktualizuj.py plan|zastosuj`), generuje zrodla.html i robi push. Wątek danych nie musi niczego publikować sam.
