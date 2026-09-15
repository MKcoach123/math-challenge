# Backend setup — Google Sheet + Apps Script (one time, ~10 min)

One script + one Sheet does everything: it **saves** each student's answers and **serves**
the scored leaderboard. The answer key lives in the Sheet and never reaches a browser.

## 1. Create the Sheet
- <https://sheets.google.com> → blank spreadsheet → name it `Math Challenge`.
- Add a tab named **`AnswerKey`** (rename "Sheet1" or insert a new tab) with this header row:

  | Week | Answer 1 | Answer 2 | Answer 3 |
  |------|----------|----------|----------|
  | Grade 4 — Week 2 | 9 | _(B/C/D…)_ | _(B/C/D…)_ |

  - The `Week` text must match the page's label **exactly** (`Grade 4 — Week 2`).
  - Fill answers as students submit them: numbers for free-text, the letter for multiple choice.
  - The `Submissions` tab is created automatically on the first submission — don't make it by hand.

## 1b. (Optional) Add a `Roster` tab — only needed for the **class-progress board**

`class_progress.html` shows how much of the points available to a *whole class* that class
collected. To do that the backend has to know who is in which class. Add a tab named
**`Roster`** with exactly this header row:

| Name | Class |
|------|-------|
| Jaylee B | Ms. Hood |
| Anaya K | Ms. Hood |
| Julieth M | Mr. Diaz |

- List **every student in the class**, not only the ones who take part — the class size is the
  denominator each week is measured against, and that is deliberate: persuading one more
  classmate to join raises the class's number just as much as one more right answer does.
- `Name` must match what the student **types into the answer page**. Matching ignores case,
  spacing and periods (`anaya k.` = `Anaya K`), but not different names.
- A student listed twice counts once (first listing wins), so a stray duplicate can't inflate
  a class.
- Names that submit but aren't on the roster are **listed on the page in a yellow banner** —
  their points count for nobody until you add them or fix the spelling.
- No `Roster` tab? The class board just shows setup instructions. Nothing else breaks.

## 2. Add the script
- In the Sheet: **Extensions → Apps Script**.
- Delete the starter code, paste **all** of `apps_script_backend.gs` (this folder), **Save** 💾.

## 3. Deploy as a Web App
- **Deploy → New deployment** → gear ⚙ → **Web app**.
- **Execute as:** *Me*  ·  **Who has access:** *Anyone*  (required: students aren't logged in).
- **Deploy** → authorize (your account → Advanced → "Go to … (unsafe)" → Allow — it's your own script).
- Copy the **Web app URL** (ends in `/exec`).
- Sanity check: open that URL in a browser — you should see `{"ok":true,...}`.

## 4. Wire the URL into the pages
Paste the `/exec` URL into the `ENDPOINT_URL = ""` line in **all three** places:
- `weeks/grade4/week2/grade4_week2.html`  (so submissions save)
- `weeks/grade4/week2/_build.py`           (so a rebuild keeps the URL)
- `weeks/grade4/leaderboard.html`          (so the board can read scores)

## 5. Test
- Open `grade4_week2.html`, submit a name + answers → a row appears in `Submissions`.
- Open `leaderboard.html` → your score shows (if you chose "show my name"); private names
  appear only via **Find my rank**.

## Updating the script later
**Deploy → Manage deployments → Edit ✏ → Version: New version** keeps the **same URL**.
A brand-new deployment makes a *new* URL (and you'd have to re-paste it everywhere).

## Notes
- **One URL for all weeks & the leaderboard.** Reuse it; the `Week` column separates weeks.
- **Privacy:** the form defaults to **Private**; private students are hidden from the public
  board but can self-check via "Find my rank". Latest submission sets a student's name + choice.
- **Scoring:** 1 point per correct answer, compared case/space-insensitively. A week with no
  `AnswerKey` row just scores 0 until you fill it in.
- **One submission per student:** not enforced — re-submits add rows; the leaderboard uses each
  student's **latest** submission per week.
- **Class board (`?view=classes`):** a week only counts once its `AnswerKey` row is filled in —
  unscoreable weeks are skipped entirely rather than dragging every class down to 0%.
  ⚠️ The whole board rests on students typing a name that matches the `Roster`. Check the
  yellow "not on the class list" banner after the first week.
