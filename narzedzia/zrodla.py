#!/usr/bin/env python3
"""Generuje zrodla.html – publiczną listę źródeł harmonogramów (z v1/). Uruchamiane przez publikuj.py."""
import html, json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MIES = ["stycznia","lutego","marca","kwietnia","maja","czerwca","lipca","sierpnia","września","października","listopada","grudnia"]
def data(iso): y, m, d = iso.split("-"); return f"{int(d)} {MIES[int(m)-1]} {y}"
def e(s): return html.escape(str(s or ""))
def a(u, t): return f'<a href="{e(u)}" rel="noopener">{e(t)}</a>'

# Oficjalne strony gmin dla harmonogramów bez linku w danych – tylko do czasu, aż wątek danych doda
# pole zrodlo.strona_gminy (pliki z danymi zmienia wyłącznie wątek danych).
UZUPELNIENIA = {"2010023": {"strona_gminy": "https://drohiczyn.pl/"}}

def wiersz(g, d):
    z = {**UZUPELNIENIA.get(g["teryt"], {}), **(d.get("zrodlo") or {})}
    nazwa = ("miasto " if g["teryt"].endswith("1") else "gm. ") + g["gmina"]
    op = z.get("operator") or g.get("operator") or ""
    if op.lower().startswith("nieustalon"): op = ""
    czesci = []
    if z.get("typ") == "korespondencja" or not z.get("url"):
        od = z.get("od_kogo") or op or "urząd gminy"
        kiedy = f" ({data(z['data_otrzymania'])})" if z.get("data_otrzymania") else ""
        czesci.append(f"Harmonogram przekazany przez: {e(od)}{kiedy}" + (f" – {a(z['url'], 'kopia dokumentu')}" if z.get("url") else ""))
    else:
        czesci.append(a(z["url"], "harmonogram w PDF" if ".pdf" in z["url"].lower() else "strona z harmonogramem") + (f" – {e(op)}" if op else ""))
    if z.get("strona_gminy") and z.get("strona_gminy") != z.get("url"):
        czesci.append(a(z["strona_gminy"], "oficjalna strona gminy"))
    okres = f"{data(g['okres']['od'])} – {data(g['okres']['do'])}"
    pobr = f" · pobrano {data(z['pobrano'])}" if z.get("pobrano") else ""
    return f"<tr><th scope=\"row\">{e(nazwa)}</th><td>{'<br>'.join(czesci)}<div class=\"m\">obowiązuje {okres}{pobr}</div></td></tr>"

def main(src=REPO / "v1", dst=REPO / "zrodla.html"):
    index = json.loads((src / "index.json").read_text(encoding="utf-8"))
    gm = [g for g in index["gminy"] if g.get("ok")]
    gm.sort(key=lambda g: (g["gmina"].lower().replace("ł", "l~").replace("ś", "s~").replace("ż", "z~").replace("ź", "z~"), g["okres"]["od"]))
    rows = "\n".join(wiersz(g, json.loads((src / g["plik"]).read_text(encoding="utf-8"))) for g in gm)
    out = f"""<!doctype html>
<html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Źródła harmonogramów – Kiedy wywóz</title>
<style>
:root{{--bg:#EFECE6;--fg:#1d1c1a;--muted:#5f5b54;--card:#F9F7F3;--line:#dcd7cd;--accent:#2f6b3a}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151513;--fg:#ecebe6;--muted:#a5a199;--card:#1e1e1b;--line:#33322e;--accent:#7fc08b}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;overflow-x:hidden}}
main{{max-width:860px;margin:0 auto;padding:32px 16px 64px}} a{{color:var(--accent);overflow-wrap:anywhere}}
h1{{font-size:28px;line-height:1.2;margin:0 0 8px}} .note{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:16px 0 24px}}
table{{width:100%;border-collapse:collapse}} th,td{{text-align:left;vertical-align:top;padding:10px 8px;border-bottom:1px solid var(--line)}}
th{{width:30%;font-weight:600}} .m{{color:var(--muted);font-size:14px}} .muted{{color:var(--muted)}}
@media (max-width:560px){{th,td{{display:block;width:auto;padding:4px 0}} th{{padding-top:12px}} td{{border-bottom:1px solid var(--line);padding-bottom:12px}} th{{border:0}}}}
</style></head><body><main>
<h1>Źródła harmonogramów</h1>
<p class="muted">Aplikacja „Kiedy wywóz” · {len(gm)} harmonogramów · stan na {data(index.get('zaktualizowano', gm[0]['zaktualizowano']))}</p>
<div class="note"><strong>Zastrzeżenie.</strong> „Kiedy wywóz” to niezależna, prywatna aplikacja. Nie jest aplikacją rządową, aplikacją gminy ani firmy odbierającej odpady i nie reprezentuje żadnej instytucji publicznej. Terminy przepisujemy z oficjalnych harmonogramów publikowanych przez gminy i firmy odbierające odpady na ich zlecenie (poniżej). W razie różnic zawsze obowiązuje dokument gminy. Błąd można zgłosić w aplikacji albo na adres <a href="mailto:rfkondratowicz@gmail.com">rfkondratowicz@gmail.com</a>.</div>
<table><thead><tr><th>Gmina</th><td><strong>Źródło</strong></td></tr></thead><tbody>
{rows}
</tbody></table>
<p class="muted"><a href="polityka-prywatnosci.html">Polityka prywatności</a> · <a href="v1/index.json">Dane w formacie JSON</a></p>
</main></body></html>
"""
    dst.write_text(out, encoding="utf-8")
    print(f"zrodla.html: {len(gm)} gmin")

if __name__ == "__main__":
    main(*(Path(p) for p in sys.argv[1:3]))
