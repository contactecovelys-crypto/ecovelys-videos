#!/usr/bin/env python3
"""Génère un visuel Instagram Ecovelys (1080x1350 JPEG), même design que les posts 01 et 02.

Usage : python3 outils/instagram_post.py post.json sortie.jpg
post.json :
{
  "badge": "NOTRE MÉTHODE",
  "titre": "Votre projet en [[4 étapes]] simples",   // [[...]] = encadré blanc ; \\n = retour à la ligne
  "style": "coches" | "numeros",
  "points": ["...", "...", "..."],                   // 3 ou 4 points courts
  "note": "Phrase de précaution en bas.",
  "bouton": "Vérifier mon éligibilité"
}
"""
import html, json, re, sys
from playwright.sync_api import sync_playwright

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;overflow:hidden;position:relative;color:#fff;
 font-family:Inter,'Helvetica Neue',Arial,sans-serif;
 background:linear-gradient(155deg,#0891d7 0%,#14a0a8 45%,#1fac84 78%,#2fb47b 100%)}
.ring{position:absolute;border:2px solid rgba(255,255,255,.14);border-radius:50%}
.blob{position:absolute;border-radius:50%;background:rgba(255,255,255,.07)}
main{position:absolute;left:70px;right:70px;top:60px;bottom:55px;display:flex;flex-direction:column}
.marque{display:flex;align-items:center;gap:16px;font-size:42px;font-weight:700}
.badge{align-self:flex-start;margin-top:34px;border:3px solid #fff;border-radius:40px;padding:12px 30px;
 font-size:24px;font-weight:700;text-transform:uppercase}
h1{margin-top:36px;font-size:76px;line-height:1.28;font-weight:800;letter-spacing:-1px}
.hl{display:inline-block;background:#fff;border-radius:20px;padding:0 15px;line-height:1.04}
.hl b{background:linear-gradient(90deg,#0891d7,#25b06f);-webkit-background-clip:text;color:transparent;font-weight:800}
ul{list-style:none;margin-top:28px;display:flex;flex-direction:column;gap:16px}
li{display:flex;align-items:center;gap:42px;background:#fff;border-radius:32px;padding:22px 34px;min-height:112px;
 color:#0f2440;font-size:36px;line-height:1.28;font-weight:600;box-shadow:0 16px 36px rgba(0,30,60,.18)}
.rond{flex:none;width:76px;height:76px;border-radius:50%;background:linear-gradient(90deg,#0891d7,#25b06f);
 color:#fff;display:flex;align-items:center;justify-content:center;font-size:42px;font-weight:800}
.bas{margin-top:auto}
.note{font-size:28px;line-height:1.45;font-weight:500;margin-bottom:28px}
.cta{height:95px;border-radius:48px;background:#fff;display:flex;align-items:center;justify-content:center;gap:36px;
 font-size:34px;font-weight:800}
.cta span{background:linear-gradient(90deg,#0891d7,#25b06f);-webkit-background-clip:text;color:transparent}
"""
COCHE = '<svg width="40" height="32" viewBox="0 0 40 32"><path d="M3 16l11 11L37 4" fill="none" stroke="#fff" stroke-width="8"/></svg>'
ECLAIR = ('<svg width="56" height="56" viewBox="0 0 56 56"><circle cx="28" cy="28" r="28" fill="#fff"/>'
          '<path d="M31 12L18 31h9l-3 13 14-20h-9z" fill="#14a0a8"/></svg>')
FLECHE = ('<svg width="48" height="48" viewBox="0 0 48 48"><circle cx="24" cy="24" r="24" fill="#22ae72"/>'
          '<path d="M13 24h20M25 15l9 9-9 9" fill="none" stroke="#fff" stroke-width="5"/></svg>')

def titre(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\[\[(.+?)\]\]", r'<span class="hl"><b>\1</b></span>', t)
    return t.replace("\n", "<br>")

def main(src, out):
    d = json.load(open(src, encoding="utf-8"))
    assert 3 <= len(d["points"]) <= 4, "3 ou 4 points"
    e = lambda s: html.escape(s, quote=False)
    puces = "".join(
        f'<li><span class="rond">{i if d.get("style") == "numeros" else COCHE}</span><span>{e(p)}</span></li>'
        for i, p in enumerate(d["points"], 1))
    rings = "".join(f'<div class="ring" style="width:{r*2}px;height:{r*2}px;left:{960-r}px;top:{120-r}px"></div>'
                    for r in (90, 190, 390, 590))
    page_html = f"""<!doctype html><meta charset="utf-8"><style>{CSS}</style><body>{rings}
<div class="blob" style="width:520px;height:520px;left:-260px;top:1000px"></div>
<div class="blob" style="width:420px;height:420px;left:800px;top:1100px"></div>
<main><div class="marque">{ECLAIR}Ecovelys</div><div class="badge">{e(d["badge"])}</div>
<h1>{titre(d["titre"])}</h1><ul>{puces}</ul>
<div class="bas"><p class="note">{e(d["note"])}</p><div class="cta"><span>{e(d["bouton"])}</span>{FLECHE}</div></div></main>"""
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        pg.set_content(page_html)
        pg.evaluate("document.fonts.ready")
        # Contrôle : rien ne doit déborder ni se chevaucher
        gap = pg.evaluate("document.querySelector('.bas').getBoundingClientRect().top - document.querySelector('ul').getBoundingClientRect().bottom")
        wide = pg.evaluate("[...document.querySelectorAll('h1,.hl,.cta span,.badge')].some(x=>x.getBoundingClientRect().right>1015)")
        if gap < 16 or wide:
            sys.exit(f"Texte trop long (espace={gap:.0f}px, trop large={wide}) : raccourcir le titre, les points ou le bouton.")
        pg.screenshot(path=out, type="jpeg", quality=92)
        b.close()
    print("OK", out)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
