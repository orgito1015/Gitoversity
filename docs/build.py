"""Generate docs/index.html for GitHub Pages from the catalog and transcript.

Standard library only. Run from anywhere:  python3 docs/build.py
The landing page leads with the courses that are actually built ("Available
now") and shows everything still "planned" as a roadmap below.
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


def esc(s):
    return html.escape(s.strip())


def badge(status):
    cls = STATUS_CLASS.get(status.strip().lower(), "planned")
    return f'<span class="badge {cls}">{esc(status)}</span>'


def parse_catalog(md):
    """Return [(faculty_name, [(code, title, status), ...]), ...]."""
    faculties, current = [], None
    rows = iter(md.splitlines())
    for line in rows:
        line = line.rstrip()
        if line.startswith("## "):
            current = (line[3:].strip(), [])
            faculties.append(current)
        elif line.startswith("|") and current is not None:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3 and cells[0].lower() != "course" and not set(cells[0]) <= {"-", ":"}:
                if cells[0]:
                    current[1].append((cells[0], cells[1], cells[2]))
    return [f for f in faculties if f[1]]


def md_to_html(md):
    """Minimal markdown for the transcript: headings, paragraphs, pipe tables."""
    out, lines, i = [], md.splitlines(), 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("# "):
            out.append(f"<h2>{esc(line[2:])}</h2>")
        elif line.startswith("|"):
            header = [c.strip() for c in line.strip("|").split("|")]
            body = ""
            while i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
                i += 1
                cells = [c.strip() for c in lines[i].strip("|").split("|")]
                if any(cells) and not all(set(c) <= {"-", ":"} for c in cells):
                    body += "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in cells) + "</tr>"
            thead = "".join(f"<th>{esc(h)}</th>" for h in header)
            out.append(f"<table><thead><tr>{thead}</tr></thead><tbody>{body}</tbody></table>")
        else:
            out.append(f"<p>{esc(line)}</p>")
        i += 1
    return "\n".join(out)


def render_available(faculties):
    cards = []
    for faculty, courses in faculties:
        for code, title, status in courses:
            if status.strip().lower() == "planned":
                continue
            cards.append(f"""      <article class="card">
        <div class="card-top"><span class="code">{esc(code)}</span>{badge(status)}</div>
        <h3>{esc(title)}</h3>
        <p class="faculty">{esc(faculty)}</p>
        <a class="cta" href="{REPO}/tree/main/{esc(code)}">Start the course &rarr;</a>
      </article>""")
    if not cards:
        return '<p class="empty">No courses are open yet. Check the roadmap below.</p>'
    return '<div class="cards">\n' + "\n".join(cards) + "\n    </div>"


def render_roadmap(faculties):
    blocks = []
    for faculty, courses in faculties:
        remaining = [(c, t, s) for c, t, s in courses if s.strip().lower() == "planned"]
        if not remaining:
            continue
        rows = "".join(
            f"<tr><td>{esc(c)}</td><td>{esc(t)}</td><td>{badge(s)}</td></tr>" for c, t, s in remaining
        )
        blocks.append(
            f"<h3>{esc(faculty)}</h3><table><tbody>{rows}</tbody></table>"
        )
    return "\n".join(blocks)


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gitoversity</title>
<meta name="description" content="An open university for offensive security. Learn by building, prove it by shipping.">
<style>
  :root {{ color-scheme: dark; --bg:#0d1117; --fg:#e6edf3; --muted:#8b949e; --card:#161b22; --line:#30363d; --accent:#58a6ff; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg); font:16px/1.6 system-ui, sans-serif; }}
  .wrap {{ max-width:900px; margin:0 auto; padding:2.5rem 1.25rem 4rem; }}
  header.hero {{ text-align:center; padding:1rem 0 2rem; border-bottom:1px solid var(--line); margin-bottom:2.5rem; }}
  .hero .banner {{ width:100%; max-width:640px; height:auto; border-radius:12px; border:1px solid var(--line); display:block; margin:0 auto 1.25rem; }}
  .hero h1 {{ font-size:2.6rem; margin:0; letter-spacing:-.02em; }}
  .hero p {{ color:var(--muted); font-size:1.15rem; margin:.5rem 0 0; }}
  .repo-link {{ margin-top:.75rem; }}
  h2 {{ font-size:1.35rem; margin:2.75rem 0 1rem; }}
  h2 .count {{ color:var(--muted); font-weight:400; font-size:1rem; }}
  h3 {{ font-size:1rem; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; margin:1.5rem 0 .5rem; }}
  a {{ color:var(--accent); text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  .cards {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:1rem; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:1.1rem 1.2rem; display:flex; flex-direction:column; }}
  .card-top {{ display:flex; justify-content:space-between; align-items:center; gap:.5rem; }}
  .card .code {{ font-family:ui-monospace, monospace; font-weight:700; color:var(--accent); }}
  .card h3 {{ color:var(--fg); text-transform:none; letter-spacing:0; font-size:1.1rem; margin:.6rem 0 .25rem; }}
  .card .faculty {{ color:var(--muted); margin:0 0 1rem; font-size:.9rem; }}
  .card .cta {{ margin-top:auto; font-weight:600; }}
  .empty {{ color:var(--muted); }}
  table {{ width:100%; border-collapse:collapse; margin:.25rem 0 1rem; background:var(--card); border:1px solid var(--line); border-radius:8px; overflow:hidden; }}
  th, td {{ text-align:left; padding:.55rem .8rem; border-bottom:1px solid var(--line); }}
  th {{ background:#1c2333; font-size:.8rem; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); }}
  tr:last-child td {{ border-bottom:none; }}
  .roadmap table td:first-child {{ font-family:ui-monospace, monospace; color:var(--muted); white-space:nowrap; }}
  .badge {{ display:inline-block; padding:.15rem .55rem; border-radius:999px; font-size:.75rem; font-weight:600; white-space:nowrap; }}
  .badge.passed {{ background:#1a7f37; color:#fff; }}
  .badge.built {{ background:#1f6feb; color:#fff; }}
  .badge.progress {{ background:#9e6a03; color:#fff; }}
  .badge.planned {{ background:#30363d; color:var(--muted); }}
  footer {{ margin-top:3rem; padding-top:1.5rem; border-top:1px solid var(--line); color:var(--muted); font-size:.9rem; text-align:center; }}
  @media (max-width:520px) {{ .hero h1 {{ font-size:2rem; }} }}
</style>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <img class="banner" src="gitoversity.png" alt="Gitoversity: an open university for offensive security">
    <h1>Gitoversity</h1>
    <p>Learn by building, prove it by shipping.</p>
    <div class="repo-link"><a href="{repo}">View the repository on GitHub</a></div>
  </header>

  <section>
    <h2>Available now <span class="count">&middot; {available_count}</span></h2>
    {available}
  </section>

  <section class="roadmap">
    <h2>Roadmap <span class="count">&middot; planned courses</span></h2>
    {roadmap}
  </section>

  <section>
    {transcript}
  </section>

  <footer>
    For authorized testing and education only. Labs run locally.<br>
    Generated from <code>catalog/README.md</code> and <code>catalog/TRANSCRIPT.md</code> on {built}.
  </footer>
</div>
</body>
</html>
"""


def main():
    faculties = parse_catalog(CATALOG.read_text(encoding="utf-8"))
    available_count = sum(
        1 for _, courses in faculties for _, _, s in courses if s.strip().lower() != "planned"
    )
    page = PAGE.format(
        repo=REPO,
        available_count=available_count,
        available=render_available(faculties),
        roadmap=render_roadmap(faculties),
        transcript=md_to_html(TRANSCRIPT.read_text(encoding="utf-8")),
        built=date.today().isoformat(),
    )
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT} ({len(page)} bytes), {available_count} available course(s)")


if __name__ == "__main__":
    main()
