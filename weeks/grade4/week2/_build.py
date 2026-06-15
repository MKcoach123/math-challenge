#!/usr/bin/env python3
"""Generate grade4_week2.html with base64-embedded images.
Re-run after editing the template below or swapping source images."""
import base64, pathlib

here = pathlib.Path(__file__).parent

def b64(name):
    data = (here / 'source_images' / name).read_bytes()
    return 'data:image/png;base64,' + base64.b64encode(data).decode()

IMG_P2 = b64('p2_tom_house.png')
IMG_P3 = b64('p3_cube_solid.png')

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Grade 4 — Week 2</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: 'Segoe UI', system-ui, Arial, sans-serif;
  background: #f0f4ff;
  padding: 24px 16px 48px;
  color: #1e293b;
}}

.page {{ max-width: 860px; margin: 0 auto; }}

/* ── Top navigation ── */
.topnav {{ display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }}
.topnav a {{
  display: inline-flex; align-items: center; gap: 6px; text-decoration: none;
  color: #4f46e5; font-weight: 700; font-size: 15px;
  padding: 8px 16px; background: #fff; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,.06);
  transition: transform .15s, box-shadow .15s;
}}
.topnav a:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.1); }}
.topnav a.lb {{ color: #b45309; }}

/* ── Header ── */
.header {{
  background: linear-gradient(135deg, #1d4ed8, #4f46e5);
  color: white;
  border-radius: 16px;
  padding: 28px 36px;
  margin-bottom: 28px;
  box-shadow: 0 6px 24px rgba(30,64,175,.3);
}}
.header h1 {{ font-size: 32px; font-weight: 900; letter-spacing: -.5px; }}
.header .sub {{ font-size: 16px; opacity: .85; margin-top: 6px; }}
.header .week-info {{ display: flex; gap: 24px; margin-top: 14px; font-size: 14px; opacity: .9; }}
.header .week-info span {{ background: rgba(255,255,255,.18); border-radius: 8px; padding: 4px 12px; }}

/* ── Student name box ── */
.name-box {{
  background: white; border-radius: 12px; padding: 18px 24px; margin-bottom: 24px;
  box-shadow: 0 2px 10px rgba(0,0,0,.08); display: flex; align-items: center; gap: 16px;
}}
.name-box label {{ font-weight: 700; font-size: 16px; white-space: nowrap; }}
.name-box input {{
  flex: 1; border: 2px solid #c7d2fe; border-radius: 8px; padding: 10px 14px;
  font-size: 16px; outline: none; transition: border-color .2s;
}}
.name-box input:focus {{ border-color: #4f46e5; }}

/* ── Problem card ── */
.problem {{
  background: white; border-radius: 16px; padding: 28px 32px; margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,.08); border-left: 6px solid #4f46e5;
}}
.problem:nth-child(2) {{ border-left-color: #0891b2; }}
.problem:nth-child(3) {{ border-left-color: #7c3aed; }}

.problem-num {{
  font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: .08em;
  color: #4f46e5; margin-bottom: 10px;
}}
.problem:nth-child(2) .problem-num {{ color: #0891b2; }}
.problem:nth-child(3) .problem-num {{ color: #7c3aed; }}

.problem-text {{ font-size: 17px; line-height: 1.5; margin: 6px 0 4px; }}

.problem img {{
  max-width: 100%; border-radius: 8px; margin: 16px 0; border: 1px solid #e2e8f0;
}}

/* ── Answer area (free text) ── */
.answer-area {{
  margin-top: 18px; display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
}}
.answer-label {{ font-weight: 700; font-size: 16px; }}
.answer-area input[type=text] {{
  width: 120px; border: 2.5px solid #c7d2fe; border-radius: 8px; padding: 10px 14px;
  font-size: 18px; font-weight: 700; text-align: center; outline: none; transition: border-color .2s;
}}
.answer-area input[type=text]:focus {{ border-color: #4f46e5; }}

/* ── Answer area (multiple choice A–E) ── */
.choices {{ gap: 12px; }}
.choice {{ display: inline-flex; cursor: pointer; }}
.choice input {{ position: absolute; opacity: 0; width: 0; height: 0; }}
.choice span {{
  display: inline-flex; align-items: center; justify-content: center;
  width: 46px; height: 46px; border-radius: 50%; border: 2.5px solid #c7d2fe;
  font-size: 19px; font-weight: 800; color: #475569; user-select: none;
  transition: background .15s, border-color .15s, color .15s, box-shadow .15s;
}}
.choice:hover span {{ border-color: #94a3b8; }}
.choice input:checked + span {{
  background: #4f46e5; border-color: #4f46e5; color: #fff; box-shadow: 0 3px 10px rgba(79,70,229,.4);
}}
.problem:nth-child(2) .choice input:checked + span {{ background: #0891b2; border-color: #0891b2; box-shadow: 0 3px 10px rgba(8,145,178,.4); }}
.problem:nth-child(3) .choice input:checked + span {{ background: #7c3aed; border-color: #7c3aed; box-shadow: 0 3px 10px rgba(124,58,237,.4); }}
.choice input:focus-visible + span {{ outline: 2px solid #4f46e5; outline-offset: 2px; }}

/* ── Leaderboard visibility choice ── */
.visibility-box {{
  background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 12px;
  padding: 14px 20px; margin-bottom: 24px; font-size: 15px;
}}
.visibility-box .vq {{ font-weight: 700; margin-bottom: 8px; display: block; }}
.visibility-box label {{ display: inline-flex; align-items: center; gap: 7px; margin-right: 22px; cursor: pointer; }}
.visibility-box .hint {{ display: block; margin-top: 6px; font-size: 13px; color: #64748b; }}

/* ── Submit ── */
.submit-row {{ text-align: center; margin-top: 8px; }}
.btn-submit {{
  background: linear-gradient(135deg, #1d4ed8, #4f46e5); color: white; border: none;
  border-radius: 12px; padding: 16px 48px; font-size: 18px; font-weight: 800; cursor: pointer;
  box-shadow: 0 4px 16px rgba(79,70,229,.4); transition: transform .15s, box-shadow .15s;
}}
.btn-submit:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(79,70,229,.5); }}
.btn-submit:active {{ transform: translateY(0); }}
.btn-submit:disabled {{ opacity: .6; cursor: default; transform: none; box-shadow: none; }}

/* ── Print styles ── */
@media print {{
  @page {{ size: A4 portrait; margin: 12mm 14mm; }}

  html, body {{
    background: white !important; padding: 0 !important; margin: 0 !important;
    -webkit-print-color-adjust: exact; print-color-adjust: exact;
  }}

  .page {{ max-width: 100%; margin: 0; }}

  /* Hide input hint text on paper */
  input::placeholder {{ color: transparent !important; opacity: 0 !important; }}
  input::-webkit-input-placeholder {{ color: transparent !important; opacity: 0 !important; }}

  .header {{
    background: none !important; color: black !important; border-radius: 0 !important;
    box-shadow: none !important; padding: 0 0 7pt 0 !important; margin-bottom: 12pt !important;
    border-bottom: 2.5pt solid #1d4ed8;
  }}
  .header h1   {{ font-size: 19pt !important; letter-spacing: 0 !important; color: #1d4ed8 !important; }}
  .header .sub {{ font-size: 10.5pt !important; margin-top: 2pt !important; opacity: 1 !important; color: #333 !important; }}
  .header .week-info {{ display: flex !important; margin-top: 5pt !important; font-size: 10pt !important; gap: 18pt !important; opacity: 1 !important; color: #333 !important; }}
  .header .week-info span {{ background: none !important; padding: 0 !important; border-radius: 0 !important; }}
  .print-btn {{ display: none !important; }}
  .topnav {{ display: none !important; }}

  .name-box {{
    background: none !important; box-shadow: none !important; border-radius: 0 !important;
    border: none !important; padding: 0 !important; margin-bottom: 12pt !important;
    display: flex; align-items: baseline; gap: 8pt;
  }}
  .name-box label {{ font-size: 11pt !important; font-weight: 700 !important; white-space: nowrap; }}
  .name-box input {{
    flex: 1; border: none !important; border-bottom: 1pt solid #444 !important; border-radius: 0 !important;
    font-size: 11pt !important; background: none !important; padding: 1pt 4pt !important;
  }}

  #quiz {{ display: block; }}

  .problem {{
    background: none !important; box-shadow: none !important; border-radius: 0 !important;
    padding: 0 0 0 9pt !important; margin: 0 0 16pt 0 !important; border-left-width: 3.5pt !important;
    page-break-inside: avoid; break-inside: avoid;
  }}
  .problem:last-of-type {{ margin-bottom: 0 !important; }}

  .problem-num {{ font-size: 10pt !important; margin-bottom: 4pt !important; }}
  .problem-text {{ font-size: 11pt !important; line-height: 1.35 !important; margin: 2pt 0 4pt !important; }}

  .problem img {{
    width: auto !important; max-width: 100% !important; max-height: 230pt !important; height: auto !important;
    margin: 4pt 0 6pt !important; border: none !important; display: block;
  }}

  .answer-area {{ margin-top: 6pt !important; gap: 12pt !important; }}
  .answer-label {{ font-size: 11pt !important; }}
  .answer-area input[type=text] {{
    border: none !important; border-bottom: 1.5pt solid #333 !important; border-radius: 0 !important;
    font-size: 12pt !important; width: 90px !important; background: none !important; padding: 1pt 2pt !important;
  }}
  .answer-area span {{ font-size: 10.5pt !important; }}

  /* Multiple choice → circled letters to ring on paper */
  .choices {{ gap: 14pt !important; }}
  .choice span {{
    width: 22pt !important; height: 22pt !important; border: 1.25pt solid #333 !important;
    background: none !important; color: #000 !important; font-size: 12pt !important; box-shadow: none !important;
  }}
  .choice input:checked + span {{ background: none !important; color: #000 !important; border-color: #000 !important; }}

  .visibility-box {{ display: none !important; }}
  .submit-row {{ display: none !important; }}
}}

/* ── Print button ── */
.print-btn {{
  background: rgba(255,255,255,.16); border: 1.5px solid rgba(255,255,255,.65); border-radius: 8px;
  padding: 8px 18px; font-size: 14px; font-weight: 600; color: #ffffff; cursor: pointer; float: right;
  margin-top: 4px; transition: background .2s, border-color .2s;
}}
.print-btn:hover {{ background: rgba(255,255,255,.30); border-color: #ffffff; }}
</style>
</head>
<body>
<div class="page">

  <div class="topnav">
    <a href="../../../index.html">← Home</a>
    <a class="lb" href="../leaderboard.html">🏆 Leaderboard</a>
  </div>

  <!-- Header -->
  <div class="header">
    <button class="print-btn" onclick="window.print()">🖨 Print</button>
    <h1>Grade 4 — Week 2</h1>
    <div class="sub">Math Challenge Problems</div>
    <div class="week-info">
      <span>📅 Due: Sunday night</span>
      <span>🏆 3 problems · 1 point each</span>
    </div>
  </div>

  <!-- Student name -->
  <div class="name-box">
    <label for="sname">Your name:</label>
    <input type="text" id="sname" placeholder="First name Last initial" autocomplete="off">
  </div>

  <form id="quiz">

    <!-- Problem 1 — free-text number -->
    <div class="problem">
      <div class="problem-num">Problem 1</div>
      <p class="problem-text">Nancy is 3 years older than Mary. Clark is 2 years younger than Nancy.
        Ben is 14 years old and twice as old as Clark. How old is Nancy?</p>
      <div class="answer-area">
        <span class="answer-label">My answer:</span>
        <input type="text" id="a1" name="a1" placeholder="?" maxlength="4" autocomplete="off">
        <span style="font-size:14px;color:#64748b">years old</span>
      </div>
    </div>

    <!-- Problem 2 — multiple choice A–E -->
    <div class="problem">
      <div class="problem-num">Problem 2</div>
      <p class="problem-text">The picture shows the front of Tom's house. The back of his house has
        3 windows and no door. What does Tom see when he looks at the back of his house?</p>
      <img src="{IMG_P2}" alt="Front of Tom's house with answer options A through E">
      <div class="answer-area choices">
        <span class="answer-label">My answer:</span>
        <label class="choice"><input type="radio" name="a2" value="A"><span>A</span></label>
        <label class="choice"><input type="radio" name="a2" value="B"><span>B</span></label>
        <label class="choice"><input type="radio" name="a2" value="C"><span>C</span></label>
        <label class="choice"><input type="radio" name="a2" value="D"><span>D</span></label>
        <label class="choice"><input type="radio" name="a2" value="E"><span>E</span></label>
      </div>
    </div>

    <!-- Problem 3 — multiple choice A–E -->
    <div class="problem">
      <div class="problem-num">Problem 3</div>
      <p class="problem-text">The solid in the picture is made of 8 cubes. How does the solid look from above?</p>
      <img src="{IMG_P3}" alt="A solid made of 8 cubes with answer options A through E">
      <div class="answer-area choices">
        <span class="answer-label">My answer:</span>
        <label class="choice"><input type="radio" name="a3" value="A"><span>A</span></label>
        <label class="choice"><input type="radio" name="a3" value="B"><span>B</span></label>
        <label class="choice"><input type="radio" name="a3" value="C"><span>C</span></label>
        <label class="choice"><input type="radio" name="a3" value="D"><span>D</span></label>
        <label class="choice"><input type="radio" name="a3" value="E"><span>E</span></label>
      </div>
    </div>

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
// ── Paste your Google Apps Script Web App URL between the quotes to save to a Sheet.
// Leave empty to test the page without a backend (shows a confirmation only).
const ENDPOINT_URL = "https://script.google.com/macros/s/AKfycbx5Xl-3-NRx5vnqZVKx4_7XiJI1iKR4Wiit8beSmlm15rJX-Fs7LBZrkk6IFseDSFK3Jw/exec";

const WEEK_LABEL = "Grade 4 — Week 2";

async function submitAnswers(btn) {{
  const name = document.getElementById('sname').value.trim();
  if (!name) {{ alert('Please enter your name first!'); return; }}

  const a1 = document.getElementById('a1').value.trim();
  const a2 = (document.querySelector('input[name="a2"]:checked') || {{}}).value || '';
  const a3 = (document.querySelector('input[name="a3"]:checked') || {{}}).value || '';
  if (!a1 || !a2 || !a3) {{ alert('Please answer all three problems before submitting.'); return; }}

  const display = (document.querySelector('input[name="display"]:checked') || {{}}).value || 'Private';
  const payload = {{ week: WEEK_LABEL, name: name, display: display, a1: a1, a2: a2, a3: a3 }};

  // No backend configured yet → local confirmation (same behaviour as before).
  if (!ENDPOINT_URL) {{
    alert('Thanks ' + name + '! Your answers have been recorded.\\n\\n' +
          'Problem 1: ' + a1 + '\\nProblem 2: ' + a2 + '\\nProblem 3: ' + a3 +
          '\\n\\n(No Sheet connected yet — set ENDPOINT_URL to save online.)');
    return;
  }}

  const original = btn.textContent;
  btn.disabled = true; btn.textContent = 'Submitting…';
  try {{
    // text/plain avoids a CORS preflight that Apps Script does not handle.
    const res = await fetch(ENDPOINT_URL, {{
      method: 'POST',
      headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
      body: JSON.stringify(payload)
    }});
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

out = here / 'grade4_week2.html'
out.write_text(HTML)
print(f"Wrote {out} ({len(HTML):,} bytes)")
