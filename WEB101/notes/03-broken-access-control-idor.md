# 03: Broken access control and IDOR (A01)
Time: ~35 min
Mapping: OWASP A01:2021 Broken Access Control, MITRE ATT&CK T1190

## Why it matters

Broken access control is the number one risk on the OWASP Top 10, and it is the most common serious bug in real bug bounty programs. The idea is simple: the app checks *who you are* (authentication) but not *whether you are allowed to touch this specific thing* (authorization). When those come apart, a logged-in low-privilege user can read or change data that belongs to someone else. Flag 1 in this lab is the cleanest version of this, an Insecure Direct Object Reference (IDOR), and once you see it you will see it everywhere.

## How it works

NorthWind Notes selects a note by a number in the URL: `/note?id=1`. When alice clicks her note, the browser sends `id=1`, and the app returns note 1. The app knows alice is logged in (her cookie is valid). What it fails to do, at `LEVEL=1`, is check that note 1 *belongs to* alice before returning it.

So the attack is to ask for a number you were not given. `id=2` belongs to admin. Alice is authenticated, the app sees a valid session, it looks up note 2, and it hands it over, flag and all. Nothing was bypassed. The app did exactly what it was told, because the only missing line of code is "is this note yours?".

This is the shape of every IDOR:

1. The app exposes a **direct reference** to an object: a database id, a filename, an account number, a document uuid, in a URL, form field, or JSON body.
2. The app **authenticates** the request (you are a valid user).
3. The app **does not authorize** the specific object (it never checks the object is yours).
4. You **change the reference** to one you should not have, and the app serves it.

Why developers get this wrong: the id is already in the URL because the app put it there for legitimate use, and in testing every user only ever clicks their own links, so the missing check is invisible until someone edits the URL. The browser never shows alice a link to note 2, so the developer feels it is hidden. It is not hidden; it is one keystroke away.

Where to look for IDOR on any target:

- Numeric ids you can increment or decrement (`id=1` to `id=2`). Sequential ids make it trivial.
- Ids in `POST` bodies and JSON, not just URLs. Tampering is the same; you just edit the body.
- Non-numeric references too: filenames, emails, uuids. Uuids are harder to guess but still an IDOR if the check is missing and you can obtain one.
- Every verb, not just read. The same missing check often lets you *edit* or *delete* other people's objects, which is more severe than reading.

Severity depends on what the object is and what you can do to it. Reading another user's note is a confidentiality breach. If the same bug let you change admin's note, or read every user's note by walking ids, it climbs toward critical. Always test whether the bug scales (can you enumerate all ids?) and whether it extends to writes.

The fix, which you will see at `LEVEL=2`, is one check in the right place: before returning the object, confirm it belongs to the current user (or that the user's role permits it). In the lab the `owns()` function enforces exactly that when `LEVEL=2`, and the attack returns `403`.

## Try it in the lab

1. Sign in as alice and open your own note. Note the URL: `/note?id=1`.
2. Change the number. Request `id=2`:
   ```
   curl -H 'Cookie: sid=YOUR_SID' 'http://127.0.0.1:8080/note?id=2'
   ```
   Read the body. Note 2 is admin's, and it contains Flag 1. Verify it with `check_flag.py`.
3. Test whether it scales: try `id=3`, `id=4`, `id=0`, a negative number, a non-number. Note which return data, which `404`, which error. This is how you measure impact.
4. Switch to `LEVEL=2`, restart, and repeat step 2. You should now get `403`. That one check is the whole fix. Record both results for your writeup.

## Key takeaways

- Broken access control is authentication without authorization: the app knows who you are but not whether you may touch this object.
- An IDOR is a direct object reference (id, filename, uuid) plus a missing ownership check; you exploit it by changing the reference.
- Look in URLs, form fields and JSON bodies, across every verb, and test whether it scales to all objects and to writes, not just one read.
- The fix is one authorization check on the specific object, enforced server-side (seen at `LEVEL=2`).

## Further reading

- OWASP Top 10 A01:2021, Broken Access Control: https://owasp.org/Top10/A01_2021-Broken_Access_Control/
- OWASP WSTG, Testing for IDOR: https://owasp.org/www-project-web-security-testing-guide/stable/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References
- PortSwigger Web Security Academy, Access control vulnerabilities: https://portswigger.net/web-security/access-control
