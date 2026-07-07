---
name: craft
description: Read, write, search, and organize Devon's Craft.do space via its MCP server (saved links, daily notes, tasks, kanban collections). Use whenever a task involves Craft, Craft documents, tagging saved links with #resources/ tags, journaling in Craft, the Craft-as-second-brain workflow, or Devon's task list ("what are my tasks", "add X to my tasks", "remind me to..." as a save-for-later item rather than a scheduled job). Includes the daily resource-tagging + description + title-cleanup job and Craft Tasks as Devon's task-management hub.
---

# Craft.do integration

Devon's personal "second brain" lives in Craft (craft.do). Sunny reaches it via Craft's
MCP server (a Cloudflare-fronted HTTP JSON-RPC endpoint, OAuth-authed, scoped to one
specific Craft space per link). See `topic:craft` for space inventory/state.

## Connection

- Config: `~/.sunny/mcp.json` entry `"craft"`. Token file: `~/.sunny/mcp-oauth/craft.json`.
- Helper library: `scripts/craft_mcp.py` in this skill dir. Handles the JSON-RPC
  handshake, session id, and **automatic token refresh** (Craft access tokens are
  short-lived, ~1hr). Use it instead of hand-rolling requests:

```python
import sys
sys.path.insert(0, "~/.sunny/skills/authored/skills/craft/scripts")  # expand ~ first
import craft_mcp
craft_mcp.read("documents list --location unsorted")
craft_mcp.read("search --include #resources")
craft_mcp.write('blocks add --id 300949c6-caa9-4761-0c47-ac681822fff6 --markdown "#resources/repos #sunny" --position end')
```

Or from bash:
```
python3 ~/.sunny/skills/authored/skills/craft/scripts/craft_mcp.py read "folders list"
python3 ~/.sunny/skills/authored/skills/craft/scripts/craft_mcp.py write "blocks add --id ABC --markdown \"#resources/repos #sunny\" --position end"
```

**Gotcha**: Craft's endpoints reject requests without a real browser User-Agent
(Cloudflare bot detection → 403 "browser_signature_banned"). `craft_mcp.py` already
sends one; don't strip it if you ever hand-roll a request.

- **Reading a linked page's real content is a separate, general-purpose skill:
  `skill:web-fetch`.** Read that skill for the full extraction strategy (trafilatura
  → optional Firecrawl fallback for JS-rendered pages → meta-tag fallback), setup,
  and gotchas — don't duplicate that logic here. In short:

```python
import sys
sys.path.insert(0, "~/.sunny/skills/authored/skills/web-fetch/scripts")  # expand ~ first
import fetch
result, err = fetch.fetch_text(url)
```

  Used by the resource-tagging job to actually READ a linked page before judging/
  describing it — **never infer a resource's subject from its URL or title alone.**
  `err` is set on hard failure (404, timeout, non-HTML, blocked) — fall back to
  whatever content/blurb is already saved on the Craft page itself in that case, and
  note the fetch failure in the run summary. `result["degraded"]` is True when the
  page was likely JS-rendered and only a thin meta-description fallback was
  available — treat that as lower-confidence input, and say so if the resulting
  description ends up thin rather than presenting it with full confidence.

## Tools exposed (`craft_read` / `craft_write`)

Your toolset may also carry these natively as `craft__craft_read` / `craft__craft_write`
(live MCP tools — present in owner-DM turns and host-endowed runs). Both paths hit the same
server; the `craft_mcp.py` helper over bash is the documented, battle-tested path for the
procedures below (it handles the Cloudflare quirk) — prefer it for jobs, and don't mix paths
mid-procedure.

Both take a single `command` string argument (shell-like syntax, `--flag value`).
Batch multiple commands with semicolons. Full command reference:

**craft_read**: `folders list`, `documents list [--location unsorted|trash|templates|daily_notes]`,
`documents resolve-link <url>`, `tasks list [--scope ...]`, `blocks get <rootBlockId>
[--format markdown|json] [--depth n]`, `collections list/schema/items-get/views-list`,
`search [--include <term>] [--location ...] [--cursor ...]`, `connection info`.

**craft_write**: `folders create`, `documents create/move/delete`, `tasks add/update/delete`,
`blocks add --id <pageId> --markdown <text> --position start|end` (or `--siblingId
<blockId> --position before|after`), `blocks update --id <blockId> --markdown <text>`
(retitle a page: update its root `page`-type block's markdown — this changes ONLY the
title/heading text, not its content children, which are separate blocks with their own
ids), `collections create/rename/items-add/items-update/items-delete/views-create`.

Append `--help` to any subcommand for its full flag list. There is no `documents
rename` — renaming a document means `blocks update`-ing its root page block's markdown.

## Space inventory (as of 2026-07-06)

Devon has **two Craft spaces**: his personal "Devon's Space" (the one this MCP link
covers) and "Wayward Lane" (shared with Kate — **not yet connected**; needs its own MCP
link generated from inside that space in Craft's UI, then added as a second entry in
`~/.sunny/mcp.json`, e.g. `craft-wayward`).

Devon's Space had, as of the last full read: 155 documents, ~145 in "unsorted" (no
folder structure), 9 daily notes (gappy), 15 stale tasks.

## Task management — Craft Tasks is Devon's task hub (set 2026-07-06)

Devon uses **Craft's own Tasks feature** as his real task list — not a separate todo
app, not a Craft doc full of checkboxes as a workaround. When Devon (or Sunny, e.g.
noticing something he mentioned wants doing later) wants to save something to come
back to, it goes into Craft Tasks via `tasks add`/`tasks update`/`tasks delete`, not
into memory, not into a scratch doc.

**Do not confuse this with `schedule_create`.** They solve different problems:
- **Craft Tasks** = a human-facing todo/reminder list — "things Devon wants to do or
  decide," surfaced to him in Craft's UI, that HE (or Sunny, when asked) will act on.
  Nothing about adding a Craft task causes Sunny to autonomously do anything later.
- **`schedule_create`** = Sunny's own mechanism for *actually performing work later*
  (a one-time reminder-to-self, a recurring job like the daily resource-tagger). This
  is Sunny's execution scheduler, not a place to jot down Devon's personal to-dos.

If a request is "save this for later, I'll get to it" → Craft Tasks. If a request is
"have you actually go do/check this at a later time" → `schedule_create`. Some things
are both (e.g. "remind me tomorrow to call the vet" could be a Craft task with a
schedule date that Devon sees in his UI, OR a Sunny schedule that pings him — ask if
ambiguous which is meant).

### Reading tasks — always filter out template tasks

`tasks list --scope all` (or any other scope) returns EVERY task block in the space,
including ones that live inside **template documents** — e.g. Craft's built-in "Daily
note" template ships with habit-tracker checkboxes (sleep, water, exercise, dinner,
reflection, "*List tasks here*") baked in as a template default. Those are not real
tasks; a template renders them into new documents every day but they are the
template's own scaffolding, not something Devon added.

**Before showing Devon any task list, filter out anything whose `in: <docId>` matches
a document living in Craft's `templates` location:**

```python
# 1. Get template doc IDs
templates = craft_mcp.read("documents list --location templates")
# 2. Get tasks
tasks = craft_mcp.read("tasks list --scope active")  # or whatever scope
# 3. Drop any task whose "in: <docId>" matches a template doc's rootBlockId
```

As of 2026-07-06 there's one template: **"Daily note"**
(`5549A459-269D-41E5-9B20-D8AEAE691DEB`) — but re-check `documents list --location
templates` each time rather than hardcoding this id, in case Devon adds more
templates later. This filtering isn't something Craft's task API does natively (a
task record doesn't self-flag "I'm in a template") — it's a cheap cross-reference
Sunny should always do before presenting a task list, not a one-off fix.

### Commands

`tasks list [--scope active|upcoming|inbox|logbook|document|all] [--document
<rootBlockId>]` — scopes: `active` (open, due today-or-earlier), `upcoming` (open, due
tomorrow-or-later), `inbox`, `logbook` (done/canceled), `document`, `all` (every task
block space-wide, not a union of the others).

`tasks add --markdown <text> [--location inbox|dailyNote|document] [--schedule
<date>] [--deadline <date>] [--state todo|done|canceled] [--repeat <shorthand|json>]`
— defaults to the inbox if no `--location` given (a sensible default for "add this to
my tasks" with no other context). `--repeat` supports shorthand like `weekly:mon,wed`
or `flexible:weekly:fri` (relative to completion) — see `tasks add --help` for the
full JSON form. For adding many at once, `--tasks '<json array>'` is faster than
looping single adds.

`tasks update --task <taskId> [--markdown <text>] [--state todo|done|canceled]
[--schedule <date>] [--deadline <date>] [--location ...] [--repeat <json>]
[--no-repeat]` — marking `--state done`/`canceled` auto-moves the task to the logbook.

`tasks delete --task <taskId>` — permanent; prefer `--state canceled` if the intent is
just "no longer relevant" rather than "never happened."

## Tag taxonomy rules (set by Devon, 2026-07-06 — read carefully)

- **Devon does NOT use Craft as a "read it later" app.** `#resources/reads` and
  `#resources/watch` are **deprecated — never apply them.** If he saved a news
  article, he saved it to capture *what it's about*, not to read it later. Tag by
  **subject**, the same as anything else: a Verge article about a new calculator
  gadget is `#resources/gadgets`, not `#resources/reads`.
- If you encounter an EXISTING document already tagged `#resources/reads` or
  `#resources/watch`, that tag is wrong and should be corrected: read the doc's
  content (fetch the link if needed) and replace the deprecated tag with the right
  subject-based tag(s), via `blocks update --id <tagBlockId> --markdown "<corrected
  tags>"` on that specific tag block (find its block id from `blocks get ...
  --format json`). This is a narrow, deliberate exception to the "append only, never
  edit" rule below — it applies ONLY to fixing a deprecated tag on its own block, never
  to any other content.
- **Multiple tags per resource are normal and encouraged**, not exceptional. In
  particular: most coding-related saves these days are also AI-related, so tag both
  `#resources/repos` AND `#resources/ai` when a repo/tool is AI-related (which is most
  of them) — don't force a single-tag pick when two genuinely apply.
- Known-good existing categories (reuse before inventing): `repos`, `ai`, `makers`,
  `landscapers`, `clothing`, `home`, `dnd`, `art`, `games`. Invent a new lowercase
  short-compound category (e.g. `gadgets`) when a resource's actual subject doesn't fit
  any existing one — this is expected and fine, especially for news/article subjects
  now that `reads`/`watch` are gone.
- Other unrelated tag families exist too (`#gifts/*`, `#pdx`) — don't confuse those
  with the resources taxonomy, don't touch them.

## The `#sunny` marker tag — how "already processed" is tracked

Every document the job evaluates gets a **`#sunny`** tag added (alongside whatever
`#resources/*` tags apply, or alone if the doc isn't a resource at all). This is the
authoritative "AI has already looked at this document" signal — visible to Devon in
Craft, and durable even if the local state-file cache is lost or reset (see Job
procedure below). **A document that already contains `#sunny` in its content should
never be re-evaluated** — that's the actual skip condition, checked by reading each
candidate's content, not by trusting a local file alone.

Because this signal didn't exist before 2026-07-06, the **first several runs of this
job function as a backfill pass**: every existing `#resources/*`-tagged document from
before this date lacks `#sunny` and a description, so it will legitimately get
reprocessed once (to add a description, fix deprecated `reads`/`watch` tags if present,
and get its `#sunny` marker) even though it was "already tagged." This is expected and
desired, not a bug — don't skip already-tagged docs just because they have a
`#resources/*` tag; only skip on `#sunny` presence.

## Job: daily resource-tagging + description + title cleanup

**Goal**: for every Craft document (in `unsorted`; daily notes are out of scope — see
Notes) that doesn't yet carry `#sunny`, actually read its linked content, then: decide
if it's a genuine single-topic saved resource; if so, tag it (multiple tags allowed,
reusing existing categories, fixing any deprecated tag found), write a short 3-4
sentence description onto the page (for future search/findability), and clean up its
title if it's obviously raw browser-clip cruft. Mark every reviewed doc `#sunny`
either way. Runs daily via a schedule AND is safe to run ad-hoc as a one-off/test.

### Procedure

1. **Load current tag taxonomy**: `search --include #resources` — collect every
   distinct `#resources/<category>` string seen (excluding the deprecated `reads`/
   `watch`, which should never be reapplied even if seen). This is the reuse-first
   candidate set for step 5.
2. **Load state**: read `~/.sunny/state/craft-resource-tagger.json` (JSON:
   `{"processed": ["<rootBlockId>", ...]}`). Create it (`{"processed": []}`) if
   missing. This is a **performance cache only** — it lets you skip re-fetching docs
   you already know are done without re-checking Craft every time. It is NOT the
   source of truth (see `#sunny` section above): if this file is ever lost/reset, the
   job self-heals because every doc's own content is checked for `#sunny` before
   any write happens, so nothing gets double-tagged even after a full state loss.
3. **List candidates**: `documents list --location unsorted`, paginating until
   exhausted. Skip any `rootBlockId` already in the state file's `processed` list
   (fast path); everything else is a candidate to actually check.
4. **Per candidate** (cap per run — 20 for a test run, ~50 for a normal daily run;
   leftovers just roll into the next run since they're still uncached):
   - `blocks get <rootBlockId> --format markdown` (or `--format json` if you need
     block ids, e.g. to fix a deprecated tag). **If the content already contains
     `#sunny`, stop here — add to processed cache and move on. Do not re-tag, re-
     describe, or re-title.**
   - Otherwise, find the actual external link in the doc (usually a `richUrl` block
     near the top) and **fetch it via `skill:web-fetch`** (see the Connection section
     above) to read the real page content — do not judge, tag, or describe from the
     URL/title alone. If the fetch fails, fall back to whatever text/blurb is already
     saved in the Craft doc itself, and note the failure in your summary.
   - Decide if it's a genuine single-topic saved resource (one link, one subject —
     a repo, article, product, tool, business, etc.) versus something that should be
     marked done without a resource tag: personal notes, reflections, checklists,
     business/vendor correspondence, journal-style writing, or anything with
     substantial original prose that isn't really "a thing bookmarked for later."
   - **If it's a resource:**
     a. Pick ALL genuinely-applicable existing `#resources/<category>` tags (plural
        is normal — e.g. an AI coding tool gets both `repos` and `ai`). Invent a new
        subject-based category only if nothing existing fits.
        If the doc currently has a deprecated `#resources/reads` or `#resources/watch`
        tag, replace it (see the tag-taxonomy section above for the mechanism).
     b. Write a **3-4 sentence description** of what the resource actually is, based
        on the fetched page content — written for future search/findability, not
        marketing copy. Insert it as a new block near the top of the page
        (`--position start`) so it's immediately visible and gets picked up by
        Craft's search on the document.
     c. If the document's title is obviously raw browser-clip cruft (e.g. trailing
        `· GitHub` / `- The Verge` / a long tag-soup title rather than a clean name),
        clean it up to just the resource's actual name via `blocks update --id
        <rootBlockId> --markdown "<Clean Title>"` on the page's root block. **Test
        this on the first doc of a run and confirm with a follow-up `blocks get`
        that only the title changed and the content children are intact before
        relying on it for the rest of the batch.** Leave titles alone if they're
        already reasonably clean.
     d. Append a final tag block: all applicable `#resources/<category>` tags plus
        `#sunny` in one block, e.g. `#resources/repos #resources/ai #sunny`
        (`--position end`).
   - **If it's not a resource:** just append `#sunny` alone (`--position end`) so
     it's marked reviewed and never re-nagged. Don't invent a tag for it.
   - Add the doc's `rootBlockId` to the state file's `processed` cache either way and
     persist the file every few docs (so a crash/timeout mid-run doesn't lose
     progress on the fast-path cache — though as noted, correctness doesn't depend
     on this file surviving).
5. **Summarize**: end the run with a concise plain-text digest — how many docs were
   tagged as resources (doc title → tags applied), how many were reviewed and marked
   done as non-resources, whether any new tag category was invented (and why), how
   many deprecated `reads`/`watch` tags were found and corrected, how many titles were
   cleaned up, any fetch failures encountered, and how many untouched candidates
   remain in the backlog if the cap was hit.

### Notes / gotchas

- Craft's search is keyword/substring only (no semantic search) — don't rely on
  `search` alone to find "everything that might be a resource"; the per-document
  content check (and now, the actual URL fetch) in step 4 is the real filter.
- **Craft's search is also not exhaustive/reliable for counting/auditing purposes**
  (confirmed 2026-07-06): `search --include #sunny` returned only 14 documents when
  spot-checking individual docs (via direct `blocks get`) showed at least one
  confirmed-tagged doc missing from those results entirely (correct `#sunny` and
  `#resources/*` tags present in its actual content, zero results for it in search).
  **Never trust a `search` count as a real count of anything** — always verify
  specific documents via `blocks get <rootBlockId>` directly when you need ground
  truth, and treat the local state-file cache (`~/.sunny/state/craft-resource-
  tagger.json`) as the more reliable fast-path signal for "have I already touched
  this doc," not search.
- Tag and description blocks are always **added**, never used to edit/replace
  existing content — with the one narrow, explicit exception of fixing a deprecated
  `reads`/`watch` tag block (see tag taxonomy section) and the title-cleanup step
  (which edits ONLY the root page block's title text, never its content children).
- Currently scoped to `--location unsorted` only. Daily notes sometimes contain
  single-link clips too, but are treated as journal space — extending this job to
  daily notes needs an explicit go-ahead from Devon first.
- `skill:web-fetch`'s extraction is a best-effort content dump, not a citation-grade
  extraction — good enough for judgment and description-writing, expect some
  nav/boilerplate noise in the extracted text and read past it rather than
  transcribing it verbatim into a description.
