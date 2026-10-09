"""Generate docs/index.html for GitHub Pages from the catalog and transcript.

Standard library only. Run from anywhere:  python3 docs/build.py
The landing page leads with the courses that are actually built ("Open now")
and shows everything still "planned" as a roadmap below.
"""
import html
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
        _, fname = split_faculty(faculty)
        for code, title, status in courses:
            if status.strip().lower() == "planned":
                continue
            cards.append(f"""      <a class="course" href="{REPO}/tree/main/{esc(code)}">
        <div class="course-head"><span class="code">{esc(code)}</span>{pill(status)}</div>
        <h3>{esc(title)}</h3>
        <p class="faculty">{esc(fname)}</p>
        <span class="start">Start the course<span class="arrow"> &rarr;</span></span>
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
<link rel="icon" href="logo-mark.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg:#0b0d12; --fg:#e9edf4; --muted:#8b93a4; --card:#12151d; --line:#232833;
    --accent:#4f8cff; --accent-soft:rgba(79,140,255,.12);
    --green:#48b968; --mono:'JetBrains Mono',ui-monospace,monospace; --sans:'Space Grotesk',system-ui,sans-serif;
  }}
  * {{ box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{ margin:0; background:var(--bg); color:var(--fg); font-family:var(--sans); line-height:1.65; -webkit-font-smoothing:antialiased; }}
  a {{ color:var(--accent); text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  .wrap {{ max-width:940px; margin:0 auto; padding:0 1.5rem 5rem; }}

  header.hero {{ padding:4rem 0 2.5rem; border-bottom:1px solid var(--line); text-align:center; }}
  .brand {{ display:flex; align-items:center; justify-content:center; gap:.9rem; }}
  .brand img {{ width:56px; height:56px; object-fit:contain; }}
  .brand .word {{ font-size:2rem; font-weight:700; letter-spacing:-.02em; }}
  .lede {{ font-size:1.25rem; color:var(--muted); max-width:34rem; margin:1.4rem auto 0; line-height:1.5; }}
  .lede strong {{ color:var(--fg); font-weight:600; }}
  .cta-row {{ margin-top:1.8rem; display:flex; gap:.7rem; flex-wrap:wrap; justify-content:center; }}
  .btn {{ font-size:.95rem; padding:.6rem 1.2rem; border-radius:8px; border:1px solid var(--line); color:var(--fg); }}
  .btn:hover {{ text-decoration:none; }}
  .btn.primary {{ background:var(--accent); border-color:var(--accent); color:#fff; font-weight:500; }}
  .btn.primary:hover {{ background:#3f7af0; }}
  .btn.ghost:hover {{ border-color:var(--muted); }}
  .meta {{ margin-top:1.8rem; display:flex; gap:2rem; flex-wrap:wrap; justify-content:center; font-size:.9rem; color:var(--muted); }}
  .meta b {{ color:var(--fg); font-family:var(--mono); font-weight:500; }}

  section {{ margin-top:3.25rem; }}
  .sec-head {{ display:flex; align-items:baseline; justify-content:space-between; margin-bottom:1.1rem; }}
  .sec-head h2 {{ font-size:1.35rem; margin:0; letter-spacing:-.01em; }}
  .sec-head .tag {{ font-family:var(--mono); font-size:.8rem; color:var(--muted); }}

  .courses {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(290px,1fr)); gap:1rem; }}
  .course {{ display:flex; flex-direction:column; color:inherit; background:var(--card); border:1px solid var(--line); border-radius:12px; padding:1.35rem 1.4rem; transition:border-color .15s; }}
  .course:hover {{ border-color:var(--accent); text-decoration:none; }}
  .course-head {{ display:flex; justify-content:space-between; align-items:center; }}
  .course .code {{ font-family:var(--mono); font-size:.9rem; color:var(--accent); }}
  .course h3 {{ font-size:1.12rem; margin:.65rem 0 .3rem; letter-spacing:-.01em; color:var(--fg); }}
  .course .faculty {{ color:var(--muted); font-size:.9rem; margin:0 0 1.15rem; }}
  .course .start {{ margin-top:auto; font-size:.9rem; color:var(--accent); }}
  .course:hover .arrow {{ margin-left:.25rem; }}
  .arrow {{ transition:margin-left .15s; }}

  .pill {{ font-family:var(--mono); font-size:.72rem; padding:.12rem .55rem; border-radius:999px; white-space:nowrap; }}
  .pill.built {{ background:rgba(72,185,104,.14); color:var(--green); }}
  .pill.progress {{ background:rgba(210,153,34,.14); color:#d6a132; }}
  .pill.passed {{ background:rgba(72,185,104,.2); color:var(--green); }}
  .pill.planned {{ background:#1a1e28; color:var(--muted); }}

  .roadmap-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:1rem; }}
  .faculty {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:1.1rem 1.25rem; }}
  .faculty-name {{ font-weight:600; margin-bottom:.7rem; font-size:.95rem; display:flex; align-items:center; gap:.5rem; }}
  .fchip {{ font-family:var(--mono); font-size:.68rem; padding:.1rem .45rem; border-radius:5px; background:var(--accent-soft); color:var(--accent); }}
  .road {{ list-style:none; margin:0; padding:0; }}
  .road li {{ display:flex; gap:.7rem; align-items:baseline; padding:.4rem 0; border-top:1px solid var(--line); font-size:.9rem; }}
  .road li:first-child {{ border-top:none; }}
  .road .rcode {{ font-family:var(--mono); font-size:.72rem; font-weight:500; letter-spacing:.03em; color:var(--accent); background:var(--accent-soft); padding:.12rem .45rem; border-radius:5px; min-width:4.8rem; text-align:center; }}
  .road .rtitle {{ color:#c6cdda; }}

  .transcript-empty {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:1.3rem 1.4rem; }}
  .transcript-empty .mono {{ font-family:var(--mono); color:var(--accent); font-size:.85rem; }}
  .transcript-empty p {{ color:var(--muted); margin:.5rem 0 0; }}
  .ledger {{ width:100%; border-collapse:collapse; background:var(--card); border:1px solid var(--line); border-radius:12px; overflow:hidden; }}
  .ledger th, .ledger td {{ text-align:left; padding:.65rem 1rem; border-bottom:1px solid var(--line); font-size:.92rem; }}
  .ledger th {{ font-family:var(--mono); font-size:.72rem; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); }}
  .ledger tr:last-child td {{ border-bottom:none; }}

  footer {{ margin-top:4rem; padding-top:1.5rem; border-top:1px solid var(--line); color:var(--muted); font-size:.85rem; }}
  footer .mono {{ font-family:var(--mono); }}
  @media (max-width:560px) {{ header.hero {{ padding:2.5rem 0 2rem; }} .brand .word {{ font-size:1.7rem; }} }}
</style>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <div class="brand">
      <img src="logo-mark.png" alt="Gitoversity logo">
      <span class="word">Gitoversity</span>
    </div>
    <p class="lede">An open university for offensive security. <strong>Learn by building, prove it by shipping.</strong></p>
    <div class="cta-row">
      <a class="btn primary" href="#open">Browse courses</a>
      <a class="btn ghost" href="{repo}">View on GitHub</a>
    </div>
    <div class="meta">
      <span><b>{available_count}</b> open now</span>
      <span><b>{faculty_count}</b> faculties</span>
      <span><b>{total_count}</b> courses mapped</span>
    </div>
  </header>

  <section id="open">
    <div class="sec-head"><h2>Open now</h2><span class="tag">ready to take</span></div>
    {available}
  </section>

  <section id="roadmap">
    <div class="sec-head"><h2>Roadmap</h2></div>
    {roadmap}
  </section>

  <section id="transcript">
    <div class="sec-head"><h2>Transcript</h2><span class="tag">shipped &amp; passed</span></div>
    {transcript}
  </section>

  <footer>
    <p class="mono">authorized testing &amp; education only &middot; all labs run locally</p>
    <p>Generated from the <a href="{repo}/blob/main/catalog/README.md">catalog</a> on {built}. Code MIT, content CC BY 4.0.</p>
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
