# Math Challenge — Status

Last updated: 2026-06-12

---

## What this project is

A classroom math challenge website where students solve 3 Math Kangaroo problems per week, submit answers online or on paper, and compete on a leaderboard. After the weekly deadline, correct answers and solutions are revealed and a new set of problems goes live.

---

## Folder structure

```
MathChallenge/
├── STATUS.md                        ← this file
├── planning/
│   └── project_analysis.md          ← full concept analysis, pros/cons, open questions
└── weeks/
    └── grade4/
        ├── leaderboard.html         ← reads scores from the backend; Overall + per-week + "Find my rank"
        ├── week1/
        │   ├── grade4_week1.html    ← self-contained problem page (images base64-embedded)
        │   └── source_images/
        │       ├── p1_sequence_pattern.png   ← "5th pattern in sequence" problem
        │       ├── p2_morgan_tiles.png       ← "Morgan's bedroom tiles" problem
        │       └── p3_subtraction_digits.png ← "triangle/square digits" subtraction problem
        └── week2/
            ├── grade4_week2.html    ← self-contained page; free-text + multiple-choice problems
            ├── _build.py            ← regenerates the HTML, base64-embedding source_images
            ├── apps_script_backend.gs ← Google Apps Script that saves submissions to a Sheet
            ├── SHEET_SETUP.md        ← 5-min setup to connect the page to a Google Sheet
            ├── problems.pages        ← original Apple Pages doc the problems came from
            └── source_images/
                ├── p2_tom_house.png   ← "back of Tom's house" (multiple choice A–E)
                └── p3_cube_solid.png  ← "8-cube solid from above" (multiple choice A–E)
```

---

## Current state

### What exists

**`weeks/grade4/week1/grade4_week1.html`** — fully working single-file HTML page:
- Blue gradient header: "Grade 4 — Week 1 · Math Challenge Problems"
- Due date and point info in header (📅 Due: Sunday night · 🏆 3 problems · 1 point each)
- Student name field
- 3 problem cards, each with:
  - Problem screenshot (base64-embedded — no external files needed)
  - Free-text answer input with unit hint
  - Color-coded left border (blue / teal / purple per problem)
- Submit button with basic client-side validation (name + all 3 answers required)
- Submit currently shows a confirmation alert — **no backend yet**
- Print button (top-right of header)
- Print CSS: A4 page, problems distributed across full page height, due date visible, answer boxes become underlines

### Week 1 problems (Grade 4)

| # | Problem | Answer type |
|---|---------|-------------|
| 1 | Sequence of square patterns — how many squares in the 5th pattern? | Number |
| 2 | Morgan's L-shaped tiles — fewest tiles to cover a 6×6 floor? | Number |
| 3 | Subtraction with △ and □ hiding digits — what digit is the triangle? | Single digit |

Answer key not yet recorded in the project (to be added when ready to score).

---

### Week 2 problems (Grade 4)

Built from `week2/problems.pages`. Mixes answer types (the page template now supports both):

| # | Problem | Answer type |
|---|---------|-------------|
| 1 | Ages — Nancy/Mary/Clark/Ben; how old is Nancy? | Number (free text) |
| 2 | Back of Tom's house (3 windows, no door) — which view? | Multiple choice A–E |
| 3 | Solid of 8 cubes — view from above? | Multiple choice A–E |

Answer key: Problem 1 = **9** (Ben 14 → Clark 7 → Nancy 9). Problems 2 & 3 multiple-choice
answers not yet confirmed — teacher to record.

### Submission backend (Google Sheet)

Chosen approach: **Google Apps Script Web App → Google Sheet** (keeps the custom page, no server to host).
- `week2/apps_script_backend.gs` appends one row per submission to a `Submissions` tab.
- `week2/SHEET_SETUP.md` has the one-time deploy steps.
- The page's `ENDPOINT_URL` constant is **still blank** — until set, Submit shows a local
  confirmation only. Paste the deployed `/exec` URL into both `grade4_week2.html` and `_build.py`.
- Same URL is reused for every week; the `Week` column distinguishes submissions.

---

## Leaderboard plan (decided 2026-06-13)

- **Two views:** per-week leaderboard AND cumulative-across-weeks, toggled on one page
  (kids may shine in a single week or by consistency over the whole run).
- **Run length:** plan for **8 weeks** total.
- **Privacy:** each student chooses at submission whether to appear **publicly (name shown)**
  or **privately**. Exact "private" appearance still being decided (hidden + self-lookup,
  anonymous alias, or fully hidden) — see open question below.
- **Architecture:** same single Apps Script + Sheet. A read endpoint (`doGet`) grades
  submissions against an `AnswerKey` tab server-side (key never reaches the browser) and
  returns ranked JSON; a static `leaderboard.html` fetches and renders it.
- **Sheet gains:** an `AnswerKey` tab (Week, A1, A2, A3) and a `Display` column
  (Public/Private) on `Submissions`. Latest submission's choice wins per student.

## What needs to be built next

### Backend — LIVE
Deployed Web App URL is wired into `week1`, `week2`, and `leaderboard.html`.
`ENDPOINT_URL = https://script.google.com/macros/s/AKfycbx5Xl-3-NRx5vnqZVKx4_7XiJI1iKR4Wiit8beSmlm15rJX-Fs7LBZrkk6IFseDSFK3Jw/exec`
Both weeks save to the `Submissions` tab; the leaderboard reads + scores live against `AnswerKey`.

### Answer keys (in the Sheet's `AnswerKey` tab — Week text must match the page label)
- **Grade 4 — Week 1:** P1 = `9`, P2 = `12`, P3 = `9`  ✅ entered & scoring
- **Grade 4 — Week 2:** P1 = `9`, P2 = `E`, P3 = `C`  ✅ entered & scoring
- **Grade 4 — Week 3:** P1 = `10` (squares), P2 = `8` (triangles), P3 = `16` (rectangles), P4 = `9` (cubes), P5 = `11` (pebbles)  ✅ confirmed (5 problems)

### Near-term
- [ ] Add the `Grade 4 — Week 1` row to the `AnswerKey` tab
- [ ] Delete leftover test rows from `Submissions` (e.g. `DELETE_ME_W1`, Probe*, Test Bot T, Lalala, YoYoYo)
- [x] Deploy the Apps Script and wire `ENDPOINT_URL` into all pages
- [x] Confirm multiple-choice answer keys for Week 2 problems 2 & 3 (E, C)
- [x] Backfill Week 1 page with save-to-Sheet wiring + privacy toggle (`Grade 4 — Week 1`)
- [x] Add `Display` (public/private) choice to the submission forms (defaults Private)
- [x] Extend Apps Script with scoring `doGet` (cumulative + per-week + Find-my-rank)
- [x] Build `leaderboard.html` (Overall + per-week toggle, top-3 medals, private self-lookup)
- [ ] Create the `AnswerKey` tab and record answers as weeks close

### For a proper web app
- [ ] Student identity system (teacher-issued codes or nicknames; no email)
- [ ] Server-side submission storage (one submission per student per week)
- [ ] Auto-scoring against answer key
- [ ] Leaderboard page (sortable, per-grade optional)
- [ ] Weekly state machine: Active → Closed → Revealed
- [ ] Solution reveal page (shown after deadline)
- [ ] Teacher admin dashboard (upload problems, enter answer key, advance week)

### Design decisions still open
- See `planning/project_analysis.md` for full list
- Key ones: score reset policy, per-grade leaderboards, point values, mobile priority

---

## How to continue in a new session

1. Read this file first, then `planning/project_analysis.md` for full context
2. Open `weeks/grade4/week1/grade4_week1.html` in a browser to see the current state
3. The HTML file is self-contained — edit it directly; no build step needed
4. Next likely task: choose a submission backend and wire up the Submit button

---

## Tech notes

- Problem images are base64-encoded PNGs embedded directly in the HTML — the file is fully portable
- Print CSS uses `@media print` with `@page { size: A4 }` and flex layout to fill the page
- Submit button calls `submitAnswers()` JS function — currently just shows an alert; replace with a fetch/POST call once a backend exists
- The `nth-child` color scheme on problem cards depends on them being direct children of `<form id="quiz">`
