#!/usr/bin/env python3
"""Build static pages for The Story Corner (Bright Mind Kids).

Run from the repo root:  python3 build.py
Reads posts.json, books.json, book_pages.json, site.json and writes:
  posts/<slug>.html, books/<slug>.html, books.html,
  activities/<slug>.html, sitemap.xml
Safe to run any number of times.
"""
import json, os, re, html, random, datetime

SITE = "https://brightmindkids.github.io"
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

def load(p, d):
    try:
        with open(p, encoding="utf-8") as f: return json.load(f)
    except Exception: return d

posts = load("posts.json", [])
books = load("books.json", [])
extra = load("book_pages.json", {})
site = load("site.json", {})
e = lambda s: html.escape(str(s or ""), quote=True)

def slugify(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:60] or "book"

for b in books:
    x = extra.get(b.get("asin"), {})
    b.update({k: v for k, v in x.items()})
    b.setdefault("slug", slugify(b.get("title", "")))
    b["url"] = f"books/{b['slug']}.html"
    b["amazon"] = "https://www.amazon.com/dp/" + b.get("asin", "")

posts = [p for p in posts if p.get("slug") and p.get("status") != "draft"]
posts.sort(key=lambda p: str(p.get("date", "")), reverse=True)

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@400;700;800&display=swap" rel="stylesheet">'
ICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 34 34'%3E%3Ccircle cx='17' cy='17' r='17' fill='%23FFC94A'/%3E%3Cpath d='M7 22c4-2 7-2 10 0 3-2 6-2 10 0V11c-4-2-7-2-10 0-3-2-6-2-10 0z' fill='%231F2A4A'/%3E%3C/svg%3E"
LOGO = '<svg width="34" height="34" viewBox="0 0 34 34" aria-hidden="true"><circle cx="17" cy="17" r="17" fill="#FFC94A"/><path d="M7 22c4-2 7-2 10 0 3-2 6-2 10 0V11c-4-2-7-2-10 0-3-2-6-2-10 0z" fill="#1F2A4A"/><path d="M17 11v11" stroke="#FFC94A" stroke-width="1.6"/></svg>'

CSS = """
:root{--navy:#1F2A4A;--sun:#FFC94A;--cream:#FFF8EC;--teal:#236A78;--soft:#5A6482;--line:#EADFC9}
*{box-sizing:border-box;min-width:0}
body{margin:0;background:#FDEDE3;color:var(--navy);font:17px/1.6 Nunito,system-ui,sans-serif;overflow-x:clip}
h1,h2,h3{font-family:Fredoka,Nunito,sans-serif;line-height:1.1;margin:0;text-wrap:balance}
a{color:inherit}
.wrap{max-width:1100px;margin:0 auto;padding:0 max(5vw,16px)}
header{background:var(--navy);color:var(--cream)}
.bar{display:flex;align-items:center;gap:16px;flex-wrap:wrap;padding-block:14px}
.logo{display:flex;align-items:center;gap:10px;font:600 21px Fredoka,sans-serif;text-decoration:none}
nav{display:flex;gap:6px;flex-wrap:wrap;margin-left:auto}
nav a{text-decoration:none;font-weight:700;font-size:15px;padding:10px 14px;border-radius:999px;min-height:44px;display:inline-flex;align-items:center}
nav a:hover,nav a:focus-visible,nav a[aria-current]{background:rgba(255,255,255,.14);outline:none}
.btn{display:inline-flex;align-items:center;min-height:48px;padding:10px 20px;border-radius:999px;background:var(--sun);color:var(--navy);font-weight:800;text-decoration:none;border:0;font-size:16px;cursor:pointer;font-family:Nunito,sans-serif}
.btn.dark{background:var(--navy);color:var(--cream)}
.btn:focus-visible{outline:3px solid var(--teal);outline-offset:2px}
footer{background:var(--navy);color:#C9D0E2;padding:26px 0;font-size:15px;margin-top:40px}
footer .wrap{display:flex;gap:14px;flex-wrap:wrap;justify-content:space-between}
.crumb{font-size:14px;color:var(--soft);padding-top:22px}.crumb a{color:var(--teal);font-weight:700}
.signup{background:var(--navy);color:var(--cream);border-radius:28px;padding:clamp(20px,3vw,34px);margin:34px 0;display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:20px;align-items:center}
.signup h2{font-size:clamp(24px,3vw,32px)}.signup p{margin:8px 0 0;color:#D9DEEC}
.signup form{display:flex;flex-direction:column;gap:10px}
.signup input[type=email]{font:16px Nunito,sans-serif;padding:12px 16px;border-radius:14px;border:0;min-height:50px}
.signup label{font-size:14px;color:#D9DEEC;display:flex;gap:8px;align-items:flex-start}
.signup .ok{display:none;background:var(--sun);color:var(--navy);border-radius:16px;padding:14px;font-weight:800}
.signup.sent form{display:none}.signup.sent .ok{display:block}
@media(max-width:720px){.signup{grid-template-columns:minmax(0,1fr)}}
@media print{header,footer,.noprint,.signup,.skyband::before,.skyband::after{display:none!important}body{background:#fff}}
.skyband{position:relative;background:linear-gradient(#CDEBEF,#A9DAE2);padding:10px 0 56px;margin-bottom:10px}
.skyband::after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:28px;background:radial-gradient(circle at 30px 30px,#FDEDE3 29px,transparent 30px) 0 0/60px 28px repeat-x}
.skyband::before{content:"";position:absolute;inset:0;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='420' height='160'%3E%3Cg fill='none' stroke='white' stroke-width='3' stroke-linecap='round' opacity='.9'%3E%3Cpath d='M40 60q6-20 26-15q9-16 27-6q22-3 20 21h-73z'/%3E%3Cpath d='M300 110q5-16 21-12q8-14 23-4q18-3 16 16h-60z'/%3E%3C/g%3E%3C/svg%3E") 0 0 repeat-x;pointer-events:none;animation:driftbg 40s linear infinite}
@keyframes driftbg{from{background-position:0 0}to{background-position:420px 0}}
@media(prefers-reduced-motion:reduce){.skyband::before{animation:none}}
.skyband>.wrap{position:relative;z-index:1}
.skyband h1{color:#7A4A1E}

"""

def nav(cur=""):
    items = [("index.html", "Stories"), ("books.html", "Books"), ("games.html", "Kids' games"),
             ("manners.html", "Manners cards"), ("bedtime.html", "Bedtime chart")]
    return "".join(f'<a href="{{R}}{h}"{" aria-current=\"page\"" if h == cur else ""}>{t}</a>' for h, t in items)

def page(title, desc, body, *, depth=0, cur="", canonical="", image="", jsonld=None, extra_css="", ogtype="website"):
    R = "../" * depth
    canon = SITE + "/" + canonical
    img = SITE + "/" + image if image else SITE + "/covers/B0HSJPX51V.jpg"
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    head = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="{ogtype}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{ICON}">
{FONTS}
<style>{CSS}{extra_css}</style>
{ld}
</head>
<body>
<header><div class="wrap bar"><a class="logo" href="{R}index.html">{LOGO} Bright Mind Kids</a><nav aria-label="Main">{nav(cur).replace("{R}", R)}</nav></div></header>
"""
    foot = f"""<footer><div class="wrap"><span>© {datetime.date.today().year} Bright Mind Kids · The Story Corner</span><span><a href="{R}books.html">Our books</a> · <a href="{R}games.html">Kids' games</a> · <a href="{R}manners.html">Manners cards</a> · <a href="{R}bedtime.html">Bedtime chart</a></span></div></footer>
{signup_js()}
</body></html>"""
    return head + body.replace("{R}", R) + foot

def signup_block(where=""):
    s = site.get("signup", {})
    if not (s.get("action") and s.get("email_entry")):
        return ""
    return f"""<section class="signup" aria-label="Free weekly activity">
<div><h2>A free activity every week</h2><p>Colouring pages, printables and gentle reading tips for kids aged 3 to 8, straight to your inbox. No spam, unsubscribe anytime.</p></div>
<div><form data-signup data-where="{e(where)}">
<input type="email" name="email" required placeholder="Your email address" aria-label="Your email address" autocomplete="email">
<label><input type="checkbox" required> I'm a parent or carer aged 18+ and I'd like to receive emails from Bright Mind Kids.</label>
<button class="btn" type="submit">Send me free activities</button></form>
<div class="ok" role="status">Thank you! Your first free activity is on its way. 💛</div></div></section>"""

def signup_js():
    s = site.get("signup", {})
    if not (s.get("action") and s.get("email_entry")):
        return ""
    cfg = json.dumps({"action": s["action"], "email": s["email_entry"], "where": s.get("where_entry", "")})
    return """<script>{const C=%s;document.querySelectorAll('form[data-signup]').forEach(f=>f.addEventListener('submit',ev=>{ev.preventDefault();const d=new FormData();d.append(C.email,f.email.value.trim());if(C.where)d.append(C.where,f.dataset.where||location.pathname);fetch(C.action,{method:'POST',mode:'no-cors',body:d}).catch(()=>{}).finally(()=>f.closest('.signup').classList.add('sent'))}))}</script>""" % cfg

def blocks(body):
    out = []
    for b in body or []:
        if "h" in b: out.append(f"<h2>{e(b['h'])}</h2>")
        elif "ul" in b: out.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in b["ul"]) + "</ul>")
        elif "tip" in b: out.append(f'<div class="tip"><b>Try this tonight</b><p>{e(b["tip"])}</p></div>')
        elif "p" in b: out.append(f"<p>{e(b['p'])}</p>")
    return "\n".join(out)

def fmt(d):
    try: return datetime.date.fromisoformat(str(d)).strftime("%B %-d, %Y")
    except Exception: return e(d)

POST_CSS = """
.art{max-width:760px;margin:0 auto;padding:0 max(5vw,16px) 20px}
.art .hero{width:100%;aspect-ratio:16/9;object-fit:cover;object-position:center 45%;border-radius:24px;margin:16px 0 22px;display:block;background:#EAF4FB}
.meta{font-size:14px;color:var(--soft);font-weight:700;display:flex;gap:12px;flex-wrap:wrap}.meta .cat{color:var(--teal);font-weight:800}
.art h1{font-size:clamp(32px,5vw,46px);margin:10px 0 14px}
.art h2{font-size:26px;margin:30px 0 8px}.art p{margin:0 0 16px}.art ul{padding-left:22px}.art li{margin-bottom:8px}
.tip{background:#F5EBD7;border-radius:18px;padding:16px 20px;margin:22px 0}.tip b{font-family:Fredoka,sans-serif;font-size:19px}.tip p{margin:4px 0 0}
.src{border-top:2px solid var(--line);margin-top:30px;padding-top:16px;font-size:15px}.src h3{font-size:18px;margin-bottom:8px}.src a{color:var(--teal);font-weight:700;overflow-wrap:anywhere}
.plug{margin-top:30px;background:var(--navy);color:var(--cream);border-radius:22px;padding:18px;display:grid;grid-template-columns:110px minmax(0,1fr);gap:16px;align-items:center}
.plug img{width:110px;height:110px;border-radius:12px;object-fit:cover}.plug p{margin:4px 0 10px;color:#D9DEEC;font-size:15px}
.more{max-width:1100px;margin:30px auto 0;padding:0 max(5vw,16px)}.more h2{font-size:28px;margin-bottom:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,280px),1fr));gap:18px}
.card{background:#fff;border-radius:20px;overflow:hidden;text-decoration:none;display:flex;flex-direction:column}
.card img,.card .ph{width:100%;height:160px;object-fit:cover;object-position:center 45%;display:block}
.card .t{padding:14px 18px 18px}.card h3{font-size:20px;margin-top:6px}
@media(max-width:560px){.plug{grid-template-columns:minmax(0,1fr)}}
"""

def ph(p):
    c = p.get("color") if re.fullmatch(r"#[0-9a-fA-F]{3,8}", str(p.get("color", ""))) else "#236A78"
    return f'<svg class="ph" viewBox="0 0 400 160" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><rect width="400" height="160" fill="{c}"/><circle cx="330" cy="40" r="22" fill="#FFC94A"/><path d="M130 130 L200 136 L200 76 L130 70Z" fill="#FFF8EC"/><path d="M270 130 L200 136 L200 76 L270 70Z" fill="#F1E3C6"/></svg>'

def card(p, R=""):
    img = f'<img src="{R}{e(p["image"])}" alt="" loading="lazy">' if p.get("image") else ph(p)
    return f'<a class="card" href="{R}posts/{e(p["slug"])}.html">{img}<div class="t"><div class="meta"><span class="cat">{e(p.get("category"))}</span><span>{fmt(p.get("date"))}</span></div><h3>{e(p.get("title"))}</h3></div></a>'

def build_posts():
    os.makedirs("posts", exist_ok=True)
    keep = set()
    for i, p in enumerate(posts):
        slug = p["slug"]; keep.add(slug + ".html")
        bk = books[i % len(books)] if books else None
        img = f'<img class="hero" src="../{e(p["image"])}" alt="">' if p.get("image") else ""
        src = ""
        if p.get("sources"):
            src = '<div class="src"><h3>Sources</h3><ul>' + "".join(
                f'<li><a href="{e(s.get("url"))}" rel="nofollow noopener">{e(s.get("title"))}</a></li>'
                for s in p["sources"] if str(s.get("url", "")).startswith("http")) + "</ul></div>"
        plug = ""
        if bk:
            plug = f'<div class="plug"><img src="../{e(bk.get("cover"))}" alt="Cover of {e(bk["title"])}"><div><b style="font-family:Fredoka,sans-serif;font-size:20px">{e(bk["title"])}</b><p>{e(bk.get("blurb"))}</p><a class="btn" href="../{e(bk["url"])}">See the book</a></div></div>'
        others = [q for q in posts if q["slug"] != slug][:3]
        body = f"""<main><div class="art"><p class="crumb"><a href="../index.html">The Story Corner</a> › {e(p.get("category"))}</p>
<div class="meta" style="margin-top:12px"><span class="cat">{e(p.get("category"))}</span><span>{fmt(p.get("date"))}</span><span>{e(p.get("read"))} min read</span></div>
<h1>{e(p.get("title"))}</h1>{img}
{blocks(p.get("body"))}
{src}{plug}{signup_block("post:" + slug)}</div>
<section class="more"><h2>More for parents</h2><div class="grid">{"".join(card(q, "../") for q in others)}</div></section></main>"""
        ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p.get("title"),
              "description": p.get("excerpt"), "datePublished": str(p.get("date")),
              "author": {"@type": "Organization", "name": "Bright Mind Kids"},
              "publisher": {"@type": "Organization", "name": "Bright Mind Kids"},
              "mainEntityOfPage": f"{SITE}/posts/{slug}.html"}
        if p.get("image"): ld["image"] = f"{SITE}/{p['image']}"
        out = page(f'{p.get("title")} · The Story Corner', p.get("excerpt", ""), body, depth=1,
                   canonical=f"posts/{slug}.html", image=p.get("image", ""), jsonld=ld, extra_css=POST_CSS, ogtype="article")
        with open(f"posts/{slug}.html", "w", encoding="utf-8") as f: f.write(out)
    for fn in os.listdir("posts"):
        if fn.endswith(".html") and fn not in keep: os.remove(os.path.join("posts", fn))

BOOK_CSS = """
.bk{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:clamp(20px,4vw,48px);align-items:start;padding:22px 0 10px}
.bk .cov{width:100%;border-radius:22px;box-shadow:0 22px 44px -18px rgba(31,42,74,.6);display:block;background:#fff}
.bk h1{font-size:clamp(34px,5vw,50px)}.bk .subt{font:600 20px Fredoka,sans-serif;color:var(--teal);margin:8px 0 0}
.facts{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}.facts span{background:#F5EBD7;border-radius:999px;padding:6px 14px;font-weight:800;font-size:14px}
.learn{list-style:none;padding:0;margin:18px 0}.learn li{padding:8px 0 8px 34px;position:relative}.learn li::before{content:"";position:absolute;left:0;top:10px;width:22px;height:22px;border-radius:50%;background:var(--sun)}
.acts{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px}
.prev{margin:30px 0}.prev h2,.freeact h2{font-size:30px;margin-bottom:14px}
.strip{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(min(86%,560px),1fr);gap:16px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:10px}
.strip img{width:100%;border-radius:16px;scroll-snap-align:start;display:block;box-shadow:0 10px 24px -16px rgba(31,42,74,.6)}
.freeact{background:#fff;border-radius:26px;padding:clamp(18px,3vw,30px);display:grid;grid-template-columns:minmax(0,1fr) auto;gap:16px;align-items:center;margin:26px 0}
.freeact p{margin:6px 0 0;color:var(--soft)}
.shelf{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,240px),1fr));gap:20px;padding:24px 0}
.bcard{background:#fff;border-radius:22px;padding:16px;text-decoration:none;display:flex;flex-direction:column;gap:8px}
.bcard img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:14px}.bcard h2{font-size:22px}.bcard p{margin:0;color:var(--soft);font-size:15px}
@media(max-width:720px){.bk,.freeact{grid-template-columns:minmax(0,1fr)}}
"""

def build_books():
    os.makedirs("books", exist_ok=True)
    for b in books:
        prev = ""
        if b.get("previews"):
            prev = '<section class="prev"><h2>Look inside</h2><div class="strip">' + "".join(
                f'<img src="../{e(x)}" alt="Inside pages of {e(b["title"])}" loading="lazy">' for x in b["previews"]) + "</div></section>"
        act = b.get("activity")
        actblock = f'<section class="freeact"><div><h2>Free activity: {e(act["title"])}</h2><p>{e(act["desc"])} Print it at home, no sign-up needed.</p></div><a class="btn dark" href="../activities/{e(act["slug"])}.html">Get the free printable</a></section>' if act else ""
        learn = "".join(f"<li>{e(x)}</li>" for x in b.get("learn", []))
        body = f"""<main><div class="skyband"><div class="wrap"><p class="crumb"><a href="../books.html">Our books</a> › {e(b["title"])}</p>
<section class="bk"><img class="cov" src="../{e(b.get("cover"))}" alt="Cover of {e(b["title"])}">
<div><h1>{e(b["title"])}</h1>{f'<p class="subt">{e(b.get("subtitle"))}</p>' if b.get("subtitle") else ""}
<div class="facts"><span>Ages {e(b.get("ages", "3–8"))}</span><span>{e(b.get("format", "Paperback"))}</span><span>by Bright Mind Kids</span></div>
<p>{e(b.get("about") or b.get("blurb"))}</p>
{f'<h2 style="font-size:24px;margin-top:20px">What your child will learn</h2><ul class="learn">{learn}</ul>' if learn else ""}
{f'<p style="color:var(--soft)">{e(b.get("extras"))}</p>' if b.get("extras") else ""}
<div class="acts"><a class="btn" href="{e(b["amazon"])}" rel="noopener">Buy on Amazon</a>{f'<a class="btn dark" href="../activities/{e(act["slug"])}.html">Free activity</a>' if act else ""}</div></div></section></div></div>
<div class="wrap">{prev}{actblock}{signup_block("book:" + b["slug"])}</div></main>"""
        ld = {"@context": "https://schema.org", "@type": "Book", "name": b["title"], "author": {"@type": "Organization", "name": "Bright Mind Kids"},
              "image": f"{SITE}/{b.get('cover')}", "description": b.get("about") or b.get("blurb"), "typicalAgeRange": str(b.get("ages", "")).replace("–", "-"),
              "url": f"{SITE}/{b['url']}", "sameAs": b["amazon"]}
        out = page(f'{b["title"]} · Children\'s book by Bright Mind Kids', b.get("blurb", ""), body, depth=1, cur="books.html",
                   canonical=b["url"], image=b.get("cover", ""), jsonld=ld, extra_css=BOOK_CSS, ogtype="book")
        with open(b["url"], "w", encoding="utf-8") as f: f.write(out)
    cards = "".join(f'<a class="bcard" href="{e(b["url"])}"><img src="{e(b.get("cover"))}" alt="Cover of {e(b["title"])}" loading="lazy"><h2>{e(b["title"])}</h2><p>{e(b.get("blurb"))}</p><span class="btn" style="align-self:flex-start">See the book</span></a>' for b in books)
    body = f"""<main><div class="skyband"><div class="wrap"><h1 style="font-size:clamp(34px,5vw,54px);padding-top:30px">Our picture books</h1>
<p style="max-width:40em">Gentle stories and activity books for children aged 3 to 8, each with a free printable activity to enjoy together.</p></div></div>
<div class="wrap"><div class="shelf">{cards}</div>{signup_block("books")}</div></main>"""
    with open("books.html", "w", encoding="utf-8") as f:
        f.write(page("Our picture books · Bright Mind Kids", "Picture books for kids aged 3 to 8 by Bright Mind Kids, each with a free printable activity.", body, cur="books.html", canonical="books.html", extra_css=BOOK_CSS))

# ---------------- activities ----------------
ACT_CSS = """
.act{max-width:860px;margin:0 auto;padding:0 max(5vw,16px)}
.act h1{font-size:clamp(32px,5vw,46px);margin:10px 0}
.tools{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0}
.sheet{background:#fff;border-radius:20px;padding:24px;box-shadow:0 12px 30px -20px rgba(31,42,74,.6)}
.sheet svg{width:100%;height:auto;display:block}
.sheet .ttl{font:700 30px Fredoka,sans-serif;text-align:center;margin-bottom:6px}
.sheet .nm{text-align:center;font-size:16px;color:#555;margin-bottom:10px}
.sheet .ft{display:flex;justify-content:space-between;font-size:13px;color:#777;margin-top:10px}
.from{display:flex;gap:16px;align-items:center;background:#fff;border-radius:22px;padding:16px;margin:24px 0}
.from img{width:90px;height:90px;border-radius:12px;object-fit:cover}
@media print{@page{size:A4;margin:10mm}.act>*:not(.sheet){display:none!important}.sheet{box-shadow:none;padding:0}.act{padding:0;max-width:none}}
"""
K = 'stroke="#1F2A4A" stroke-width="4" stroke-linejoin="round" stroke-linecap="round" fill="#fff"'

def svg_finn():
    return f"""<svg viewBox="0 0 600 700" role="img" aria-label="Colouring page of Finn the fennec fox under the stars">
<rect x="4" y="4" width="592" height="692" rx="24" {K}/>
<path d="M470 70a60 60 0 1 0 40 100a50 50 0 0 1-40-100z" {K}/>
{''.join(f'<path d="M{x} {y}l7 15 16 2-12 11 3 16-14-8-14 8 3-16-12-11 16-2z" {K}/>' for x,y in [(90,80),(200,140),(330,70),(110,230),(520,250)])}
<path d="M40 620q260-60 520 0v70H40z" {K}/>
<path d="M200 330l-60-170 120 120z" {K}/><path d="M400 330l60-170-120 120z" {K}/>
<path d="M175 250l-20-55 55 55M425 250l20-55-55 55" fill="none" stroke="#1F2A4A" stroke-width="3"/>
<ellipse cx="300" cy="350" rx="120" ry="100" {K}/>
<path d="M300 380l-30 20q30 30 60 0z" {K}/>
<circle cx="255" cy="335" r="14" {K}/><circle cx="345" cy="335" r="14" {K}/>
<circle cx="300" cy="392" r="10" fill="#1F2A4A"/>
<path d="M210 430q-30 90 0 170h180q30-80 0-170" {K}/>
<path d="M245 600v-60M355 600v-60" fill="none" stroke="#1F2A4A" stroke-width="4"/>
<path d="M390 560q120 10 120-60q0-40-40-40q20 50-80 70" {K}/>
<path d="M250 500q50 30 100 0" fill="none" stroke="#1F2A4A" stroke-width="4"/>
<rect x="470" y="520" width="50" height="70" rx="10" {K}/><path d="M480 520v-16h30v16M495 540v30" fill="none" stroke="#1F2A4A" stroke-width="4"/>
</svg>"""

ANIMALS = {
 "sheep": lambda x, y: f'<g transform="translate({x} {y})"><path d="M-30 0a14 14 0 0 1 12-20a16 16 0 0 1 28-2a14 14 0 0 1 18 14a12 12 0 0 1-6 22H-22a12 12 0 0 1-8-14z" {K}/><ellipse cx="-30" cy="-4" rx="12" ry="10" {K}/><path d="M-14 14v14M14 14v14" {K}/></g>',
 "bird": lambda x, y: f'<g transform="translate({x} {y})"><ellipse cx="0" cy="0" rx="26" ry="18" {K}/><circle cx="20" cy="-14" r="11" {K}/><path d="M30 -14l12 4-12 4" {K}/><path d="M-6 -4q-10 -16 -24 -10q8 12 24 10" {K}/></g>',
 "turtle": lambda x, y: f'<g transform="translate({x} {y})"><path d="M-30 8a30 26 0 0 1 60 0z" {K}/><circle cx="38" cy="2" r="9" {K}/><path d="M-20 8v10M20 8v10" {K}/><path d="M-12 -8l12 -8 12 8" fill="none" stroke="#1F2A4A" stroke-width="3"/></g>',
 "butterfly": lambda x, y: f'<g transform="translate({x} {y})"><path d="M0 0q-30-34-36-4q4 24 36 4zM0 0q30-34 36-4q-4 24-36 4zM0 0q-24 30-28 14q0-14 28-14zM0 0q24 30 28 14q0-14-28-14z" {K}/><path d="M0-14v30" fill="none" stroke="#1F2A4A" stroke-width="4"/></g>',
 "rabbit": lambda x, y: f'<g transform="translate({x} {y})"><ellipse cx="0" cy="8" rx="22" ry="18" {K}/><circle cx="18" cy="-12" r="12" {K}/><path d="M14-22q-4-24 4-26q6 2 2 26M24-22q4-24 10-22q4 6-6 24" {K}/></g>',
}

def svg_count():
    rnd = random.Random(7)
    rows = [("sheep", 2), ("bird", 4), ("turtle", 2), ("butterfly", 3), ("rabbit", 4)]
    g = []
    y = 70
    for name, n in rows:
        for i in range(n):
            g.append(f'<g transform="translate({70 + i * 100 + rnd.randint(-4, 4)} {y + rnd.randint(-4, 4)}) scale(1.1)">' + ANIMALS[name](0, 0) + "</g>")
        g.append(f'<rect x="510" y="{y-30}" width="60" height="60" rx="12" {K}/>')
        y += 110
    return f'<svg viewBox="0 0 600 620" role="img" aria-label="Counting page with animals two by two">{"".join(g)}<path d="M480 30v560" fill="none" stroke="#E9DCC2" stroke-width="3" stroke-dasharray="6 10"/></svg>'

def svg_maze(seed=11, N=9):
    rnd = random.Random(seed)
    W = [[{"n":1,"s":1,"e":1,"w":1,"v":0} for _ in range(N)] for _ in range(N)]
    st = [(0, 0)]; W[0][0]["v"] = 1
    while st:
        x, y = st[-1]
        nb = [(x+dx, y+dy, a, b) for dx, dy, a, b in ((0,-1,"n","s"),(0,1,"s","n"),(1,0,"e","w"),(-1,0,"w","e")) if 0 <= x+dx < N and 0 <= y+dy < N and not W[y+dy][x+dx]["v"]]
        if not nb: st.pop(); continue
        nx, ny, a, b = rnd.choice(nb); W[y][x][a] = 0; W[ny][nx][b] = 0; W[ny][nx]["v"] = 1; st.append((nx, ny))
    S = 520 / N; o = 50; d = []
    for y in range(N):
        for x in range(N):
            c = W[y][x]; X = o + x*S; Y = o + y*S
            if c["n"] and not (x == 0 and y == 0): d.append(f"M{X:.1f} {Y:.1f}h{S:.1f}")
            if c["w"]: d.append(f"M{X:.1f} {Y:.1f}v{S:.1f}")
            if y == N-1 and c["s"] and not (x == N-1): d.append(f"M{X:.1f} {Y+S:.1f}h{S:.1f}")
            if x == N-1 and c["e"]: d.append(f"M{X+S:.1f} {Y:.1f}v{S:.1f}")
    fish = f'<g transform="translate({o+S/2-4} {o-12})"><path d="M-18 -14q14-14 28 0q-14 14-28 0z" {K}/><path d="M-18-14l-10-8v16z" {K}/></g>'
    whale = f'<g transform="translate({o+520-S/2} {o+520+44})"><path d="M-46 0q0-30 46-30q40 0 46 24q-8 22-46 22q-46 0-46-16z" {K}/><path d="M-46 0l-20-16v30z" {K}/><circle cx="20" cy="-10" r="4" fill="#1F2A4A"/><path d="M0-34q-4-14 6-18M0-34q8-12 16-8" fill="none" stroke="#1F2A4A" stroke-width="3"/></g>'
    return f'<svg viewBox="0 0 620 640" role="img" aria-label="Ocean maze from a little fish to a whale"><path d="{"".join(d)}" fill="none" stroke="#1F2A4A" stroke-width="5" stroke-linecap="round"/>{fish}{whale}<text x="{o+30}" y="{o-14}" font-family="Fredoka, Arial, sans-serif" font-size="20" fill="#1F2A4A">START</text><text x="{o+330}" y="{o+560}" font-family="Fredoka, Arial, sans-serif" font-size="20" fill="#1F2A4A">FINISH</text></svg>'

def svg_promise():
    items = ["I ask a grown-up before using a screen.", "I take a screen break to move and play.", "I am kind to others, online and offline.",
             "No screens at meals or bedtime.", "I put the device away when time is up.", "If something feels wrong, I tell a grown-up."]
    g = ['<rect x="30" y="20" width="110" height="300" rx="30" ' + K + '/>'] + [f'<circle cx="85" cy="{y}" r="36" {K}/>' for y in (80, 170, 260)]
    g += [f'<text x="160" y="{v}" font-family="Fredoka, Arial, sans-serif" font-size="22" fill="#1F2A4A">{t}</text>' for v, t in ((88, "Red: screens off, time to play!"), (178, "Yellow: almost time to stop."), (268, "Green: OK to use, with a grown-up."))]
    y = 380
    for t in items:
        g.append(f'<rect x="40" y="{y-26}" width="34" height="34" rx="8" {K}/><text x="92" y="{y}" font-family="Nunito, Arial, sans-serif" font-size="22" fill="#1F2A4A">{e(t)}</text>')
        y += 52
    g.append(f'<text x="40" y="{y+30}" font-family="Nunito, Arial, sans-serif" font-size="20" fill="#1F2A4A">Signed: ____________________   Grown-up: ____________________</text>')
    return f'<svg viewBox="0 0 600 {y+60}" role="img" aria-label="Screen-time promise with a traffic light to colour">{"".join(g)}</svg>'

ACT_SVG = {"colour-finn": svg_finn, "count-the-animals": svg_count, "ocean-maze": svg_maze, "screen-time-promise": svg_promise}
ACT_HELP = {"colour-finn": "Colour Finn, the moon, the stars and the lantern. What colour will Finn's pyjamas be tonight?",
            "count-the-animals": "Count each row of animals and write the number in the box. Can you spot which animals came two by two?",
            "ocean-maze": "Help the little fish swim through the ocean maze to reach the friendly whale.",
            "screen-time-promise": "Colour the traffic light, tick each promise together, and sign it as a family."}

def build_acts():
    os.makedirs("activities", exist_ok=True)
    for b in books:
        a = b.get("activity")
        if not a or a["slug"] not in ACT_SVG: continue
        body = f"""<main class="act"><p class="crumb"><a href="../books/{e(b["slug"])}.html">{e(b["title"])}</a> › Free activity</p>
<h1>{e(a["title"])}</h1><p>{e(ACT_HELP.get(a["slug"], a["desc"]))} Free to print for home and classroom use.</p>
<div class="tools"><button class="btn" onclick="window.print()">Print this page</button><a class="btn dark" href="../books/{e(b["slug"])}.html">About the book</a></div>
<div class="sheet"><div class="ttl">{e(a["title"])}</div><div class="nm">Name: ______________________</div>{ACT_SVG[a["slug"]]()}<div class="ft"><span>From "{e(b["title"])}" by Bright Mind Kids</span><span>brightmindkids.github.io</span></div></div>
<div class="from"><img src="../{e(b.get("cover"))}" alt="Cover of {e(b["title"])}"><div><b style="font-family:Fredoka,sans-serif;font-size:20px">Enjoyed this? Read the story.</b><p style="margin:4px 0 10px;color:var(--soft)">{e(b.get("blurb"))}</p><a class="btn" href="{e(b["amazon"])}" rel="noopener">See it on Amazon</a></div></div>
{signup_block("activity:" + a["slug"])}</main>"""
        out = page(f'{a["title"]} · Free printable for kids', a["desc"], body, depth=1, canonical=f'activities/{a["slug"]}.html', image=b.get("cover", ""), extra_css=ACT_CSS)
        with open(f'activities/{a["slug"]}.html', "w", encoding="utf-8") as f: f.write(out)

def build_sitemap():
    urls = [("", "daily", "1.0"), ("books.html", "weekly", "0.9"), ("games.html", "monthly", "0.8"), ("manners.html", "monthly", "0.8"), ("bedtime.html", "monthly", "0.8")]
    urls += [(b["url"], "monthly", "0.9") for b in books]
    urls += [(f'activities/{b["activity"]["slug"]}.html', "monthly", "0.8") for b in books if b.get("activity") and b["activity"]["slug"] in ACT_SVG]
    urls += [(f'posts/{p["slug"]}.html', "monthly", "0.7") for p in posts]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"  <url><loc>{SITE}/{u}</loc><changefreq>{c}</changefreq><priority>{p}</priority></url>\n" for u, c, p in urls) + "</urlset>\n"
    with open("sitemap.xml", "w", encoding="utf-8") as f: f.write(xml)

def write_book_links():
    raw = load("books.json", [])
    for r in raw:
        b = next((x for x in books if x.get("asin") == r.get("asin")), None)
        if b: r["page"] = b["url"]
    with open("books.json", "w", encoding="utf-8") as f: json.dump(raw, f, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    write_book_links(); build_posts(); build_books(); build_acts(); build_sitemap()
    print(f"Built {len(posts)} posts, {len(books)} books, sitemap updated.")
