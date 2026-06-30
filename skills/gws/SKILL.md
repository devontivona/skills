---
name: gws
description: "Run Google Workspace commands (Calendar, Drive, Tasks) as Devon or Sunny via the gws CLI: read/create calendar events, send invites as Devon, manage Drive files and Tasks. Use whenever a task needs Google Calendar/Drive/Tasks, sending a calendar invite, or adding a new Google account/identity. Includes the headless OAuth login recipe and the gws-as identity wrapper."
---

# gws — Google Workspace CLI (Calendar / Drive / Tasks)

`gws` is the official googleworkspace/cli, installed at `~/.local/bin/gws` (static musl
build, Node-independent). It talks to Google Workspace APIs for whichever identity its
config dir is pointed at.

## Two identities — ALWAYS use the wrapper

Never call `gws` bare for account work. Use `gws-as` (at `~/.local/bin/gws-as`, also
bundled here at `scripts/gws-as`):

    gws-as devon <args>   # acts as devon@tivona.me  — Devon's calendar; invites send AS him
    gws-as sunny <args>   # acts as sunny@waywardlane.com — Sunny's own calendar

It just sets `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` (devon → ~/.config/gws-devon,
sunny → ~/.config/gws-sunny) then execs gws. Pick the identity deliberately: a calendar
invite to Devon's guests must go out as **devon**.

## Syntax

    gws-as <who> <service> <resource> [sub-resource] <method> --json '{...}' --params '{...}'

- `--params '{...}'` = URL/query params; `--json '{...}'` = request body (POST/PATCH).
- Output is JSON by default; add `--format table|yaml|csv` for humans.
- `--dry-run` validates locally without calling the API — use before any write/delete.
- Wrap JSON values in single quotes so the shell leaves the inner double-quotes alone.

## Common operations

List calendars:

    gws-as devon calendar calendarList list --format table

Show upcoming events (helper):

    gws-as devon calendar events list --params '{"calendarId":"primary","timeMin":"2026-07-01T00:00:00Z","singleEvents":true,"orderBy":"startTime","maxResults":10}'

Create an event AND send invites (the key use case — sends email to guests):

    gws-as devon calendar events insert --params '{"calendarId":"primary","sendUpdates":"all"}' --json '{
      "summary":"Coffee with Sam",
      "start":{"dateTime":"2026-07-03T10:00:00-07:00"},
      "end":{"dateTime":"2026-07-03T10:30:00-07:00"},
      "attendees":[{"email":"sam@example.com"}]
    }'

`sendUpdates":"all"` is what actually emails the attendees. Omit it and the event is
created silently with no invite. Use `events patch`/`update` (same sendUpdates) to edit.

Drive — list / upload:

    gws-as devon drive files list --params '{"pageSize":10}'
    gws-as devon drive files create --upload /path/to/file.pdf --json '{"name":"file.pdf"}'

Tasks — list task lists / add a task:

    gws-as devon tasks tasklists list
    gws-as devon tasks tasks insert --params '{"tasklist":"<listId>"}' --json '{"title":"Buy diapers"}'

Discover any method's schema:

    gws schema calendar.events.insert --resolve-refs

## Adding a NEW Google account (headless OAuth login recipe)

The box is headless, so the normal localhost-callback browser flow needs a relay through
the user. Recipe (the same one used for both existing accounts):

1. Pick a config dir for the new identity, e.g. `~/.config/gws-<name>`, and drop a
   `client_secret.json` in it (reuse the existing OAuth client — see references below for
   the client_secret.json shape; it includes the desktop client_id/secret + project_id).
2. Background the login so it prints its URL and waits on its callback port:

       GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-<name> \
         nohup bash -c 'gws auth login -s calendar,drive,tasks > /tmp/gwslogin.out 2>&1' & 
       sleep 6 && cat /tmp/gwslogin.out      # grab the printed accounts.google.com URL + its localhost:PORT

3. Send the URL to the user (iPad/no-shell is fine). They sign in as the RIGHT account,
   approve scopes, and land on a "Safari can't connect to localhost" page — that's
   expected on a headless box.
4. They copy the FULL address-bar URL (it contains `&code=4/...`) and paste it back.
5. Complete the flow by curling that redirect against the waiting local port:

       curl -s "http://localhost:PORT/?code=<CODE>&scope=<...>&..."   # the whole pasted query string

   The waiting callback server catches it and finishes the token exchange. Verify:

       gws-as <name> auth status        # has_refresh_token: true
       gws-as <name> calendar calendarList list --format table

GOTCHAS learned:
- Auth codes are ONE-TIME and short-lived. If the bg process already exited (timed out)
  the code is spent — restart the login and send a fresh URL.
- `client_secret.json` MUST include `"project_id"` or `auth status` shows a
  client_config_error (auth still works, but fix it to keep status clean).
- A non-owner account (e.g. sunny@ on Devon's project) needs
  `roles/serviceusage.serviceUsageConsumer` on the project or reads fail with "Caller does
  not have required permission to use project". Grant it as the project owner:
  `gcloud projects add-iam-policy-binding <project> --member="user:<email>" --role="roles/serviceusage.serviceUsageConsumer"` (propagation ~1 min).
- gcloud's OWN headless login (for the project owner) uses a different relay: 
  `mkfifo /tmp/f; (exec 3<>/tmp/f; gcloud auth login <email> --no-launch-browser --update-adc <&3 &)` then write the pasted verification code into the fifo. gcloud is only needed for
  project/API admin, not for gws runtime.

## Scopes & the consent screen

- Scope each login to only what's needed: `gws auth login -s calendar,drive,tasks`. Do NOT
  use the "recommended"/`--full` preset — it requests 85+ scopes and FAILS for @gmail.com
  accounts (Google caps consent at ~25 scopes).
- Project: `sunny-workspace-38323` ("Sunny Workspace"), owned by devon@tivona.me. OAuth
  client is a Desktop-app type. Enable more APIs with
  `gcloud services enable <api>.googleapis.com --project sunny-workspace-38323`.

## Publishing status / token longevity

- In **Testing** mode, refresh tokens expire after ~7 days (because the scopes go beyond
  name/email/profile). If reads suddenly fail with an auth error, the token likely expired —
  re-run the login recipe.
- **Publishing** the app (Cloud Console → APIs & Services → OAuth consent screen →
  Audience → "Publish App", then confirm) removes the 7-day expiry → long-lived tokens.
  This is a MANUAL Console click — no API/gcloud command flips it.
- Publishing does NOT require Google verification and does NOT cost you any scopes: an
  unverified production app still grants full drive/calendar/tasks to the owner's own
  accounts — the only effect is a one-time "Google hasn't verified this app → Advanced →
  Continue" screen at login, plus a 100-user cap (irrelevant here). Skip formal
  verification (it'd need a privacy policy, demo video, and an annual CASA security audit
  for the restricted `drive` scope — overkill for a personal tool).
- After publishing, re-run the login once per account to mint fresh non-expiring tokens.

## References

- `scripts/gws-as` — the identity wrapper (already installed at ~/.local/bin/gws-as).
- Deeper state/history (account list, project, decisions) lives in memory topic:gws.
