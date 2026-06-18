#!/usr/bin/env python3
"""
Lock the solution pages behind a passcode (client-side AES-256-GCM gate).

Usage:  python3 lock_solutions.py <PASSCODE_DEV> <PASSCODE_TEACHER>

For each  weeks/grade4/weekN/solutions_weekN.src.html  (the PLAINTEXT source),
it writes a locked  weeks/grade4/weekN/solutions_weekN.html  — a small passcode
screen whose real content (text + figures) is AES-encrypted. EITHER passcode
unlocks it (the content key is wrapped separately under each).

The passcodes are NEVER stored — only the encrypted blobs are. Keep the
*.src.html files OUT of git (they are plaintext); commit only the locked .html.

Needs the `cryptography` package (pip install cryptography).
"""
import sys, os, json, base64, pathlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ITER = 200_000
GRADE_DIR = pathlib.Path(__file__).parent

def b64(b): return base64.b64encode(b).decode()

def derive(passcode, salt):
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(passcode.encode())

def encrypt(html, passcodes):
    content_key = os.urandom(32)
    iv_c = os.urandom(12)
    ct_c = AESGCM(content_key).encrypt(iv_c, html.encode("utf-8"), None)
    wraps = []
    for pc in passcodes:
        salt, iv = os.urandom(16), os.urandom(12)
        ct = AESGCM(derive(pc, salt)).encrypt(iv, content_key, None)
        wraps.append({"salt": b64(salt), "iv": b64(iv), "ct": b64(ct)})
    return {"iter": ITER, "wraps": wraps, "content": {"iv": b64(iv_c), "ct": b64(ct_c)}}

def verify(blob, passcodes, original):
    """Mirror the browser's decrypt to guarantee every passcode round-trips."""
    for pc in passcodes:
        ok = False
        for w in blob["wraps"]:
            try:
                ck = AESGCM(derive(pc, base64.b64decode(w["salt"]))).decrypt(
                    base64.b64decode(w["iv"]), base64.b64decode(w["ct"]), None)
                html = AESGCM(ck).decrypt(base64.b64decode(blob["content"]["iv"]),
                                          base64.b64decode(blob["content"]["ct"]), None).decode("utf-8")
                if html == original:
                    ok = True; break
            except Exception:
                continue
        if not ok:
            raise SystemExit(f"verify failed for a passcode")
    return True

GATE = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Solutions — locked</title>
<style>
* { box-sizing:border-box; margin:0; padding:0; }
body { font-family:'Segoe UI',system-ui,Arial,sans-serif; background:#f0f4ff; color:#1e293b;
  min-height:100vh; display:flex; align-items:center; justify-content:center; padding:24px; }
.gate { background:#fff; border-radius:18px; box-shadow:0 8px 30px rgba(30,64,175,.18); padding:36px 34px; max-width:420px; width:100%; text-align:center; }
.lock { font-size:46px; }
.gate h1 { font-size:23px; font-weight:900; margin:8px 0 4px; }
.gate p { font-size:14.5px; color:#64748b; margin-bottom:20px; }
form { display:flex; gap:10px; }
input { flex:1; border:2px solid #c7d2fe; border-radius:10px; padding:12px 14px; font-size:18px; text-align:center; letter-spacing:.15em; outline:none; }
input:focus { border-color:#4f46e5; }
button { border:none; background:linear-gradient(135deg,#1d4ed8,#4f46e5); color:#fff; font-weight:800; font-size:15px; border-radius:10px; padding:12px 20px; cursor:pointer; }
button:disabled { opacity:.6; cursor:default; }
.err { color:#b91c1c; font-size:14px; font-weight:600; margin-top:14px; min-height:18px; }
.home { display:inline-block; margin-top:18px; font-size:13px; color:#94a3b8; text-decoration:none; }
.home:hover { color:#4f46e5; }
</style></head>
<body>
<div class="gate">
  <div class="lock">&#128274;</div>
  <h1>Solutions are locked</h1>
  <p>Enter the passcode to see the answers &amp; solutions.</p>
  <form id="f" onsubmit="return doUnlock(event)">
    <input id="pc" type="password" inputmode="numeric" placeholder="Passcode" autocomplete="off" autofocus>
    <button id="go" type="submit">Unlock</button>
  </form>
  <div id="err" class="err"></div>
  <a class="home" href="../../../index.html">&larr; Back to home</a>
</div>
<script>
const DATA = __DATA__;
const b64d = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));
async function unlock(pc) {
  const base = await crypto.subtle.importKey('raw', new TextEncoder().encode(pc), 'PBKDF2', false, ['deriveKey']);
  for (const w of DATA.wraps) {
    try {
      const key = await crypto.subtle.deriveKey(
        { name:'PBKDF2', salt:b64d(w.salt), iterations:DATA.iter, hash:'SHA-256' },
        base, { name:'AES-GCM', length:256 }, false, ['decrypt']);
      const ckRaw = await crypto.subtle.decrypt({ name:'AES-GCM', iv:b64d(w.iv) }, key, b64d(w.ct));
      const ckey = await crypto.subtle.importKey('raw', ckRaw, { name:'AES-GCM' }, false, ['decrypt']);
      const buf = await crypto.subtle.decrypt({ name:'AES-GCM', iv:b64d(DATA.content.iv) }, ckey, b64d(DATA.content.ct));
      return new TextDecoder().decode(buf);
    } catch (e) { /* wrong wrap, try the next */ }
  }
  return null;
}
async function doUnlock(e) {
  e.preventDefault();
  const err = document.getElementById('err'), go = document.getElementById('go');
  err.textContent = ''; go.disabled = true; go.textContent = 'Unlocking…';
  let html = null;
  try { html = await unlock(document.getElementById('pc').value.trim()); } catch (e) {}
  if (html) { document.open(); document.write(html); document.close(); }
  else { err.textContent = 'Wrong passcode — try again.'; go.disabled = false; go.textContent = 'Unlock';
         const i = document.getElementById('pc'); i.value=''; i.focus(); }
  return false;
}
</script>
</body></html>
"""

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    passcodes = sys.argv[1:3]
    srcs = sorted(GRADE_DIR.glob("week*/solutions_week*.src.html"))
    if not srcs:
        print("No *.src.html sources found."); sys.exit(1)
    for s in srcs:
        html = s.read_text()
        blob = encrypt(html, passcodes)
        verify(blob, passcodes, html)
        out = s.with_name(s.name.replace(".src.html", ".html"))
        out.write_text(GATE.replace("__DATA__", json.dumps(blob)))
        print(f"locked {out.relative_to(GRADE_DIR)}  ({len(out.read_text())//1024} KB)")

if __name__ == "__main__":
    main()
