#!/usr/bin/env python3
"""
Reusable weekly page generator for the Math Challenge.

Each week lives in   weeks/grade4/weekN/   with:
  - week.json                  ← the week's definition (label, due, problems[])
  - source_images/*.png        ← any problem images referenced by week.json
The generator embeds the images as base64 and writes  grade4_weekN.html.
It also rebuilds the week cards on the site's home page (index.html).

Usage:
  python3 build_week.py weeks/grade4/week3     # build that week, then refresh index
  python3 build_week.py --all                  # rebuild every week + index
  python3 build_week.py --index                # only rebuild index.html

week.json shape:
{
  "number": 3,
  "week_label": "Grade 4 — Week 3",     // MUST match the AnswerKey tab's Week cell
  "due": "Sunday night",
  "problems": [
    { "type": "number", "text": "....", "unit": "squares" },
    { "type": "text",   "text": "....", "label": "Triangle digit:", "image": "p3.png" },
    { "type": "choice", "text": "....", "image": "p2.png", "choices": ["A","B","C","D","E"] }
  ]
}
Problem types: "number"/"text" → free-text box; "choice" → A–E radio chips.
"image" is optional on any problem.
"""
import base64, json, pathlib, sys, html as _html

ENDPOINT_URL = "https://script.google.com/macros/s/AKfycbx5Xl-3-NRx5vnqZVKx4_7XiJI1iKR4Wiit8beSmlm15rJX-Fs7LBZrkk6IFseDSFK3Jw/exec"
ACCENTS = ["#4f46e5", "#0891b2", "#7c3aed"]          # per-problem left border / accents
WEEK_COLORS = ["#4f46e5", "#0891b2", "#7c3aed", "#db2777", "#ea580c", "#16a34a", "#0284c7", "#9333ea"]
EMOJI = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣"]

GRADE_DIR = pathlib.Path(__file__).parent
REPO_ROOT = GRADE_DIR.parent.parent
INDEX = REPO_ROOT / "index.html"


def b64_img(week_dir, name):
    data = (week_dir / "source_images" / name).read_bytes()
    return "data:image/png;base64," + base64.b64encode(data).decode()


def esc(s):
    return _html.escape(str(s), quote=True)


# ── CSS (kept in sync with the look of week1/week2) ──────────────────────────
def css():
    accent_nth = "\n".join(
        f".problem:nth-child({i+1}) {{ border-left-color: {c}; }}\n"
        f".problem:nth-child({i+1}) .problem-num {{ color: {c}; }}\n"
        f".problem:nth-child({i+1}) .choice input:checked + span {{ background: {c}; border-color: {c}; }}"
        for i, c in enumerate(ACCENTS)
    )
    return f"""* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Segoe UI', system-ui, Arial, sans-serif; background: #f0f4ff; padding: 24px 16px 48px; color: #1e293b; }}
.page {{ max-width: 860px; margin: 0 auto; }}

.topnav {{ display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }}
.topnav a {{ display: inline-flex; align-items: center; gap: 6px; text-decoration: none; color: #4f46e5; font-weight: 700; font-size: 15px; padding: 8px 16px; background: #fff; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,.06); transition: transform .15s, box-shadow .15s; }}
.topnav a:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.1); }}
.topnav a.lb {{ color: #b45309; }}

.header {{ background: linear-gradient(135deg, #1d4ed8, #4f46e5); color: white; border-radius: 16px; padding: 28px 36px; margin-bottom: 28px; box-shadow: 0 6px 24px rgba(30,64,175,.3); }}
.header h1 {{ font-size: 32px; font-weight: 900; letter-spacing: -.5px; }}
.header .sub {{ font-size: 16px; opacity: .85; margin-top: 6px; }}
.header .week-info {{ display: flex; gap: 24px; margin-top: 14px; font-size: 14px; opacity: .9; }}
.header .week-info span {{ background: rgba(255,255,255,.18); border-radius: 8px; padding: 4px 12px; }}

.name-box {{ background: white; border-radius: 12px; padding: 18px 24px; margin-bottom: 24px; box-shadow: 0 2px 10px rgba(0,0,0,.08); display: flex; align-items: center; gap: 16px; }}
.name-box label {{ font-weight: 700; font-size: 16px; white-space: nowrap; }}
.name-box input {{ flex: 1; border: 2px solid #c7d2fe; border-radius: 8px; padding: 10px 14px; font-size: 16px; outline: none; transition: border-color .2s; }}
.name-box input:focus {{ border-color: #4f46e5; }}

.problem {{ background: white; border-radius: 16px; padding: 28px 32px; margin-bottom: 24px; box-shadow: 0 2px 12px rgba(0,0,0,.08); border-left: 6px solid #4f46e5; }}
{accent_nth}
.problem-num {{ font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; color: #4f46e5; margin-bottom: 10px; }}
.problem-text {{ font-size: 17px; line-height: 1.5; margin: 6px 0 4px; }}
.problem img {{ max-width: 100%; border-radius: 8px; margin: 16px 0; border: 1px solid #e2e8f0; }}

.answer-area {{ margin-top: 18px; display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }}
.answer-label {{ font-weight: 700; font-size: 16px; }}
.answer-area input[type=text] {{ width: 120px; border: 2.5px solid #c7d2fe; border-radius: 8px; padding: 10px 14px; font-size: 18px; font-weight: 700; text-align: center; outline: none; transition: border-color .2s; }}
.answer-area input[type=text]:focus {{ border-color: #4f46e5; }}
.unit {{ font-size: 14px; color: #64748b; }}

.choices {{ gap: 12px; }}
.choice {{ display: inline-flex; cursor: pointer; }}
.choice input {{ position: absolute; opacity: 0; width: 0; height: 0; }}
.choice span {{ display: inline-flex; align-items: center; justify-content: center; width: 46px; height: 46px; border-radius: 50%; border: 2.5px solid #c7d2fe; font-size: 19px; font-weight: 800; color: #475569; user-select: none; transition: background .15s, border-color .15s, color .15s, box-shadow .15s; }}
.choice:hover span {{ border-color: #94a3b8; }}
.choice input:checked + span {{ background: #4f46e5; border-color: #4f46e5; color: #fff; box-shadow: 0 3px 10px rgba(79,70,229,.4); }}
.choice input:focus-visible + span {{ outline: 2px solid #4f46e5; outline-offset: 2px; }}

.visibility-box {{ background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 12px; padding: 14px 20px; margin-bottom: 24px; font-size: 15px; }}
.visibility-box .vq {{ font-weight: 700; margin-bottom: 8px; display: block; }}
.visibility-box label {{ display: inline-flex; align-items: center; gap: 7px; margin-right: 22px; cursor: pointer; }}
.visibility-box .hint {{ display: block; margin-top: 6px; font-size: 13px; color: #64748b; }}

.submit-row {{ text-align: center; margin-top: 8px; }}
.btn-submit {{ background: linear-gradient(135deg, #1d4ed8, #4f46e5); color: white; border: none; border-radius: 12px; padding: 16px 48px; font-size: 18px; font-weight: 800; cursor: pointer; box-shadow: 0 4px 16px rgba(79,70,229,.4); transition: transform .15s, box-shadow .15s; }}
.btn-submit:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(79,70,229,.5); }}
.btn-submit:active {{ transform: translateY(0); }}
.btn-submit:disabled {{ opacity: .6; cursor: default; transform: none; box-shadow: none; }}

.print-btn {{ background: rgba(255,255,255,.16); border: 1.5px solid rgba(255,255,255,.65); border-radius: 8px; padding: 8px 18px; font-size: 14px; font-weight: 600; color: #fff; cursor: pointer; float: right; margin-top: 4px; transition: background .2s, border-color .2s; }}
.print-btn:hover {{ background: rgba(255,255,255,.30); border-color: #fff; }}

@media print {{
  @page {{ size: A4 portrait; margin: 12mm 14mm; }}
  html, body {{ background: white !important; padding: 0 !important; margin: 0 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  .page {{ max-width: 100%; margin: 0; }}
  input::placeholder {{ color: transparent !important; opacity: 0 !important; }}
  input::-webkit-input-placeholder {{ color: transparent !important; opacity: 0 !important; }}
  .topnav {{ display: none !important; }}
  .header {{ background: none !important; color: black !important; border-radius: 0 !important; box-shadow: none !important; padding: 0 0 7pt 0 !important; margin-bottom: 12pt !important; border-bottom: 2.5pt solid #1d4ed8; }}
  .header h1 {{ font-size: 19pt !important; letter-spacing: 0 !important; color: #1d4ed8 !important; }}
  .header .sub {{ font-size: 10.5pt !important; margin-top: 2pt !important; opacity: 1 !important; color: #333 !important; }}
  .header .week-info {{ display: flex !important; margin-top: 5pt !important; font-size: 10pt !important; gap: 18pt !important; opacity: 1 !important; color: #333 !important; }}
  .header .week-info span {{ background: none !important; padding: 0 !important; border-radius: 0 !important; }}
  .print-btn {{ display: none !important; }}
  .name-box {{ background: none !important; box-shadow: none !important; border-radius: 0 !important; border: none !important; padding: 0 !important; margin-bottom: 12pt !important; display: flex; align-items: baseline; gap: 8pt; }}
  .name-box label {{ font-size: 11pt !important; font-weight: 700 !important; white-space: nowrap; }}
  .name-box input {{ flex: 1; border: none !important; border-bottom: 1pt solid #444 !important; border-radius: 0 !important; font-size: 11pt !important; background: none !important; padding: 1pt 4pt !important; }}
  #quiz {{ display: block; }}
  .problem {{ background: none !important; box-shadow: none !important; border-radius: 0 !important; padding: 0 0 0 9pt !important; margin: 0 0 16pt 0 !important; border-left-width: 3.5pt !important; page-break-inside: avoid; break-inside: avoid; }}
  .problem:last-of-type {{ margin-bottom: 0 !important; }}
  .problem-num {{ font-size: 10pt !important; margin-bottom: 4pt !important; }}
  .problem-text {{ font-size: 11pt !important; line-height: 1.35 !important; margin: 2pt 0 4pt !important; }}
  .problem img {{ width: auto !important; max-width: 100% !important; max-height: 230pt !important; height: auto !important; margin: 4pt 0 6pt !important; border: none !important; display: block; }}
  .answer-area {{ margin-top: 6pt !important; gap: 12pt !important; }}
  .answer-label {{ font-size: 11pt !important; }}
  .answer-area input[type=text] {{ border: none !important; border-bottom: 1.5pt solid #333 !important; border-radius: 0 !important; font-size: 12pt !important; width: 90px !important; background: none !important; padding: 1pt 2pt !important; }}
  .unit {{ font-size: 10.5pt !important; }}
  .choices {{ gap: 14pt !important; }}
  .choice span {{ width: 22pt !important; height: 22pt !important; border: 1.25pt solid #333 !important; background: none !important; color: #000 !important; font-size: 12pt !important; box-shadow: none !important; }}
  .choice input:checked + span {{ background: none !important; color: #000 !important; border-color: #000 !important; }}
  .visibility-box {{ display: none !important; }}
  .submit-row {{ display: none !important; }}
}}"""


def render_problem(i, p, week_dir):
    n = i + 1
    parts = [f'    <div class="problem">', f'      <div class="problem-num">Problem {n}</div>']
    if p.get("text"):
        parts.append(f'      <p class="problem-text">{esc(p["text"])}</p>')
    if p.get("image"):
        parts.append(f'      <img src="{b64_img(week_dir, p["image"])}" alt="Problem {n} figure">')

    ptype = p.get("type", "number")
    if ptype == "choice":
        choices = p.get("choices", ["A", "B", "C", "D", "E"])
        chips = "\n".join(
            f'        <label class="choice"><input type="radio" name="a{n}" value="{esc(c)}"><span>{esc(c)}</span></label>'
            for c in choices
        )
        parts.append('      <div class="answer-area choices">')
        parts.append('        <span class="answer-label">My answer:</span>')
        parts.append(chips)
        parts.append('      </div>')
    else:
        label = p.get("label", "My answer:")
        unit = f'\n        <span class="unit">{esc(p["unit"])}</span>' if p.get("unit") else ""
        ml = p.get("maxlength", 6)
        parts.append('      <div class="answer-area">')
        parts.append(f'        <span class="answer-label">{esc(label)}</span>')
        parts.append(f'        <input type="text" id="a{n}" name="a{n}" placeholder="?" maxlength="{ml}" autocomplete="off">{unit}')
        parts.append('      </div>')

    parts.append('    </div>')
    return "\n".join(parts)


def render_week(week_dir, cfg):
    problems = cfg["problems"]
    num = len(problems)
    title = cfg.get("title", cfg["week_label"])
    due = cfg.get("due", "Sunday night")
    problems_html = "\n\n".join(render_problem(i, p, week_dir) for i, p in enumerate(problems))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<style>
{css()}
</style>
</head>
<body>
<div class="page">

  <div class="topnav">
    <a href="../../../index.html">← Home</a>
    <a class="lb" href="../leaderboard.html">\U0001f3c6 Leaderboard</a>
  </div>

  <div class="header">
    <button class="print-btn" onclick="window.print()">\U0001f5a8 Print</button>
    <h1>{esc(title)}</h1>
    <div class="sub">Math Challenge Problems</div>
    <div class="week-info">
      <span>\U0001f4c5 Due: {esc(due)}</span>
      <span>\U0001f3c6 {num} problems · 1 point each</span>
    </div>
  </div>

  <div class="name-box">
    <label for="sname">Your name:</label>
    <input type="text" id="sname" placeholder="First name Last initial" autocomplete="off">
  </div>

  <form id="quiz">

{problems_html}

    <div class="visibility-box">
      <span class="vq">Show my name on the class leaderboard?</span>
      <label><input type="radio" name="display" value="Private" checked> No, keep me private</label>
      <label><input type="radio" name="display" value="Public"> Yes, show my name</label>
      <span class="hint">Private keeps your name hidden from classmates — you can still look up your own
        rank on the leaderboard using your name.</span>
    </div>

    <div class="submit-row">
      <button type="button" class="btn-submit" onclick="submitAnswers(this)">Submit Answers ✓</button>
    </div>

  </form>

</div>

<script>
const ENDPOINT_URL = "{ENDPOINT_URL}";
const WEEK_LABEL = "{esc(cfg['week_label'])}";
const NUM_PROBLEMS = {num};

async function submitAnswers(btn) {{
  const name = document.getElementById('sname').value.trim();
  if (!name) {{ alert('Please enter your name first!'); return; }}

  const answers = {{}};
  for (let i = 1; i <= NUM_PROBLEMS; i++) {{
    const radio = document.querySelector('input[name="a' + i + '"]:checked');
    if (radio) {{ answers['a' + i] = radio.value; continue; }}
    const box = document.getElementById('a' + i);
    answers['a' + i] = box ? box.value.trim() : '';
  }}
  for (let i = 1; i <= NUM_PROBLEMS; i++) {{
    if (!answers['a' + i]) {{ alert('Please answer all ' + NUM_PROBLEMS + ' problems before submitting.'); return; }}
  }}

  const display = (document.querySelector('input[name="display"]:checked') || {{}}).value || 'Private';
  const payload = Object.assign({{ week: WEEK_LABEL, name: name, display: display }}, answers);

  if (!ENDPOINT_URL) {{
    alert('Thanks ' + name + '! Your answers have been recorded.\\n\\n(No Sheet connected yet.)');
    return;
  }}

  const original = btn.textContent;
  btn.disabled = true; btn.textContent = 'Submitting…';
  try {{
    const res = await fetch(ENDPOINT_URL, {{ method: 'POST', headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }}, body: JSON.stringify(payload) }});
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Save failed');
    alert('Thanks ' + name + '! Your answers have been recorded. ✓');
  }} catch (e) {{
    alert('Sorry — something went wrong saving your answers.\\nPlease tell your teacher.\\n\\n(' + e.message + ')');
  }} finally {{
    btn.disabled = false; btn.textContent = original;
  }}
}}
</script>
</body>
</html>
"""


def build_week(week_dir):
    week_dir = pathlib.Path(week_dir).resolve()
    cfg = json.loads((week_dir / "week.json").read_text())
    if not cfg.get("problems"):
        print(f"  (skip {week_dir.name}: metadata only, no problems[])")
        return cfg
    n = cfg.get("number") or int("".join(filter(str.isdigit, week_dir.name)))
    out = week_dir / f"grade4_week{n}.html"
    out.write_text(render_week(week_dir, cfg))
    try:
        shown = out.relative_to(REPO_ROOT)
    except ValueError:
        shown = out
    print(f"  built {shown} ({len(cfg['problems'])} problems)")
    return cfg


def all_weeks():
    dirs = sorted([d for d in GRADE_DIR.glob("week*") if (d / "week.json").exists()],
                  key=lambda d: int("".join(filter(str.isdigit, d.name)) or 0))
    return dirs


def rebuild_index():
    cards = []
    for d in all_weeks():
        cfg = json.loads((d / "week.json").read_text())
        n = cfg.get("number") or int("".join(filter(str.isdigit, d.name)))
        html_name = cfg.get("html", f"grade4_week{n}.html")
        nprob = len(cfg.get("problems", [])) or cfg.get("num_problems", 3)
        color = WEEK_COLORS[(n - 1) % len(WEEK_COLORS)]
        emoji = EMOJI[(n - 1) % len(EMOJI)]
        cards.append(
            f'  <a class="card" style="border-left-color:{color}" href="weeks/grade4/week{n}/{html_name}">\n'
            f'    <span class="emoji">{emoji}</span>\n'
            f'    <span class="text">\n'
            f'      <span class="title">Week {n}</span>\n'
            f'      <span class="desc">Grade 4 · {nprob} problems</span>\n'
            f'    </span>\n'
            f'    <span class="arrow">→</span>\n'
            f'  </a>'
        )
    text = INDEX.read_text()
    start = "<!-- WEEKS:START (auto-generated by build_week.py — do not edit between these markers) -->"
    end = "<!-- WEEKS:END -->"
    a, b = text.index(start), text.index(end)
    new = text[:a] + start + "\n" + "\n".join(cards) + "\n  " + text[b:]
    INDEX.write_text(new)
    print(f"  index.html: {len(cards)} week cards")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return
    if argv[0] == "--index":
        rebuild_index(); return
    if argv[0] == "--all":
        for d in all_weeks():
            build_week(d)
        rebuild_index(); return
    build_week(argv[0])
    rebuild_index()


if __name__ == "__main__":
    main(sys.argv[1:])
