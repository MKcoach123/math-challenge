# Math Challenge Website — Project Analysis

Created: 2026-06-11

## Concept

Weekly math challenge website for a classroom. Each week three problems from old Math Kangaroo contests are posted. Students submit answers online or on paper. At week's end scores are posted to a leaderboard and solutions are revealed. A new set of three problems then goes live.

---

## Core Features

| Feature | Description |
|---------|-------------|
| Problem display | 3 problems per week, shown as images, viewable online or printable |
| Answer submission | Student enters name + answers; one submission per student per week |
| Scoring | Answers compared to key; points added to running total |
| Leaderboard | Updated once per week after deadline |
| Solution reveal | After deadline: correct answers + explanations shown |
| Weekly cycle | Active → Closed → Revealed → Next week |
| Admin | Teacher uploads problems, answer key, triggers state changes |

---

## Key Design Decisions

**Student identity** — no email needed; teacher issues a join code or nickname per student. Keeps it simple and avoids privacy issues with minors.

**Answer type** — free-text numeric answers (Math Kangaroo problems in this set are free-response, not multiple-choice A–E).

**Weekly flip** — manual "Advance week" button for teacher is simpler and more reliable than a cron job.

**Problem format** — screenshot images embedded as base64 in the HTML. Self-contained, no server needed for the static view.

---

## Complexity Tiers

| Scope | Includes | Effort |
|-------|----------|--------|
| **Minimal** | Static HTML per week, Google Form for answers, Google Sheet leaderboard | 1–2 days |
| **Simple web app** | Login, DB-backed submissions, auto-scoring, leaderboard, teacher dashboard | 2–3 weeks |
| **Full** | Auth, scheduler, solution display, history/stats per student, mobile | 6–10 weeks |

**Recommended start:** Simple web app scope.

---

## Potential Issues

- **Copyright** — Math Kangaroo problems are copyrighted. Private classroom use is likely fine under educational fair use; a public site is a gray area.
- **Cheating** — Solutions are publicly available online; hard to prevent during the week without proctoring.
- **Multiple submissions** — Needs server-side enforcement; a form alone won't prevent re-submission.
- **Privacy (COPPA)** — Collecting names/scores of children under 13 in the US requires parental consent. Use first name + last initial only; no email.
- **Engagement drop-off** — Leaderboard can demotivate students who fall behind. Consider resetting scores by term or adding bonus problems.
- **Teacher workload** — Someone prepares 3 problems + answer key + solution explanation every week. Build a backlog early.

---

## Pros / Cons

**Pros**
- Real competition math problems — high quality, age-calibrated
- Gamification drives repeat engagement
- Print option is inclusive for students without devices
- Low stakes → safe to try hard problems
- History of solutions builds a study resource

**Cons / Risks**
- Leaderboard can create stress for weaker students
- Weekly cadence requires sustained teacher commitment
- Tech failure during deadline week causes headaches
- Younger kids (grades 1–2) may need help with online submission

---

## Open Questions

- Should scores reset each term or accumulate all year?
- Should there be separate leaderboards per grade?
- What point values? (Math Kangaroo uses 3/4/5 pt tiers)
- Should solutions include step-by-step explanations or just the answer?
- Mobile-friendly from day one or desktop first?
