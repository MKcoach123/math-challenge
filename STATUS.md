# Math Challenge — Project Status & Resume Guide

Last updated: 2026-06-15

> **Read this first if starting a new session.** It captures the whole project state, how it's
> deployed, and exactly how to make changes. Companion: `planning/project_analysis.md` (concept).

---

## 1. What this is

A classroom math-challenge website. Each week, students solve a set of Math Kangaroo problems
(currently 3–5 per week), submit answers online (or print on paper), and compete on a leaderboard.
After the weekly deadline the answers + solutions are revealed. Planned run: **8 weeks**, Grade 4.

**It is fully live and working** — pages hosted, submissions saving, scoring + leaderboard running.

---

## 2. Live URLs

- **Site (share this):** https://MKcoach123.github.io/math-challenge/
  - Leaderboard: `…/weeks/grade4/leaderboard.html`
  - Week N problems: `…/weeks/grade4/weekN/grade4_weekN.html`
  - Week 2 solutions: `…/weeks/grade4/week2/solutions_week2.html`
- **GitHub repo:** `MKcoach123/math-challenge` (public; GitHub Pages from `main` / root)
- **Backend endpoint (Apps Script Web App):**
  `https://script.google.com/macros/s/AKfycbx5Xl-3-NRx5vnqZVKx4_7XiJI1iKR4Wiit8beSmlm15rJX-Fs7LBZrkk6IFseDSFK3Jw/exec`

---

## 3. How it's built (architecture)

- **Static HTML pages**, fully self-contained (problem images base64-embedded). Hosted on GitHub Pages.
- **One Google Apps Script Web App + one Google Sheet** is the entire backend:
  - `doPost` → appends a row to the **`Submissions`** tab.
  - `doGet` → grades submissions against the **`AnswerKey`** tab (server-side; the key never
    reaches the browser) and returns ranked JSON for the leaderboard.
- **`leaderboard.html`** fetches that JSON: Overall (cumulative) + per-week views, top-3 medals,
  "Find my rank" self-lookup, and instant-load `localStorage` caching (Apps Script is ~2–3 s/call).
- **`build_week.py`** is a reusable generator: reads a per-week `week.json` + images, emits the
  week's HTML, and auto-rebuilds the home-page cards.

### Privacy model
Submission form has a Public/Private choice, **defaults to Private**. Private students are hidden
from the public board but can find their own rank via "Find my rank". (Decided 2026-06-13.)

---

## 4. File structure

```
MathChallenge/
├── index.html                         ← home page (hub): leaderboard + week cards (auto-generated)
├── STATUS.md                          ← this file
├── .gitignore
├── planning/project_analysis.md       ← concept analysis, pros/cons, open questions
└── weeks/grade4/
    ├── build_week.py                  ← THE generator (build a week + rebuild index)
    ├── leaderboard.html               ← Overall + per-week + Find-my-rank + caching
    ├── week1/
    │   ├── grade4_week1.html          ← hand-built page (NOT from generator); wired to backend
    │   ├── week.json                  ← metadata only (no problems[]) — used for the index card
    │   └── source_images/ (3 png)
    ├── week2/
    │   ├── grade4_week2.html          ← generated (5 problems)
    │   ├── week.json                  ← full config incl. "solutions" + "solutions_available"
    │   ├── solutions_week2.html       ← answers + solutions page (gated button on home)
    │   ├── solutions_week2.pages      ← source doc for the solutions
    │   ├── problems.pages             ← source doc for the problems
    │   ├── apps_script_backend.gs     ← THE backend script (paste this into Apps Script)
    │   ├── SHEET_SETUP.md             ← one-time Sheet/Apps-Script setup notes
    │   └── source_images/ (3 png: star_value, tom_house, cube_solid)
    └── week3/
        ├── grade4_week3.html          ← generated (5 problems)
        ├── week.json                  ← full config (image_max_width 260px)
        ├── problems_week3.pages        ← source doc
        └── source_images/ (4 png)
```

Note: `apps_script_backend.gs` lives in `week2/` for historical reasons but is the **global** backend
for all weeks. `_extract/`, `__pycache__/`, `.DS_Store`, `.claude/` are gitignored.

---

## 5. Weeks & answer keys

All weeks are live and scoring. Keys live in the Sheet's **`AnswerKey`** tab (columns:
`Week | Answer 1 … Answer 6`). The `Week` cell must match the page label (dash/spacing tolerant).

| Week | # | Problems (type) | Answer key |
|------|---|-----------------|-----------|
| **Grade 4 — Week 1** | 5 | squares sequence-5th (num,img), Sarah's tiles on 6×6 (num,img), Clare's legs (num), missing number 24,3,21,6,18,? (num), △5−48=4□ triangle digit (num,img) | `9, 12, 24, 9, 9` |
| **Grade 4 — Week 2** | 5 | Anna's father (num), Nancy (num), star value (num, img), Tom's house (A–E), 8-cube view (A–E) | `36, 9, 6, E, C` |
| **Grade 4 — Week 3** | 5 | squares (num,img), triangles (num,img), rectangles (num,img), cubes (num,img), pebbles (num) | `10, 8, 16, 9, 11` |
| **Grade 4 — Week 4** | 5 | Kenga jumps (num,img), half glass (num,img), Albert's cards right-end (num,img), squares balance 3 triangles (num,img), hens&eggs (num,img) | `8, 250, 8, 6, 12` |

All three verified scoring 5/5 (or 3/3) on all-correct test submissions.

⚠️ **Reorder gotcha:** if you insert/reorder problems, the answer-key columns shift. Always re-check
the `AnswerKey` row order after editing a week (this bit us on Weeks 2 & 3).

---

## 6. How to do common tasks

### Update / add a week's problems
1. Drop the updated `.pages` (or images) into `weeks/grade4/weekN/`.
2. Extract: unzip the `.pages` (it's a zip) → `Data/*.png` are the figures; `preview.jpg` is page 1.
   For text on later pages, decompress `Index/Document.iwa` (pure-Python Snappy decoder — see git
   history of this session / the technique: IWA chunks = `00` + 3-byte LE length + snappy block).
3. Save chosen images into `weekN/source_images/` and write/update `weekN/week.json`.
   - problem `type`: `"number"`/`"text"` (free-text box) or `"choice"` (A–E radios).
   - optional per-problem `"image"`, `"image_width"`; week-level `"image_max_width"` (e.g. "260px").
4. Build: `cd weeks/grade4 && python3 build_week.py weekN`  (also rebuilds `index.html` cards).
5. Update the `AnswerKey` tab row (add `Answer N` columns as needed) — backend already supports up to 6.
6. **Deploy:** `git add -A && git commit -m "…" && git push`  (Pages updates in ~1 min).

### Add a solutions page (with the gated reveal button)
- Build a `solutions_weekN.html` in the week folder (see `week2/solutions_week2.html` as the model).
- In `weekN/week.json` add `"solutions": "solutions_weekN.html"` and `"solutions_available": false`.
- The home-page button shows **🔒 locked** until you flip `solutions_available` to `true`, then
  rebuild (`python3 build_week.py --index`) + push to "reveal" after the deadline.

### Change the backend script
1. Edit `weeks/grade4/week2/apps_script_backend.gs`, commit/push.
2. Copy the new code from the raw GitHub URL (guaranteed current):
   `https://raw.githubusercontent.com/MKcoach123/math-challenge/main/weeks/grade4/week2/apps_script_backend.gs`
3. ⚠️ **Open the Sheet → Extensions → Apps Script** (the *Sheet-bound* project — NOT script.google.com,
   which opens a different/empty project). Paste over `Code.gs`, Save.
4. **Deploy → Manage deployments → Edit ✏ → Version: New version → Deploy** (keeps the same URL).
5. Verify: `curl '<endpoint>?view=debug'` shows the parsed keys.

### Verify scoring / debug
- `…/exec?view=debug` → tabs, AnswerKey headers, parsed keys, submission weeks, week-match flags.
- `…/exec?view=leaderboard[&week=Grade 4 — Week N]` → ranked public rows + hiddenCount.
- `…/exec?view=findme&name=…[&week=…]` → one student's rank/points (works for private students).

---

## 7. Deployment / environment notes

- The local folder `/Users/natalia/FunWithAI/MathChallenge` is a **git repo** → `MKcoach123/math-challenge`.
- Authenticated via `gh` (account MKcoach123, brew-installed at `/opt/homebrew/bin`). Updates = `git push`.
- **Do NOT use the browser drag-upload** on GitHub — it kept dropping files in the wrong folder.
  Always push from the local repo instead.
- **Local preview:** `python3 -m http.server 8000` in the repo root → http://localhost:8000/.
  Needed because Safari blocks `file://` navigation between pages ("outside the sandbox").
- GitHub Pages CDN lags ~20–60 s after a push; `raw.githubusercontent.com/.../main/...` reflects the
  repo immediately. Browsers cache — hard-refresh with **Cmd+Shift+R**.

---

## 8. Open items / next steps

- [ ] **Clean test rows** from the `Submissions` tab: `ZZ_W2`, `ZZ_W3`, `ZZ_TEST*`, `DELETE_ME_W1`,
      `Probe*`, `Test Bot T`, `Lalala`, `YoYoYo`, etc.
- [ ] Week 2 solutions button is currently **enabled** (`solutions_available: true`) for testing. For
      real use, set it `false` during the week and flip to `true` after the deadline.
- [ ] Add solutions pages for Weeks 1 & 3 if desired.
- [ ] Weeks 4–8 problems (drop `.pages` in `weekN/` and run the generator).
- [ ] Add the per-week **due date** to `week.json` (`"due"`) — currently "Sunday night" placeholder.
- [ ] (Optional) one-submission-per-student enforcement; per-grade leaderboards; score reset policy.

---

## 9. Design decisions locked

- Backend: Google Apps Script + Sheet (no server to host).
- Hosting: GitHub Pages, updated via `git push`.
- Leaderboard: Overall **and** per-week; up to 8 weeks; backend supports 3–6 problems/week.
- Privacy: per-student Public/Private, defaults Private; private = hidden + self-lookup.
- Identity: first name + last initial, no email (COPPA-conscious).
- Manual "reveal" of solutions (flag flip) rather than time-based automation.
