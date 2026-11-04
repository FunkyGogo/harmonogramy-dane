#!/usr/bin/env python3
"""
Aktualizacja v1/ na podstawie index.json z Dysku Google (wątek danych) – używane przez codzienne zadanie.

  1) python narzedzia/aktualizuj.py plan <nowy_index.json>
       wypisuje JSON: lista plików do pobrania z Dysku [{plik, drive_id}] (nowe lub ze zmienionym sha256)
       oraz informację, czy cokolwiek się zmieniło.
  2) python narzedzia/aktualizuj.py zastosuj <nowy_index.json> <katalog_z_pobranymi_plikami>
       sprawdza sha256 pobranych plików, kopiuje je do v1/, zapisuje index.json, usuwa pliki spoza indeksu,
       sprawdza całość (publikuj.sprawdz) i generuje zrodla.html. Nie robi commita.
Plików z danymi nie zmienia – kopiuje je bajt w bajt.
"""
import hashlib, json, shutil, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
V1 = REPO / "v1"
sys.path.insert(0, str(Path(__file__).resolve().parent))

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def plan(nowy):
    idx = json.loads(Path(nowy).read_text(encoding="utf-8"))
    potrzebne = []
    for g in idx["gminy"]:
        if not g.get("ok"): continue
        p = V1 / g["plik"]
        if not p.exists() or sha(p) != g["sha256"]:
            potrzebne.append({"plik": g["plik"], "drive_id": g.get("drive_id"), "gmina": g["gmina"]})
    stary = (V1 / "index.json").read_bytes() if (V1 / "index.json").exists() else b""
    zmiana = bool(potrzebne) or stary != Path(nowy).read_bytes()
    print(json.dumps({"zmiana": zmiana, "do_pobrania": potrzebne}, ensure_ascii=False, indent=1))

def zastosuj(nowy, katalog):
    import publikuj, zrodla
    idx = json.loads(Path(nowy).read_text(encoding="utf-8"))
    kat = Path(katalog)
    bledy = []
    for g in idx["gminy"]:
        if not g.get("ok"): continue
        cel = V1 / g["plik"]
        src = kat / g["plik"]
        if src.exists():
            if sha(src) != g["sha256"]:
                bledy.append(f"{g['plik']}: pobrany plik ma inny sha256 niż index.json"); continue
            shutil.copyfile(src, cel)
        elif not cel.exists() or sha(cel) != g["sha256"]:
            bledy.append(f"{g['plik']}: brak pliku o sha256 z indeksu")
    if bledy:
        sys.exit("Nie aktualizuję – zgłoś do wątku danych:\n  " + "\n  ".join(bledy))
    if Path(nowy).resolve() != (V1 / "index.json").resolve():
        shutil.copyfile(nowy, V1 / "index.json")
    potrzebne = {"index.json", "README.md"} | {g["plik"] for g in idx["gminy"] if g.get("ok")}
    for p in V1.iterdir():
        if p.name not in potrzebne: p.unlink()
    # pliki z ok:false nie trafiają do v1 – sprawdzamy tylko te z ok:true
    sprawdzany = {**idx, "gminy": [g for g in idx["gminy"] if g.get("ok")]}
    tmp = V1 / "_sprawdzany_index.json"
    tmp.write_text(json.dumps(sprawdzany, ensure_ascii=False), encoding="utf-8")
    try:
        kopia = V1 / "index.json"
        oryg = kopia.read_bytes(); kopia.write_bytes(tmp.read_bytes())
        publikuj.sprawdz(V1)
        kopia.write_bytes(oryg)
    finally:
        tmp.unlink(missing_ok=True)
    zrodla.main(V1, REPO / "zrodla.html")
    print(f"OK: {len(sprawdzany['gminy'])} gmin w v1/")

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "plan": plan(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "zastosuj": zastosuj(sys.argv[2], sys.argv[3])
    else: sys.exit(__doc__)
