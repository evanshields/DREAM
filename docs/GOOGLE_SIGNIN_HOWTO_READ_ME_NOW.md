# DREAM — How to fix Google Sign-In (plain English, do this yourself)

**For:** Evan · **Date:** 2026-06-09 · **Time needed:** ~5 minutes of clicking

This guide is for the ONE thing only you can do: telling Google that the 5 Shieldstone people
are allowed to sign in. Everything else (the code that was rejecting Google logins) I've already
fixed — see the "What I already handled" note at the bottom.

---

## The short version

Your DREAM app uses "Sign in with Google." Right now Google treats your app as a **Test app**
(not yet publicly approved). A Test app **only lets people sign in if you've added them to an
allow-list inside Google's settings.** Nobody is on that list yet, so every Google login is
blocked by Google before it even reaches your app.

**Your job:** add 5 email addresses as "Test users" in the Google Cloud console. That's it.

---

## Step-by-step (with what each screen looks like)

### 1. Open the Google Cloud Console
- Go to **https://console.cloud.google.com**
- Sign in with **evan@shieldstone.co** (the account that owns the DREAM Google project).
  - If you land in the wrong project, click the project name in the very top bar (next to
    "Google Cloud") and pick the DREAM / Shieldstone project. The right project contains an
    OAuth client whose ID starts with **`954847212741-...`**.

### 2. Go to the OAuth consent screen
- In the search bar at the top, type **`OAuth consent screen`** and click the result.
  (Or: left menu ☰ → **APIs & Services** → **OAuth consent screen**.)

### 3. Confirm it says "Testing"
- Near the top you'll see a **Publishing status**. It should say **Testing**.
  (If it says "In production," Google already lets anyone in your domain sign in and you can
  skip to "How to test it" below — but it almost certainly says Testing.)

### 4. Add the 5 Test users
- Scroll down to the **Test users** section.
- Click **+ ADD USERS**.
- Paste these 5 addresses, **one per line**:

  ```
  evan@shieldstone.co
  fahd@shieldstone.co
  alton@shieldstone.co
  chuck@shieldstone.co
  charles@gatewaymb.co
  ```

  (Charles uses a non-Shieldstone Google address — that's fine, Google Sign-In works with any
  Google account, and our app's allow-list already includes him.)
- Click **SAVE**.

### 5. Wait a few minutes
- Google can take **5–15 minutes** to apply the change. If a login fails right after saving,
  wait and try again.

**You're done.** There is nothing else to configure on Google's side.

---

## How to test it (after the deploy + a few minutes' wait)

> ⚠️ Google login will only work once I (or the next Claude session) **deploy the code fix** to the
> live server. Until then, even with Test users added, Google logins still fail — see the note
> below. If I've already deployed by the time you read this, you can test now.

1. Go to **https://dream.shieldstone.co** in a browser.
2. Click **Sign in with Google** (note: a login button may still need to be built into the
   website — see "Heads up" below).
3. Pick one of the 5 allow-listed Google accounts.
4. You should land in the app. If Google shows a scary "**This app isn't verified**" screen,
   that's normal for a Testing app — click **Advanced → Go to DREAM (unsafe)**. It's your own
   app; it's safe.

If you get **"Error 403: access_denied"** → that email isn't in the Test users list (re-check
spelling) or Google hasn't finished applying the change yet (wait longer).

---

## If you'd rather just unblock Google login RIGHT NOW, before the deploy

There's a faster manual option, but it has a trade-off. The live server has a setting called
`AUTH_JWT_SECRET` that powers the temporary **username/password** login I set up for you. The OLD
code on the server has a bug: while that setting is present, it accidentally rejects Google logins.

- **If you don't need the username/password login anymore** and just want Google working: the
  next Claude session can remove that one setting and restart the server (~1 minute). Google then
  works on the old code immediately. **But your username/password login stops working.**
- **The better fix** (which I've prepared and which keeps BOTH login methods working) is to deploy
  the new code. That's the recommended path and it's already staged.

You don't have to act on this section — it's just so you understand the two settings interact.
The clean answer is "add the 5 Test users (above) + let the deploy happen."

---

## Heads up — two things that still need building (not your job, just FYI)

1. **The website may not have a Google "Sign in" button yet.** The behind-the-scenes login
   machinery is done and tested, but the actual button on the page is a separate piece of work
   that's on the to-do list. Until it exists, login happens via a developer tool, not a click.
2. **The username/password login I made for you DOES work today** (I tested it live). Your
   password is in our earlier chat — please move it into your password manager; it's stored
   nowhere else.

---

## What I already handled (so you know the boundary of your task)

- **The code bug** that made Google logins fail whenever the password-login setting was present:
  **fixed** (the app now decides "is this a Google token or one of ours?" the correct way).
- **Securing the app's internal endpoints** (they were briefly open to the public internet):
  **fixed** — everything now requires a login.
- **Pinning the login allow-list** to those exact 5 emails: **already configured** on the server.

Your only manual step is adding the 5 Test users in Google (Steps 1–5 above). Everything else is
code/server work handled on my side.

---

### Quick reference
- **Console:** https://console.cloud.google.com → OAuth consent screen → Test users
- **OAuth Client ID:** `954847212741-g00fssf9sa9mvglus6b61cc61pt3f7hj.apps.googleusercontent.com`
- **The 5 emails:** evan@ / fahd@ / alton@ / chuck@ (all @shieldstone.co) + charles@gatewaymb.co
- **Live app:** https://dream.shieldstone.co
- **Security to-do for you:** rotate the Google "Client Secret" and the Kimi API key when you get
  a chance (both passed through chat today), and save your DREAM username/password in a manager.
