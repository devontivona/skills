---
name: task-assistant
description: Daily personal task-assistant job — investigate and complete/unblock Devon's open personal Craft tasks (Task Inbox + any doc with open tasks, excluding Icebox and Craft's own onboarding/template docs), track per-task nudge history so it never repeats a stale suggestion, and produce a morning iMessage summary. Triggered by a 7am PT standing schedule; also usable ad hoc if Devon asks to check on his personal tasks or task inbox.
---

# Task Assistant — daily personal-task pass

Devon's personal (non-work) backlog lives in Craft as checkbox tasks: the loose items in
**Task Inbox** (`block_taskInbox`), plus a handful that are their own sub-pages with more
detail (e.g. "Order a Galleri blood test and new panels", "Decide on financial advisor").
This job's mandate: each morning, work through that backlog like a competent chief-of-staff
would — do what can be done outright, unblock what needs Devon's judgment by doing the legwork
and writing findings into the task, and leave everything else alone with a light touch.

Read `skill:craft` first for the Craft MCP mechanics (the `craft_mcp.py` helper, task syntax,
block nesting). This skill is the *procedure*; craft is the *plumbing*.

## Scope — what's in, what's out

**In scope**: every incomplete (`[ ]`) task Craft returns from `tasks list --scope all`,
EXCEPT:
- Anything inside the **Icebox** doc (`E807F4C0-26C7-4F73-B568-3D06AC101543`) — Devon
  explicitly deprioritized these. Don't touch, don't discuss, don't even mention them in the
  summary.
- **Any template document** — Craft has a real, first-class "template" doc type (Devon
  authors his own, e.g. a custom daily-note template, not just Craft's built-ins), and the
  MCP exposes it directly: `documents list --location templates` returns exactly the set of
  doc ids that are templates. Fetch that list once per run and exclude any task whose parent
  doc id appears in it — do NOT pattern-match on titles ("daily note", "Craft Handbook", etc.);
  that's fragile and will miss a template Devon names something else. Recurring habit-checklist
  items ("Sleep for or at least 7h", "*List tasks here*", etc.) fall out of scope automatically
  once their template parent is excluded this way.
- Already-completed (`[x]`) tasks, obviously — `tasks list` with incomplete-only filtering
  handles this, but double check when reading a doc's raw content.

**Explicitly IN scope, not excluded**: the **Sunny** doc (`6C06B91B-38A8-4268-94F4-CD89C6F8D6F3`)
— Devon's own bug reports/ideas for Sunny itself (e.g. "Fix bug: when a job is killed by Sunny,
it is still reflected on the dashboard as running"). These are fair game and genuinely fun: for
a well-scoped code bug/feature with a clear repro, delegate a `coding`-skill subagent to
investigate and — if a fix is actually reachable — open a PR against Sunny's own repo (branch +
PR only, **never merge**; a PR is reversible, a merge to main is not). For fuzzier ones
("Research best web-search tool for agents"), treat it like any other research-unblock task:
gather findings, write them into the task.

## Per-task bucketing (do this for every in-scope task, every run)

1. **Fully completable now** (you have what you need, no missing judgment call) → do the real
   underlying thing AND mark the Craft task done (`tasks update --state done`), with a one-line
   note of what you did either in the task's own note/child block or just in the run summary.
   Example: Devon decided on a financial advisor elsewhere in conversation → mark "Decide on
   financial advisor" done, note the decision + link to the decision memo.

   **CRITICAL gotcha (see skill:craft for the full writeup, hit for real 2026-07-12): marking
   a task done HIDES it — and any open sub-tasks nested under it — from every view in Devon's
   UI.** Before marking anything done, make sure the ENTIRE task is actually resolved, not
   just the part you happened to check. A task title can silently cover more than one
   sub-thing (e.g. "Check on my HSA transfer" turned out to mean two separate HSA transfers,
   not one) — if there's any chance a task has multiple parts, ask or dig further before
   closing it, and if a task already has child content, read it first to confirm nothing in
   there is still open. When genuinely unsure, leave the parent open with a status note
   rather than guessing it closed.

2. **Unblockable via research/legwork, but the actual call is Devon's** → do the digging
   (web search, email search, Craft/HA lookups, price/vendor research, log investigation) and
   write findings **into the task's body** as a nested note (see "Writing into a task" below).
   Leave the checkbox unchecked. This is the single most valuable bucket — it's where "I already
   did the annoying part, you just need to pick" lives.

3. **Needs a human action only Devon can take** (a phone call only he can make, a decision with
   no research left to do, something requiring his physical presence) → leave it alone. Just
   track its age (see staleness below) — don't manufacture busywork.

## Autonomy line — what you can just DO vs. what you propose

Devon's rule: **anything reversible, do it. Any one-way door, default to him.**

Do outright (reversible, information-gathering, or trivially undoable):
- Web/email research, price/vendor shortlists, log/history investigation (HA, email, Craft).
- Checking a status (an HSA transfer, a shipment, an account state).
- Drafting an email into Drafts (never sending) or a Craft note.
- Adding a calendar event/hold that's easy to delete (e.g. "put X on the calendar" tasks).
- Opening a PR against Sunny's own repo (a branch, not a merge).
- Marking a Craft task done when the underlying real thing is genuinely finished.

Always propose instead of doing (one-way doors):
- Spending money, booking something non-refundable, sending an email that commits Devon to
  something, merging a PR, deleting/canceling something that isn't trivially reversible.
- Anything where you're not sure which side of the line it's on — ask, don't guess.

## Writing into a task (Craft mechanics)

For a task that already has its own sub-page, add findings as normal content on that page
(`blocks add --id <pageId> --markdown "..." --position end`).

For a loose checklist-line task (no sub-page yet), use the exact same call —
`blocks add --id <taskBlockId> --markdown "..." --position end`. Craft auto-promotes a plain
task block into a page the moment you add child content to it (verified directly: `type`
flips from `text` to `page` and the new content becomes its child), which is exactly what the
Craft UI does when a human adds detail to a task. Don't hand-roll a nested-bullet-via-sibling
workaround — this is the native mechanism and matches what Devon sees if he opens the task
himself. Prefix the note so it's clearly Sunny's addition, e.g.
`🤖 Sunny (YYYY-MM-DD): <finding>`.

## Per-task state — the anti-nagging memory

State lives OUTSIDE Craft, in `~/.sunny/data/task-assistant/history.json` (this repo's state
dir, not a Craft doc — Devon confirmed the iMessage summary is the audit trail, no Craft log
needed). Schema: a dict keyed by Craft task block id (stable across runs):

```json
{
  "<taskBlockId>": {
    "title": "short cached label, for readability when debugging the file",
    "first_seen": "YYYY-MM-DD",
    "last_run_seen": "YYYY-MM-DD",
    "nudges": [
      {"date": "YYYY-MM-DD", "angle": "one-line description of what was suggested/done"}
    ],
    "status": "open | unblocked_pending_devon | done | needs_devon_action"
  }
}
```

Rules for using it:
- **Load it at the start of every run, save it at the end.** If it doesn't exist yet, create it
  empty — this is the first run.
- Before writing a new nudge/suggestion for a task, check `nudges` for that task. If you've
  already suggested angle X and Devon hasn't acted (task still open, unchanged), do NOT repeat
  X verbatim. Either find a genuinely different angle (different vendor, different framing,
  new information since last time) or, after **2 unsuccessful nudges**, go quiet on it — it
  still shows up in the task list contextually, just without a repeated push. Only bring it up
  again unprompted if something material changed (new info, approaching deadline, etc.).
- **Staleness thresholds** (based on how long a task has sat untouched — use `first_seen` or
  the task's own `schedule` date, whichever is more meaningful):
  - **14+ days untouched** → worth a mention in the summary (not a nag, just a visibility note).
  - **30+ days untouched** → worth one stronger flag, then drop back to passive visibility
    (per the 2-nudge rule above).
- Overdue-but-scheduled tasks (schedule date has passed) → suggest Devon reschedule it (never
  reschedule it yourself — rescheduling is a judgment call about priority, not a research task).

## The daily run procedure

1. Load `~/.sunny/data/task-assistant/history.json` (or start fresh).
2. `craft__craft_read` → `documents list --location templates`, collect the set of template
   doc ids. Also confirm the Icebox doc id.
3. `craft__craft_read` → `tasks list --scope all`. Drop any task whose parent doc id is in the
   template set or is the Icebox doc; drop already-completed tasks.
4. For each remaining in-scope open task: bucket it (see above), take action per the autonomy
   line, and update its history entry.
5. Write the updated history file back.
6. Compose the morning message — see format below — and send it via `send_message` (this job
   is triggered by a schedule delivering to Devon directly, so just reply normally when it fires).

## Message format

Three short parts, iMessage-appropriate (concise, plain text, no markdown headers):

**(a) What I did** — 1-4 bullets of real completed/unblocked work from this run. Skip this
section entirely if nothing happened (e.g. everything's already been nudged out or is waiting
on Devon). Be concrete: "Booked nothing, but shortlisted 3 hotels for Shannon & Austin's wedding
weekend — [link/names] — want me to hold one?" beats "worked on hotel task."

**(b) Open questions** — anything genuinely blocking further progress that only Devon can
answer, phrased so a one-word reply unblocks more work. Skip if none. Cap at ~3 — don't dump
the whole backlog as questions.

**(c) Today's suggested priorities** — acknowledging workday reality: frame as "if you get 10-15
min tonight or tomorrow morning" rather than a full task list. Usually 1-2 items, picked from:
tasks nearing/at staleness thresholds, overdue-and-unactioned items, or anything you unblocked
this run that's now trivial for him to finish. Never repeat an already-2x-nudged item here.

Keep the whole message to a few short texts, per Sunny's general iMessage style — this is a
digest, not a status report dump.

## Don'ts

- Don't touch Icebox. Don't even reference it exists in the summary.
- Don't nag — see the 2-nudge rule. Silence on a task is fine; repeating yourself isn't.
- Don't make one-way-door moves autonomously (spend money, send a commit-you email, merge code,
  cancel/delete something non-trivial to undo).
- Don't invent completions — only mark a Craft task done when the real underlying thing is
  actually finished, not just "researched."
