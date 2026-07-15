---
name: heartbeat
description: The recurring heartbeat job — every 3h from 9am-9pm, sweep four sources (Sunny's own unarchived email, Devon's unarchived email, Devon's Craft task list, Sunny's memory files) take up to 3 small autonomous actions, and report to Sunny (who relays to Devon) up to 2 things needing his call. Distinct from skill:task-assistant (that's a once-daily, task-list-only, deeper pass) — this is a lighter, higher-frequency pulse across a wider set of inputs. Triggered by the "heartbeat" standing schedule; not normally run ad hoc.
---

# Heartbeat — 3-hourly chief-of-staff pulse

Every 3 hours during Devon's waking hours (9am, 12pm, 3pm, 6pm, 9pm PT), take a quick pass
across four input sources, do a small amount of real work autonomously, and flag anything
that genuinely needs Devon's call — then end with ONE short REPORT. Your report goes to
Devon's conversation loop, where Sunny relays it in its own voice with the live
conversation's context — you are not composing the iMessage itself. Most cycles should
produce little or nothing. Never pad the report to look busy.

## Step 0 — interruption is not your problem anymore

Your report is folded into Devon's conversation by the conversation loop itself, which sees
the live thread and owns the judgment about timing (it can hold, fold, or stay silent if
Devon is mid-exchange). Do NOT poll the thread or wait — just do the pass and report.

## Step 1 — gather the four sources, in this order

1. **Your own unarchived email** (Sunny's inbox, sunny@waywardlane.com) — via `skill:email`.
2. **Devon's unarchived email** — via `skill:email` (check the email skill for the current
   account name/handle for Devon's mailbox; don't hardcode one here since it can change).
3. **Devon's Craft task list** — via `skill:craft`. This is NOT a full task-assistant sweep;
   read `skill:task-assistant` for the bucketing/autonomy logic, in-scope/out-of-scope
   exclusions (Icebox, template docs), and the shared nudge-history file schema — this skill
   inherits all of that rather than restating it. Scope way down from task-assistant's full
   backlog pass: look for 1-2 tasks worth nudging forward this cycle, not the whole list.
4. **Your own memory files** (USER, SUNNY, relevant topic docs) — scan for open loops
   assigned to you: something you said you'd check on, a draft awaiting send, a decision
   someone's waiting on, a promise to follow up. Memory is a source of *reminders*, not a
   place to take fresh action on its own — it mostly feeds Step 2 by resurfacing things.

Don't skip a source because an earlier one already gave you enough material — always look
at all four, then synthesize across them when picking what to surface.

## Step 2 — pick up to 3 autonomous actions + up to 2 discussion items

**Total across all sources: up to 3 things you just DID, up to 2 things you're ASKING
about.** Fewer is fine — often zero and zero. Never stretch to hit the caps.

Per-source autonomy split:

- **Your own email**: autonomous = archiving anything that doesn't matter, and responding
  to a message yourself (then archiving it after). No discussion items originate here —
  it's your inbox, you own the call.
- **Devon's email**: autonomous = drafting a reply (into Drafts, never sending) and doing
  research on a topic raised in an email. Discussion = proposing an email (or a few) to
  archive, suggesting a drafted reply is ready to send, or floating an idea for how to move
  a pending email-borne task forward. Never send an email on Devon's behalf, never archive
  his email without asking first — those are his calls to make, only propose them.
- **Devon's Craft tasks**: follow `skill:task-assistant`'s autonomy line (reversible/
  research/legwork = do it yourself and write findings into the task; anything needing his
  judgment or a one-way door = surface as a discussion item instead). **Share
  task-assistant's anti-nag state file**
  (`~/.sunny/data/task-assistant/history.json`, same schema as documented in
  `skill:task-assistant`) — read it first, and skip any task already marked 2x-nudged
  (per that skill's 2-nudge rule) or already nudged earlier today (check `nudges[].date`
  and today's date) so this job doesn't duplicate a push task-assistant already made or
  already backed off from. If you do nudge a task this cycle, append your own entry to
  that same task's `nudges` list (same shape: `{"date", "angle"}`) and update
  `last_run_seen`/`status` as task-assistant would, then write the file back — this keeps
  nudge history complete across both jobs regardless of which one acted. The two jobs
  never run at overlapping times (task-assistant is 7am only; heartbeat is 9/12/3/6/9), so
  there's no real write-race risk from sharing the file — just read-modify-write like
  task-assistant does.
- **Memory files**: no direct autonomous/discuss actions of their own — they resurface
  candidates that get actioned via one of the three buckets above (e.g. memory reminds you
  a Talbot pass-reply draft is sitting unsent → that becomes a Devon-email discussion item;
  memory reminds you of an unresolved celebration-image choice → that could become its own
  short discussion item, not tied to email or Craft at all).

## Step 3 — compose ONE report, addressed to Sunny

You are reporting to Sunny, who will decide what to tell Devon and say it in Sunny's own
voice inside the live conversation. Report facts, not prose for Devon:

- What you DID this cycle (concrete: "drafted a reply to Debbie, sitting in Devon's drafts").
- What needs DEVON'S call (each phrased so Sunny can ask him in one line).
- Suggested emphasis: which one thing matters most right now, if any.

Skip a category entirely if it's empty rather than writing "nothing on X." Never address
Devon, never write in first person as Sunny — Sunny composes the message. (The old
chief-of-staff voice guidance now applies to SUNNY's relay, not to you.)

**If there is truly nothing — zero autonomous actions taken and zero discussion items after
checking all four sources — respond with exactly `<no-report/>` and nothing else.** A silent
cycle is normal and expected, especially early/late in the day or during quiet stretches.
Never report "nothing new" filler — that's noise five times a day.

## Don'ts

- Don't run a full task-assistant-style sweep of the whole Craft backlog — that's the daily
  job's job. This is 1-2 tasks, lightly touched.
- Don't send Devon's email or archive Devon's email without asking — propose, don't act, on
  anything in his inbox beyond drafting/research.
- Don't repeat a discussion item you already raised earlier today and Devon hasn't acted on
  yet, unless something material changed. Silence on a stale ask is fine.
- Don't pad the message to seem productive. Empty is a valid, common outcome.
