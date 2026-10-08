"""Generate docs/index.html for GitHub Pages from the catalog and transcript.

Standard library only. Run from anywhere:  python3 docs/build.py
Not a general markdown engine: it handles exactly the headings, paragraphs and
pipe tables that catalog/README.md and catalog/TRANSCRIPT.md use.
"""
import html
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog" / "README.md"
TRANSCRIPT = ROOT / "catalog" / "TRANSCRIPT.md"
OUT = ROOT / "docs" / "index.html"

STATUS_CLASS = {
    "passed": "passed",
    "built, awaiting pass": "built",
    "in progress": "progress",
    "planned": "planned",
}


def status_badge(text):
    cls = STATUS_CLASS.get(text.strip().lower(), "planned")
    return f'<span class="badge {cls}">{html.escape(text.strip())}</span>'


def render_cell(text):
    """Escape a table cell, turn [label](url) into a link, badge status words."""
    text = text.strip()
    if text.lower() in STATUS_CLASS:
        return status_badge(text)
    link = re.fullmatch(r"\[(.+?)\]\((.+?)\)", text)
    if link:
        return f'<a href="{html.escape(link.group(2))}">{html.escape(link.group(1))}</a>'
    return html.escape(text)


def split_row(line):
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def md_to_html(md):
    """Convert the limited markdown subset to HTML body fragments."""
    out, i = [], 0
    lines = md.splitlines()
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("# "):
            out.append(f"<h1>{html.escape(line[2:].strip())}</h1>")
        elif line.startswith("## "):
            out.append(f"<h2>{html.escape(line[3:].strip())}</h2>")
        elif line.startswith("|"):
            header = split_row(line)
            i += 1  # skip the |---|---| separator row
            rows = []
            while i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
                i += 1
                cells = split_row(lines[i])
                if cells and not all(set(c) <= {"-", ":"} for c in cells):
                    rows.append(cells)
            thead = "".join(f"<th>{html.escape(h)}</th>" for h in header)
            body = ""
            for r in rows:
                if not any(r):
                    continue
                body += "<tr>" + "".join(f"<td>{render_cell(c)}</td>" for c in r) + "</tr>"
            out.append(f"<table><thead><tr>{thead}</tr></thead><tbody>{body}</tbody></table>")
        else:
            out.append(f"<p>{html.escape(line.strip())}</p>")
        i += 1
    return "\n".join(out)


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
  .wrap {{ max-width:860px; margin:0 auto; padding:2.5rem 1.25rem 4rem; }}
  header.hero {{ text-align:center; padding:1rem 0 2rem; border-bottom:1px solid var(--line); margin-bottom:2rem; }}
  .hero h1 {{ font-size:2.6rem; margin:0; letter-spacing:-.02em; }}
  .hero p {{ color:var(--muted); font-size:1.15rem; margin:.5rem 0 0; }}
  h1 {{ font-size:1.9rem; }}
  h2 {{ font-size:1.25rem; margin-top:2.25rem; border-bottom:1px solid var(--line); padding-bottom:.35rem; }}
  a {{ color:var(--accent); text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  table {{ width:100%; border-collapse:collapse; margin:1rem 0; background:var(--card); border:1px solid var(--line); border-radius:8px; overflow:hidden; }}
  th, td {{ text-align:left; padding:.6rem .8rem; border-bottom:1px solid var(--line); }}
  th {{ background:#1c2333; font-size:.85rem; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); }}
  tr:last-child td {{ border-bottom:none; }}
  .badge {{ display:inline-block; padding:.15rem .55rem; border-radius:999px; font-size:.78rem; font-weight:600; white-space:nowrap; }}
  .badge.passed {{ background:#1a7f37; color:#fff; }}
  .badge.built {{ background:#1f6feb; color:#fff; }}
  .badge.progress {{ background:#9e6a03; color:#fff; }}
  .badge.planned {{ background:#30363d; color:var(--muted); }}
  .repo-link {{ text-align:center; margin-top:.75rem; }}
  footer {{ margin-top:3rem; padding-top:1.5rem; border-top:1px solid var(--line); color:var(--muted); font-size:.9rem; text-align:center; }}
  @media (max-width:520px) {{ .hero h1 {{ font-size:2rem; }} th, td {{ padding:.5rem .55rem; }} }}
</style>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <h1>Gitoversity</h1>
    <p>An open university for offensive security.<br>Learn by building, prove it by shipping.</p>
    <div class="repo-link"><a href="https://github.com/orgito1015/Gitoversity">View the repository on GitHub</a></div>
  </header>

  <section>{catalog}</section>
  <section>{transcript}</section>

  <footer>
    For authorized testing and education only. Labs run locally.<br>
    Generated from <code>catalog/README.md</code> and <code>catalog/TRANSCRIPT.md</code> on {built}.
  </footer>
</div>
</body>
</html>
"""


def main():
    page = PAGE.format(
        catalog=md_to_html(CATALOG.read_text(encoding="utf-8")),
        transcript=md_to_html(TRANSCRIPT.read_text(encoding="utf-8")),
        built=date.today().isoformat(),
    )
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT} ({len(page)} bytes)")


if __name__ == "__main__":
    main()
