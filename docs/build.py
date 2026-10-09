"""Generate docs/index.html for GitHub Pages from the catalog and transcript.

Standard library only. Run from anywhere:  python3 docs/build.py
The landing page leads with the courses that are actually built ("Open now")
and shows everything still "planned" as a roadmap below.
"""
import html
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/orgito1015/Gitoversity"
CATALOG = ROOT / "catalog" / "README.md"
TRANSCRIPT = ROOT / "catalog" / "TRANSCRIPT.md"
OUT = ROOT / "docs" / "index.html"

STATUS_CLASS = {
    "passed": "passed",
    "built, awaiting pass": "built",
    "in progress": "progress",
    "planned": "planned",
}
STATUS_LABEL = {"built, awaiting pass": "open", "in progress": "in progress"}


def esc(s):
    return html.escape(s.strip())


def pill(status):
    cls = STATUS_CLASS.get(status.strip().lower(), "planned")
    label = STATUS_LABEL.get(status.strip().lower(), status.strip())
    return f'<span class="pill {cls}">{esc(label)}</span>'


def split_faculty(name):
    """'AIRT: AI Red Teaming' -> ('AIRT', 'AI Red Teaming')."""
    if ":" in name:
        code, _, rest = name.partition(":")
        return code.strip(), rest.strip()
    return "", name.strip()


def parse_catalog(md):
    """Return [(faculty_name, [(code, title, status), ...]), ...]."""
    faculties, current = [], None
    for line in md.splitlines():
        line = line.rstrip()
        if line.startswith("## "):
            current = (line[3:].strip(), [])
            faculties.append(current)
        elif line.startswith("|") and current is not None:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3 and cells[0].lower() != "course" and not set(cells[0]) <= {"-", ":"} and cells[0]:
                current[1].append((cells[0], cells[1], cells[2]))
    return [f for f in faculties if f[1]]


def parse_transcript(md):
    """Return [(course, passed_on, shipped), ...] of real (non-empty) rows."""
    rows = []
    for line in md.splitlines():
        line = line.rstrip()
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3 and cells[0].lower() != "course" and not all(set(c) <= {"-", ":"} for c in cells):
                if any(cells):
                    rows.append(cells[:3])
    return rows


def render_available(faculties):
    cards = []
    for faculty, courses in faculties:
        fcode, fname = split_faculty(faculty)
        for code, title, status in courses:
            if status.strip().lower() == "planned":
                continue
            cards.append(f"""      <a class="course" href="{REPO}/tree/main/{esc(code)}">
        <div class="course-head"><span class="code">{esc(code)}</span>{pill(status)}</div>
        <h3>{esc(title)}</h3>
        <p class="faculty"><span class="fchip">{esc(fcode)}</span>{esc(fname)}</p>
        <span class="start">Start the course <span class="arrow">&rarr;</span></span>
      </a>""")
    if not cards:
        return '<p class="empty">No courses are open yet. The roadmap below is what is coming.</p>'
    return '<div class="courses">\n' + "\n".join(cards) + "\n    </div>"


def render_roadmap(faculties):
    blocks = []
    for faculty, courses in faculties:
        fcode, fname = split_faculty(faculty)
        remaining = [(c, t, s) for c, t, s in courses if s.strip().lower() == "planned"]
        if not remaining:
            continue
        items = "".join(
            f'<li><span class="rcode">{esc(c)}</span><span class="rtitle">{esc(t)}</span></li>'
            for c, t, s in remaining
        )
        blocks.append(f"""      <div class="faculty">
        <div class="faculty-name"><span class="fchip">{esc(fcode)}</span>{esc(fname)}</div>
        <ul class="road">{items}</ul>
      </div>""")
    return '<div class="roadmap-grid">\n' + "\n".join(blocks) + "\n    </div>"


def render_transcript(rows):
    if not rows:
        return ('<div class="transcript-empty">'
                '<span class="mono">$ cat transcript.md</span>'
                '<p>No courses passed yet. A row lands here when a writeup and its shipped '
                'output go public. Be the first.</p></div>')
    body = "".join(
        f"<tr><td>{esc(c)}</td><td>{esc(p)}</td><td>{esc(s)}</td></tr>" for c, p, s in rows
    )
    return (f'<table class="ledger"><thead><tr><th>Course</th><th>Passed</th>'
            f'<th>Shipped</th></tr></thead><tbody>{body}</tbody></table>')


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gitoversity</title>
<meta name="description" content="An open university for offensive security. Learn by building, prove it by shipping.">
<meta property="og:title" content="Gitoversity">
<meta property="og:description" content="An open university for offensive security. Learn by building, prove it by shipping.">
<meta property="og:image" content="{repo_raw}/gitoversity.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="gitoversity.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    color-scheme: dark;
    --bg:#070810; --bg2:#0c0e1a; --fg:#e8edf6; --muted:#8a93a8;
    --card:#0f1320; --line:#1e2436; --accent:#3b82f6; --accent2:#60a5fa; --glow:rgba(59,130,246,.35);
    --green:#2ea043; --amber:#d29922;
    --mono:'JetBrains Mono', ui-monospace, monospace;
    --sans:'Space Grotesk', system-ui, sans-serif;
  }}
  * {{ box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{
    margin:0; background:var(--bg); color:var(--fg); font-family:var(--sans); line-height:1.6;
    background-image:
      radial-gradient(60rem 40rem at 50% -10rem, rgba(59,130,246,.18), transparent 60%),
      linear-gradient(var(--line) 1px, transparent 1px),
      linear-gradient(90deg, var(--line) 1px, transparent 1px);
    background-size:auto, 54px 54px, 54px 54px;
    background-position:center top, center, center;
  }}
  body::before {{
    content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
    background:radial-gradient(90rem 50rem at 50% -20rem, transparent 40%, var(--bg) 85%);
  }}
  .wrap {{ position:relative; z-index:1; max-width:1000px; margin:0 auto; padding:0 1.25rem 5rem; }}

  /* hero */
  .hero {{ text-align:center; padding:3.5rem 0 2.5rem; }}
  .hero .banner {{
    width:100%; max-width:560px; height:auto; display:block; margin:0 auto 1.75rem;
    border-radius:16px; border:1px solid var(--line);
    box-shadow:0 0 0 1px rgba(255,255,255,.02), 0 30px 80px -30px var(--glow);
  }}
  .hero h1 {{
    font-size:clamp(2.4rem,7vw,3.6rem); font-weight:700; margin:0; letter-spacing:-.03em;
    background:linear-gradient(180deg,#fff,#aab4cc); -webkit-background-clip:text; background-clip:text; color:transparent;
  }}
  .motto {{ font-family:var(--mono); color:var(--accent2); font-size:1rem; margin:.9rem 0 0; }}
  .motto .cursor {{ display:inline-block; width:.6ch; background:var(--accent2); animation:blink 1.1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity:0; }} }}
  .cta-row {{ margin-top:1.6rem; display:flex; gap:.75rem; justify-content:center; flex-wrap:wrap; }}
  .btn {{
    font-family:var(--mono); font-size:.9rem; text-decoration:none; padding:.6rem 1.1rem; border-radius:10px;
    border:1px solid var(--line); color:var(--fg); transition:transform .15s, border-color .15s, box-shadow .15s;
  }}
  .btn:hover {{ transform:translateY(-2px); }}
  .btn.primary {{ background:linear-gradient(180deg,var(--accent2),var(--accent)); border-color:transparent; color:#06101f; font-weight:500; box-shadow:0 10px 30px -10px var(--glow); }}
  .btn.ghost:hover {{ border-color:var(--accent); box-shadow:0 10px 30px -14px var(--glow); }}

  /* stats */
  .stats {{ display:flex; gap:1rem; justify-content:center; flex-wrap:wrap; margin:2.25rem 0 .5rem; }}
  .stat {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:.9rem 1.4rem; min-width:7rem; }}
  .stat .n {{ font-family:var(--mono); font-size:1.7rem; font-weight:500; color:var(--accent2); }}
  .stat .l {{ font-size:.78rem; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; }}

  /* section headers */
  section {{ margin-top:3.5rem; }}
  .sec-head {{ display:flex; align-items:baseline; gap:.75rem; margin-bottom:1.25rem; }}
  .sec-head h2 {{ font-size:1.5rem; margin:0; letter-spacing:-.02em; }}
  .sec-head .tag {{ font-family:var(--mono); font-size:.78rem; color:var(--muted); }}

  /* course cards */
  .courses {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:1.1rem; }}
  .course {{
    position:relative; display:flex; flex-direction:column; text-decoration:none; color:inherit;
    background:linear-gradient(180deg,var(--card),#0b0e18); border:1px solid var(--line);
    border-radius:16px; padding:1.3rem 1.4rem; overflow:hidden; transition:transform .18s, border-color .18s, box-shadow .18s;
  }}
  .course::after {{
    content:""; position:absolute; inset:0; border-radius:16px; padding:1px; pointer-events:none; opacity:0;
    background:linear-gradient(130deg,var(--accent2),transparent 40%); transition:opacity .2s;
    -webkit-mask:linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); -webkit-mask-composite:xor; mask-composite:exclude;
  }}
  .course:hover {{ transform:translateY(-4px); border-color:transparent; box-shadow:0 24px 60px -24px var(--glow); }}
  .course:hover::after {{ opacity:1; }}
  .course-head {{ display:flex; justify-content:space-between; align-items:center; gap:.5rem; }}
  .course .code {{ font-family:var(--mono); font-weight:500; color:var(--accent2); letter-spacing:.02em; }}
  .course h3 {{ font-size:1.18rem; margin:.7rem 0 .4rem; letter-spacing:-.01em; }}
  .course .faculty {{ color:var(--muted); font-size:.9rem; margin:0 0 1.2rem; display:flex; align-items:center; gap:.5rem; }}
  .course .start {{ margin-top:auto; font-family:var(--mono); font-size:.88rem; color:var(--accent2); }}
  .course .arrow {{ transition:transform .18s; display:inline-block; }}
  .course:hover .arrow {{ transform:translateX(4px); }}
  .fchip {{ font-family:var(--mono); font-size:.68rem; font-weight:500; padding:.1rem .45rem; border-radius:6px; background:rgba(59,130,246,.12); color:var(--accent2); border:1px solid rgba(59,130,246,.25); }}

  /* pills */
  .pill {{ font-family:var(--mono); display:inline-block; padding:.12rem .5rem; border-radius:999px; font-size:.7rem; font-weight:500; white-space:nowrap; border:1px solid transparent; }}
  .pill.built {{ background:rgba(46,160,67,.14); color:#4ac26b; border-color:rgba(46,160,67,.3); }}
  .pill.progress {{ background:rgba(210,153,34,.14); color:var(--amber); border-color:rgba(210,153,34,.3); }}
  .pill.passed {{ background:rgba(46,160,67,.2); color:#4ac26b; }}
  .pill.planned {{ background:#141827; color:var(--muted); border-color:var(--line); }}

  /* roadmap */
  .roadmap-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:1rem; }}
  .faculty {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:1.1rem 1.2rem; }}
  .faculty-name {{ font-weight:600; display:flex; align-items:center; gap:.5rem; margin-bottom:.8rem; font-size:.98rem; }}
  .road {{ list-style:none; margin:0; padding:0; }}
  .road li {{ display:flex; gap:.6rem; align-items:baseline; padding:.35rem 0; border-top:1px solid var(--line); font-size:.9rem; }}
  .road li:first-child {{ border-top:none; }}
  .road .rcode {{ font-family:var(--mono); font-size:.78rem; color:var(--muted); min-width:4.6rem; }}
  .road .rtitle {{ color:#c4ccdc; }}

  /* transcript */
  .transcript-empty {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:1.4rem 1.5rem; }}
  .transcript-empty .mono {{ font-family:var(--mono); color:var(--accent2); font-size:.85rem; }}
  .transcript-empty p {{ color:var(--muted); margin:.6rem 0 0; }}
  .ledger {{ width:100%; border-collapse:collapse; background:var(--card); border:1px solid var(--line); border-radius:14px; overflow:hidden; }}
  .ledger th, .ledger td {{ text-align:left; padding:.7rem 1rem; border-bottom:1px solid var(--line); }}
  .ledger th {{ font-family:var(--mono); font-size:.72rem; text-transform:uppercase; letter-spacing:.06em; color:var(--muted); }}
  .ledger tr:last-child td {{ border-bottom:none; }}

  footer {{ margin-top:4rem; padding-top:1.5rem; border-top:1px solid var(--line); color:var(--muted); font-size:.85rem; text-align:center; }}
  footer a {{ color:var(--accent2); text-decoration:none; }}
  footer .mono {{ font-family:var(--mono); }}

  @media (prefers-reduced-motion:reduce) {{ * {{ animation:none !important; transition:none !important; }} }}
</style>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <img class="banner" src="gitoversity.png" alt="Gitoversity: an open university for offensive security">
    <h1>Gitoversity</h1>
    <p class="motto">&gt; learn by building, prove it by shipping<span class="cursor">&nbsp;</span></p>
    <div class="cta-row">
      <a class="btn primary" href="#open">Browse courses</a>
      <a class="btn ghost" href="{repo}">View on GitHub</a>
    </div>
    <div class="stats">
      <div class="stat"><div class="n">{available_count}</div><div class="l">Open now</div></div>
      <div class="stat"><div class="n">{faculty_count}</div><div class="l">Faculties</div></div>
      <div class="stat"><div class="n">{total_count}</div><div class="l">Courses</div></div>
    </div>
  </header>

  <section id="open">
    <div class="sec-head"><h2>Open now</h2><span class="tag">// ready to take</span></div>
    {available}
  </section>

  <section id="roadmap">
    <div class="sec-head"><h2>Roadmap</h2><span class="tag">// planned</span></div>
    {roadmap}
  </section>

  <section id="transcript">
    <div class="sec-head"><h2>Transcript</h2><span class="tag">// shipped &amp; passed</span></div>
    {transcript}
  </section>

  <footer>
    <p class="mono">authorized testing &amp; education only &middot; all labs run locally</p>
    <p>Generated from <a href="{repo}/blob/main/catalog/README.md">catalog</a> on {built}.
    Code MIT, content CC BY 4.0.</p>
  </footer>
</div>
</body>
</html>
"""


def main():
    faculties = parse_catalog(CATALOG.read_text(encoding="utf-8"))
    transcript = parse_transcript(TRANSCRIPT.read_text(encoding="utf-8"))
    total = sum(len(c) for _, c in faculties)
    available = sum(1 for _, c in faculties for _, _, s in c if s.strip().lower() != "planned")
    page = PAGE.format(
        repo=REPO,
        repo_raw=f"{REPO.replace('github.com', 'raw.githubusercontent.com')}/main/docs",
        available_count=available,
        faculty_count=len(faculties),
        total_count=total,
        available=render_available(faculties),
        roadmap=render_roadmap(faculties),
        transcript=render_transcript(transcript),
        built=date.today().isoformat(),
    )
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT} ({len(page)} bytes), {available} open / {total} total across {len(faculties)} faculties")


if __name__ == "__main__":
    main()
