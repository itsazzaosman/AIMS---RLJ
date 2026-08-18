# Email Authentication (OTP) — Work Summary

Summary of the debugging, fixes, and deployment work done on the
`features/email-authentication` branch.

## 1. OTP emails weren't being sent

**Symptom:** the OTP code showed up in the terminal/console logs instead of
arriving in the recipient's inbox.

**Root cause:** `manage.py` loads `src/core/settings.py` by default (not
`dev_settings.py`). That file falls back to Django's console email backend
whenever the `JANEWAY_EMAIL_BACKEND` env var is empty. Two separate bugs
caused it to be empty:

- The `.env` file at the project root was missing several variables
  (`DB_*`, `JANEWAY_PORT`, etc.) that the running Docker container needed,
  so the container was never recreated to pick up the email vars.
- The `Makefile` unconditionally `export`ed `JANEWAY_EMAIL_BACKEND` /
  `_HOST` / `_PORT` / `_USE_TLS` as **empty strings**, even when
  `DEBUG_SMTP` wasn't set. Since Docker Compose treats "shell has this var
  set to empty" as higher priority than `.env`, this silently overrode the
  real SMTP settings on every `make run`.

**Fixes:**
- `Makefile` — moved those `export` lines inside the `ifdef DEBUG_SMTP`
  block, so they're only exported (and only forced to the debug SMTP
  relay) when explicitly opted into.
- `src/core/dev_settings.py` / `src/core/janeway_global_settings.py` —
  reverted hardcoded Gmail credentials back to reading from
  `JANEWAY_EMAIL_*` env vars (their original pattern). The exposed Gmail
  app password was rotated.

## 2. OTP activation link broke on Gmail `+` addresses

**Symptom:** "Invalid email or confirmation code" even when the OTP was
typed correctly, specifically for addresses like `user+test@gmail.com`.

**Root cause:** `core/views.py`'s `register()` view built the activation
redirect URL by string-interpolating the raw email into the query string
without URL-encoding. A literal `+` in a query string decodes as a space,
so `user+test@gmail.com` became `user test@gmail.com` by the time the
activation page read it back — which then didn't match the real account.

**Fix:** use `urlencode()` when building the redirect URL
(`core/views.py`).

## 3. OTP paste didn't work

**Symptom:** pasting a 6-digit code into the OTP boxes only filled the
first box (each `<input maxlength="1">` truncates pasted text to one
character).

**Fix:** added a `paste` event handler in
`templates/admin/core/accounts/activate_account.html` that splits the
clipboard text across the remaining boxes.

## 4. CI

- `.github/workflows/ci.yml` predates this work (added by a teammate,
  originally from upstream Janeway). It was disabled in the GitHub UI
  per request, rather than deleted.
- Along the way, fixed a real bug it caught: `RegistrationForm`'s
  `human_captcha` field was unconditionally required, breaking any test
  (or deployment) that disables captcha via `CAPTCHA_TYPE=None` — this was
  never fully re-fixed to respect that setting; worth revisiting.
- Also fixed `ruff format` failures in `forms.py`, `views.py`, and
  `create_privacy.py`.

## 5. PR #1 merge / revert

PR #1 ("Add OTP-based email account activation") was merged into `master`,
then reverted with `git revert -m 1` (non-destructive — history and the
PR's merged status are both preserved; a new commit undoes its net
changes). Reasoning: work moved to focus on getting this branch properly
hosted/demoed first rather than staying merged into `master` immediately.

**Also found and flagged:** a real OpenSSH private key had been committed
to `master` in a teammate's earlier "Initial Janeway Docker PostgreSQL
deployment" commit, sitting in files literally named
`eval "$(ssh-agent -s)"` / `.pub`. It predates this branch's own history
entirely. **The key owner (`siltanukifilie@gmail.com`) needs to rotate
that key** — this is unresolved as of this summary.

## 6. Render.com deployment

Set up a free-tier deploy so the branch could be demoed without a local
tunnel. New files, all on `features/email-authentication`:

- `render.yaml` — Blueprint: a free web service + free Postgres.
- `dockerfiles/Dockerfile.render` — lean build (skips dev tooling /
  mysqlclient, not needed for this deploy).
- `dockerfiles/render-entrypoint.sh` — on boot: migrate, first-time
  `install_janeway` if no journal exists yet, sync `Press.domain` /
  `Journal.domain` from the `JANEWAY_PRESS_DOMAIN` env var, then start the
  server.

Issues hit and fixed, in order:

1. **`ModuleNotFoundError: foundationform`** — that package is an editable
   git install (`pip install -e`) whose source was cloned into
   `--src /tmp/src`. Render's build and runtime environments don't share
   `/tmp` the way local Docker does, so the cloned source vanished before
   the app ever started. Fixed by pointing `--src` at
   `/vol/janeway/.pip-src` instead (inside the app directory).
2. **Health check timeout** — `render.yaml` had `healthCheckPath: /`,
   which requires a real HTTP 200 from the DB-backed homepage. That can't
   succeed until migrations *and* `install_janeway` both finish, which
   takes several minutes on Janeway's full migration history — longer
   than the HTTP health check's timeout allows. Removed
   `healthCheckPath` so Render falls back to a plain TCP port-open check
   (15 min allowance), which is what the entrypoint actually needs.
3. **Site redirecting to `https://www.example.org`** — `Press.domain`
   (and separately `Journal.domain`) are DB fields, set once by
   `install_janeway` using whatever `JANEWAY_PRESS_DOMAIN` happened to be
   *at that moment*. Changing the env var afterward doesn't retroactively
   fix already-created rows. Fixed by having the entrypoint re-sync both
   fields from the env var unconditionally on every boot.
4. **The sync above kept getting undone** — `render.yaml` had
   `JANEWAY_PRESS_DOMAIN` / `JANEWAY_CSRF_TRUSTED_ORIGINS` as plain
   `value:` entries, which Render silently re-applies from the file on
   every Blueprint sync (i.e. every push) — overwriting the correct value
   set manually in the dashboard, back to the `localhost` placeholder.
   Fixed by marking both `sync: false`, same as the email secrets, so
   Render leaves the dashboard-set value alone across syncs. **Requires
   re-entering the correct domain in the dashboard one more time** after
   this fix, since the value had already been stomped before the fix
   landed.

## 7. Migrated real local data to the Render deploy

The generic `install_janeway --use-defaults` press/journal looked nothing
like the real local "ILPD" journal (name, nav, logo, description — all
DB content, not code). Migrated by:

1. `pg_dump -Fc` the local Postgres database (~22 MB).
2. Connected to Render's Postgres externally, `DROP SCHEMA public CASCADE`
   + recreate, to give `pg_restore` a clean target.
3. `pg_restore --no-owner --no-privileges` the local dump into Render's
   database.

The entrypoint's domain self-heal (see §6.3–6.4) then re-points the
restored `press.localhost` / `localhost` domain values at the real
`onrender.com` hostname automatically on the next boot.

## 8. ngrok tunnel for local demoing

Also used ngrok to expose the local `localhost:8000` instance directly,
as an alternative/supplement to the Render deploy. Same underlying
domain-matching issue as Render: ngrok's random hostname doesn't match
any `Press`/`Journal` domain, so Janeway redirects to the default host.

Fixed per-session using `core.models.DomainAlias` (a non-redirecting
alias mapping the ngrok hostname to the `ilpd` journal directly). Since
ngrok's **free plan has no static/reserved domain** (confirmed via
ngrok's docs — that requires a paid plan), the hostname changes on every
tunnel restart. Wrote `sync_ngrok_domain.sh` (repo root, intentionally
**not committed** — pure local dev convenience) to automate re-pointing
the alias: reads ngrok's local API (`127.0.0.1:4040/api/tunnels`) and
updates the `DomainAlias` in one step. Run it after every ngrok restart.

## Outstanding / worth revisiting

- `human_captcha` in `RegistrationForm` doesn't respect `CAPTCHA_TYPE`
  the way the old `CaptchaForm` mixin did — breaks registration in any
  environment/test that disables captcha.
- PR #1 is currently reverted on `master`; the actual feature work lives
  intact on `features/email-authentication` and in the original PR diff,
  ready to be re-merged once ready.

