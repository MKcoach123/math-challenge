/**
 * Math Challenge — backend (Google Apps Script Web App)
 *
 * One script + one Sheet powers everything:
 *   • doPost  — receives a student's answers, appends a row to "Submissions"
 *   • doGet   — grades submissions against "AnswerKey" and returns ranked JSON
 *               for the leaderboard page (cumulative, per-week, and self-lookup)
 *
 * Sheet tabs (see SHEET_SETUP.md):
 *   Submissions : Timestamp | Week | Name | Display | Answer 1 | Answer 2 | Answer 3
 *   AnswerKey   : Week | Answer 1 | Answer 2 | Answer 3
 *   Roster      : Name | Class          ← optional; only needed for ?view=classes
 *
 * The answer key stays server-side — it is never sent to a browser.
 */

var SUBMISSIONS = 'Submissions';
var ANSWER_KEY  = 'AnswerKey';
var ROSTER      = 'Roster';   // Name | Class — powers the class-progress board
var MAX_PROBLEMS = 6;   // supports 3–6 problems/week; AnswerKey/Submissions use Answer 1..6
var SUB_HEADER  = ['Timestamp', 'Week', 'Name', 'Display']
  .concat(answerCols());  // -> ... 'Answer 1' .. 'Answer 6'

function answerCols() {
  var cols = [];
  for (var i = 1; i <= MAX_PROBLEMS; i++) cols.push('Answer ' + i);
  return cols;
}

/* ───────────────────────── Write: receive a submission ───────────────────────── */

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.tryLock(10000); // serialize writes so rows don't collide
  try {
    var data = JSON.parse(e.postData.contents);

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(SUBMISSIONS) || ss.insertSheet(SUBMISSIONS);
    if (sheet.getLastRow() === 0) {
      sheet.getRange(1, 1, 1, SUB_HEADER.length).setValues([SUB_HEADER]);
      sheet.setFrozenRows(1);
    } else if (sheet.getLastColumn() < SUB_HEADER.length) {
      // Widen an older 3-answer sheet to Answer 1..6 (existing rows keep blanks).
      sheet.getRange(1, 1, 1, SUB_HEADER.length).setValues([SUB_HEADER]);
    }

    // Default to Private unless the student explicitly chose Public.
    var display = (norm(data.display) === 'public') ? 'Public' : 'Private';

    var row = [new Date(), data.week || '', data.name || '', display];
    for (var i = 1; i <= MAX_PROBLEMS; i++) row.push(data['a' + i] || '');
    sheet.appendRow(row);

    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

/* ───────────────────────── Read: leaderboard / self-lookup ───────────────────────── */

function doGet(e) {
  try {
    var p = (e && e.parameter) || {};
    var view = p.view || 'leaderboard';

    if (view === 'findme') {
      return json(findRank(p.name, p.week));        // private students look themselves up
    }
    if (view === 'debug') {
      return json(debugInfo());                     // inspect what the sheet parsing sees
    }
    if (view === 'classes') {
      return json(classProgress());                 // per-class, per-week collective progress
    }
    // view === 'leaderboard'  (optionally scoped to ?week=...)
    return json(leaderboard(p.week));
  } catch (err) {
    return json({ ok: false, error: String(err) });
  }
}

/** Public leaderboard. weekLabel omitted/blank ⇒ cumulative across all weeks. */
function leaderboard(weekLabel) {
  var s = computeStandings(weekLabel);
  var rows = s.standings
    .filter(function (x) { return x.display === 'Public'; })
    .map(function (x) {
      return { rank: x.rank, name: x.name, points: x.points, weeksPlayed: x.weeksPlayed };
    });
  var hidden = s.standings.length - rows.length;
  return {
    ok: true,
    scope: weekLabel ? 'week' : 'cumulative',
    week: weekLabel || '',
    weeks: s.weeks,
    rows: rows,
    hiddenCount: hidden,
    totalStudents: s.standings.length
  };
}

/** A single student's standing — works whether they are public or private. */
function findRank(name, weekLabel) {
  if (!name || !nameKey(name)) return { ok: true, found: false };
  var s = computeStandings(weekLabel);
  var key = nameKey(name);
  for (var i = 0; i < s.standings.length; i++) {
    if (s.standings[i].key === key) {
      var x = s.standings[i];
      return {
        ok: true, found: true, name: x.name, rank: x.rank,
        points: x.points, weeksPlayed: x.weeksPlayed,
        totalStudents: s.standings.length,
        scope: weekLabel ? 'week' : 'cumulative', week: weekLabel || ''
      };
    }
  }
  return { ok: true, found: false, totalStudents: s.standings.length };
}

/**
 * Core scoring. Returns { standings:[{key,name,points,weeksPlayed,display,rank}], weeks:[...] }
 * sorted by points desc then name, with competition ranks (ties share a rank).
 */
function computeStandings(weekLabel) {
  var key = getAnswerKey();                 // { normWeek: [a1,a2,a3] (normalized) }
  var subs = getRows(SUBMISSIONS);
  var wf = weekLabel ? norm(weekLabel) : null;

  // Latest submission per (student, week) wins.
  var latest = {};                          // "studentKey|weekKey" -> row
  var weeksSet = {};
  subs.forEach(function (r) {
    var wk = norm(r['Week']);
    if (!wk || !nameKey(r['Name'])) return;
    weeksSet[r['Week']] = true;          // record every week, independent of the filter
    if (wf && wk !== wf) return;
    var k = nameKey(r['Name']) + '|' + wk;
    var ts = new Date(r['Timestamp']).getTime() || 0;
    if (!latest[k] || ts >= latest[k]._ts) { r._ts = ts; r._wk = wk; latest[k] = r; }
  });

  // Aggregate per student.
  var byStudent = {};
  Object.keys(latest).forEach(function (k) {
    var r = latest[k];
    var sk = nameKey(r['Name']);
    var rec = byStudent[sk] || (byStudent[sk] = {
      key: sk, name: r['Name'], points: 0, weeksPlayed: 0, display: 'Private', _ts: -1
    });
    rec.weeksPlayed += 1;
    rec.points += scoreOne(r, key[r._wk]);
    if (r._ts >= rec._ts) {                 // newest submission sets the display name + privacy
      rec._ts = r._ts; rec.name = r['Name'];
      rec.display = (norm(r['Display']) === 'public') ? 'Public' : 'Private';
    }
  });

  var standings = Object.keys(byStudent).map(function (k) { return byStudent[k]; });
  standings.sort(function (a, b) {
    return b.points - a.points || a.name.localeCompare(b.name);
  });
  // Competition ranking (1,2,2,4,…)
  for (var i = 0; i < standings.length; i++) {
    standings[i].rank = (i > 0 && standings[i].points === standings[i - 1].points)
      ? standings[i - 1].rank : i + 1;
  }

  return { standings: standings, weeks: Object.keys(weeksSet).sort() };
}

/** Points for one submission vs the week's key (array of Answer 1..N). 1 point per correct answer. */
function scoreOne(row, keyArr) {
  if (!keyArr) return 0;                     // no key entered for this week yet
  var pts = 0;
  for (var i = 0; i < keyArr.length; i++) {
    if (keyArr[i] !== '' && norm(row['Answer ' + (i + 1)]) === keyArr[i]) pts++;
  }
  return pts;
}

/* ───────────────────────── helpers ───────────────────────── */

/** Diagnostic: shows the tabs found, the parsed answer key, and distinct submission weeks. */
function debugInfo() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var tabs = ss.getSheets().map(function (s) { return s.getName(); });
  var keyMap = getAnswerKey();
  var subWeeks = {};
  getRows(SUBMISSIONS).forEach(function (r) { if (r['Week']) subWeeks[r['Week']] = (subWeeks[r['Week']] || 0) + 1; });
  return {
    ok: true,
    tabs: tabs,
    answerKeyHeaders: (getRows(ANSWER_KEY)[0] ? Object.keys(getRows(ANSWER_KEY)[0]) : []),
    answerKeyParsed: keyMap,                 // normalized week -> [a1,a2,a3]
    submissionWeeks: subWeeks,               // exact Week text -> count
    weekMatch: Object.keys(subWeeks).reduce(function (acc, w) { acc[w] = !!keyMap[norm(w)]; return acc; }, {})
  };
}

/* ───────────────────────── Class progress (?view=classes) ─────────────────────────
 *
 * A collective board: how much of the points available to a WHOLE CLASS that class
 * actually collected. Deliberately not a ranking of individuals.
 *
 *   possible(week) = students in the class  ×  problems in that week
 *   pct(week)      = points the class earned / possible(week)
 *
 * The class size is the roster count, NOT the number who submitted — so persuading
 * one more classmate to take part raises the number just like getting one more
 * answer right does. That is the point of the board.
 *
 * Weeks with no answer key yet are skipped entirely (nobody can be scored, so
 * counting them would drag every class down for no reason).
 */
function classProgress() {
  var roster = getRoster();
  if (!roster.classes.length) {
    return { ok: true, rosterMissing: true, classes: [], weeks: [], byClass: {}, unmatched: [],
             note: 'Add a "Roster" tab with columns: Name | Class' };
  }

  var key  = getAnswerKey();                 // { normWeek: [a1..aN] }
  var subs = getRows(SUBMISSIONS);

  // Latest submission per (student, week) wins — same rule the individual board uses.
  var latest = {}, weeksSet = {}, unmatched = {};
  subs.forEach(function (r) {
    var wk = norm(r['Week']), nk = nameKey(r['Name']);
    if (!wk || !nk) return;
    if (!key[wk]) return;                    // no answer key for this week yet → unscoreable
    if (!roster.byName[nk]) { unmatched[String(r['Name']).trim()] = true; return; }
    weeksSet[r['Week']] = true;              // keep the label as typed, for display
    var k = nk + '|' + wk;
    var ts = new Date(r['Timestamp']).getTime() || 0;
    if (!latest[k] || ts >= latest[k]._ts) { r._ts = ts; r._wk = wk; latest[k] = r; }
  });

  // Tally points and participants per (class, week).
  var tally = {};                            // class -> weekLabel -> {points, participants}
  Object.keys(latest).forEach(function (k) {
    var r  = latest[k];
    var cls = roster.byName[nameKey(r['Name'])];
    var wl  = String(r['Week']).trim();
    var byWeek = tally[cls] || (tally[cls] = {});
    var cell   = byWeek[wl] || (byWeek[wl] = { points: 0, participants: 0 });
    cell.points += scoreOne(r, key[r._wk]);
    cell.participants += 1;
  });

  // Only weeks that have BOTH an answer key and at least one submission are shown.
  var weeks = Object.keys(weeksSet).sort();
  var problems = {};
  weeks.forEach(function (wl) { problems[wl] = key[norm(wl)].length; });

  var byClass = {};
  roster.classes.forEach(function (cls) {
    var size = roster.sizes[cls];
    // Three measures, and they multiply:  took part  ×  got right  =  collected.
    //   partPct = participants / class size          ← rises just by taking part
    //   acc     = points / problems attempted        ← rises by getting them right
    //   pct     = points / (class size × problems)   ← the two combined
    // Showing all three means a student who tries and scores 0 still visibly
    // moves their class forward, which pct and acc alone would never reward.
    var wk = {}, totPts = 0, totPos = 0, totTried = 0, totPart = 0, totSlots = 0;
    weeks.forEach(function (wl) {
      var cell = (tally[cls] && tally[cls][wl]) || { points: 0, participants: 0 };
      var possible = size * problems[wl];              // whole class × problems
      var tried    = cell.participants * problems[wl]; // only those who took part
      totPts += cell.points; totPos += possible; totTried += tried;
      totPart += cell.participants; totSlots += size;
      wk[wl] = {
        points: cell.points,
        possible: possible,
        participants: cell.participants,
        pct: possible ? round1(100 * cell.points / possible) : 0,
        tried: tried,
        acc: tried ? round1(100 * cell.points / tried) : null,
        partPct: size ? round1(100 * cell.participants / size) : 0
      };
    });
    byClass[cls] = {
      size: size,
      weeks: wk,
      total: { points: totPts, possible: totPos,
               pct: totPos ? round1(100 * totPts / totPos) : 0,
               tried: totTried,
               acc: totTried ? round1(100 * totPts / totTried) : null,
               // cumulative participation = every (student × week) slot filled
               participants: totPart, slots: totSlots,
               partPct: totSlots ? round1(100 * totPart / totSlots) : 0 }
    };
  });

  return {
    ok: true,
    classes: roster.classes,
    weeks: weeks,
    problems: problems,
    byClass: byClass,
    // Names that submitted but aren't on the roster — their points count for nobody.
    // Surfaced so a typo doesn't silently cost a class its score.
    unmatched: Object.keys(unmatched).sort()
  };
}

/** Roster tab → { byName: {nameKey: class}, sizes: {class: n}, classes: [sorted] } */
function getRoster() {
  var byName = {}, sizes = {};
  getRows(ROSTER).forEach(function (r) {
    var nk = nameKey(r['Name']);
    var cls = String(r['Class'] == null ? '' : r['Class']).trim();
    if (!nk || !cls) return;
    if (byName[nk]) return;                  // first listing wins; a dupe must not inflate class size
    byName[nk] = cls;
    sizes[cls] = (sizes[cls] || 0) + 1;
  });
  return { byName: byName, sizes: sizes, classes: Object.keys(sizes).sort() };
}

function round1(n) { return Math.round(n * 10) / 10; }

function getAnswerKey() {
  var map = {};
  getRows(ANSWER_KEY).forEach(function (r) {
    var wk = norm(r['Week']);
    if (!wk) return;
    var arr = [];
    for (var i = 1; i <= MAX_PROBLEMS; i++) arr.push(norm(r['Answer ' + i]));
    while (arr.length && arr[arr.length - 1] === '') arr.pop();  // trim unused trailing answers
    map[wk] = arr;
  });
  return map;
}

function getRows(sheetName) {
  var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);
  if (!sh || sh.getLastRow() < 2) return [];
  var values = sh.getDataRange().getValues();
  var header = values.shift().map(function (h) { return String(h).trim(); });
  return values.map(function (row) {
    var o = {};
    header.forEach(function (h, i) { o[h] = row[i]; });
    return o;
  });
}

function norm(v) {
  return String(v == null ? '' : v)
    .replace(/[‒-―−]/g, '-')   // en/em dashes & minus → plain hyphen
    .trim().toLowerCase().replace(/\s+/g, ' ');
}

/**
 * Identity key for a student NAME (used only to group submissions into one person).
 * On top of norm() it drops periods/commas, so "John S", "john s." and "John S."
 * all collapse to the same student. Display still uses the raw, latest-typed name.
 * (Kept separate from norm() so answer matching is unaffected — e.g. a "2.5" answer.)
 */
function nameKey(v) {
  return norm(v).replace(/[.,]/g, '').replace(/\s+/g, ' ').trim();
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
