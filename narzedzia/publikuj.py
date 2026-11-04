#!/usr/bin/env python3
"""
Publikacja danych harmonogramów na GitHub Pages.

Wątek danych uruchamia to po każdej zmianie plików na Dysku/w folderze dane:

    python narzedzia/publikuj.py "C:/Users/rfkon/Downloads/Harmonogramy/dane"

Skrypt:
 1. sprawdza index.json (numer formatu < 100, sha256 każdego pliku z ok: true),
 2. kopiuje index.json i pliki gmin do v1/ (usuwa z v1/ pliki, których nie ma w indeksie),
 3. robi commit i push – GitHub Pages publikuje w ciągu ~1 minuty.
Z --bez-push tylko kopiuje i sprawdza.
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DST = REPO / "v1"


def sprawdz(src: Path) -> dict:
    index = json.loads((src / "index.json").read_text(encoding="utf-8"))
    if not isinstance(index.get("gminy"), list) or not (0 < index.get("wersja", 0) < 100):
        sys.exit(f"Nieobsługiwana wersja formatu: {index.get('wersja')} ")
    bledy = []
    for g in index["gminy"]:
        p = src / g["plik"]
        if not p.exists():
            bledy.append(f"brak pliku {g['plik']}")
            continue
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        if sha != g["sha256"]:
            bledy.append(f"{g['plik']}: sha256 różni się od index.json")
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("teryt") != g["teryt"] or d.get("okres") != g["okres"]:
            bledy.append(f"{g['plik']}: teryt/okres niezgodne z index.json")
        if g.get("ok") and not d.get("walidacja", {}).get("ok"):
            bledy.append(f"{g['plik']}: ok w indeksie, ale walidacja.ok = false")
    if bledy:
        sys.exit("Nie publikuję – popraw w wątku danych:\n  " + "\n  ".join(bledy))
    return index


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    src = Path(args[0])
    index = sprawdz(src)
    if src.resolve() == DST.resolve():
        print(f"v1/ poprawne: {len(index['gminy'])} plików gmin ({index.get('zaktualizowano')})")
        return
    DST.mkdir(exist_ok=True)
    potrzebne = {"index.json"} | {g["plik"] for g in index["gminy"]}
    for p in DST.glob("*.json"):
        if p.name not in potrzebne:
            p.unlink()
    for name in potrzebne:
        shutil.copy2(src / name, DST / name)
    print(f"v1/: {len(potrzebne) - 1} plików gmin + index.json ({index.get('zaktualizowano')})")

    if "--bez-push" in sys.argv:
        return
    import zrodla  # lista źródeł na stronie (zrodla.html) zawsze zgodna z danymi
    zrodla.main(DST, REPO / "zrodla.html")
    subprocess.run(["git", "-C", str(REPO), "add", "-A", "v1", "zrodla.html"], check=True)
    if subprocess.run(["git", "-C", str(REPO), "diff", "--cached", "--quiet"]).returncode == 0:
        print("Bez zmian – nic do publikacji.")
        return
    msg = f"Dane {index.get('zaktualizowano')}: {len(index['gminy'])} plików"
    subprocess.run(["git", "-C", str(REPO), "commit", "-m", msg], check=True)
    subprocess.run(["git", "-C", str(REPO), "push"], check=True)
    print("Wysłane. Strona odświeży się w ciągu ok. minuty.")


if __name__ == "__main__":
    main()
