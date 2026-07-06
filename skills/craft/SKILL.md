---
name: craft
description: Read, write, search, and organize Devon's Craft.do space via its MCP server (saved links, daily notes, tasks, kanban collections). Use whenever a task involves Craft, Craft documents, tagging saved links with #resources/ tags, journaling in Craft, or the Craft-as-second-brain workflow. Includes the daily untagged-resource-link tagging job.
---

# Craft.do integration

Devon's personal "second brain" lives in Craft (craft.do). Sunny reaches it via Craft's
MCP server (a Cloudflare-fronted HTTP JSON-RPC endpoint, OAuth-authed, scoped to one
specific Craft space per link). See `topic:craft` for space inventory/state and
`topic:craft-second-brain` (if present) for the broader tool assessment.

## Connection

- Config: `~/.sunny/mcp.json` entry `"craft"`. Token file: `~/.sunny/mcp-oauth/craft.json`.
- Helper library: `scripts/craft_mcp.py` in this skill dir. Handles the JSON-RPC
  handshake, session id, and **automatic token refresh** (Craft access tokens are
  short-lived, ~1hr). Use it instead of hand-rolling requests:

```python
import sys
sys.path.insert(0, "~/.sunny/skills/authored/skills/craft/scripts")  # expand ~ first
import craft_mcp
craft_mcp.read("documents list --location unsorted --offset 0")
craft_mcp.read("search #resources/")
craft_mcp.write('blocks add --id 300949c6-caa9-4761-0c47-ac681822fff6 --markdown "#resources/repos" --position end')
```

Or from bash:
```
python3 ~/.sunny/skills/authored/skills/craft/scripts/craft_mcp.py read "folders list"
python3 ~/.sunny/skills/authored/skills/craft/scripts/craft_mcp.py write "blocks add --id ABC --markdown \"#resources/repos\" --position end"
```

**Gotcha**: Craft's endpoints reject requests without a real browser User-Agent
(Cloudflare bot detection → 403 "browser_signature_banned"). `craft_mcp.py` already
sends one; don't strip it if you ever hand-roll a request.

## Tools exposed (`craft_read` / `craft_write`)

Both take a single `command` string argument (shell-like syntax, `--flag value`).
Batch multiple commands with semicolons. Full command reference:

**craft_read**: `folders list`, `documents list [--location unsorted|trash|templates|daily_notes]`,
`documents resolve-link <url>`, `tasks list [--scope ...]`, `blocks get <rootBlockId>
[--format markdown|json] [--depth n]`, `collections list/schema/items-get/views-list`,
`search <query> [--location ...]`, `connection info`.

**craft_write**: `folders create`, `documents create`, `tasks add/update/delete`,
`blocks add --id <pageId> --markdown <text> --position start|end` (or `--siblingId
<blockId> --position before|after`), `blocks update/delete/move`, `collections
create/rename/items-add/items-update/items-delete/views-create`.

Append `--help` to any subcommand for its full flag list (e.g. `collections create --help`).

## Space inventory (as of 2026-07-06)

Devon has **two Craft spaces**: his personal "Devon's Space" (the one this MCP link
covers) and "Wayward Lane" (shared with Kate — **not yet connected**; needs its own MCP
link generated from inside that space in Craft's UI, then added as a second entry in
`~/.sunny/mcp.json`, e.g. `craft-wayward`).

Devon's Space had, as of the last full read: 155 documents, ~145 in "unsorted" (no
folder structure), 9 daily notes (gappy), 15 stale tasks. Existing `#resources/*` tag
taxonomy found via `search #resources/`: `repos`, `makers`, `landscapers`, `clothing`,
`reads`, `home`, `ai`, `dnd`, `art`. Other unrelated tag families exist too (`#gifts/*`,
`#pdx`) — don't confuse those with the resources taxonomy.

## Job: daily untagged-resource-link tagging

**Goal**: find single-topic saved-link documents in "unsorted" that don't yet have a
`#resources/*` tag, tag each with an existing category (or a new one if genuinely
novel), and produce a short summary. Runs daily via a schedule AND is safe to run
ad-hoc as a one-off check.

### Procedure

1. **Load current tag taxonomy**: `search #resources/` — collect every distinct
   `#resources/<category>` string seen across the results. This is the reuse-first
   candidate set for step 4.
2. **Load state**: read `~/.sunny/state/craft-resource-tagger.json` (JSON: `{"processed":
   ["<rootBlockId>", ...]}`). Create it (`{"processed": []}`) if missing. This tracks
   documents already evaluated (tagged OR deliberately skipped as non-resources) so
   re-runs don't re-nag on the same docs.
3. **List candidates**: `documents list --location unsorted`, paginating with
   `--offset` (50 per page) until exhausted. For each doc whose `rootBlockId` is NOT
   already in the state file's `processed` list, it's a candidate.
4. **Per candidate** (cap ~50 per run to keep runtime bounded — leftover candidates
   just get picked up on the next run since they're still unprocessed):
   - `blocks get <rootBlockId> --format markdown` to read the actual content.
   - Skip (but still mark processed) if:
     - It's clearly NOT a single-topic external-link clip — e.g. a personal note,
       reflection, checklist, business/vendor inquiry doc, genetic-testing notes, or
       anything with substantial original prose rather than "here's a link + maybe a
       short AI/summary blurb." Use judgment: the target pattern is "one link, one
       subject" (see the antvis/Infographic example in topic:craft for the shape).
     - It already contains a `#resources/...` tag anywhere in its text (the taxonomy
       search in step 1 should have caught most of these, but double-check per-doc
       since search result completeness isn't guaranteed).
   - Otherwise, it's a resource: pick the best-fit existing `#resources/<category>`
     from step 1's set. Only invent a new category if nothing existing genuinely
     fits — keep new tags in the same style (lowercase, one word or short compound,
     e.g. `repos`, `reads`, `ai`).
   - Apply it: `blocks add --id <rootBlockId> --markdown "#resources/<category>"
     --position end`.
   - Add the doc's `rootBlockId` to the state file's `processed` list either way
     (tagged or intentionally skipped) and persist the file after every few docs
     (so a crash/timeout mid-run doesn't lose progress).
5. **Summarize**: end the run with a short plain-text digest — how many docs were
   tagged (with which tag each), how many were reviewed-and-skipped (non-resource),
   whether any new tag category was created, and if the backlog isn't fully drained
   yet, how many untouched candidates remain (they'll be picked up next run).

### Notes / gotchas

- Craft's search is keyword/substring only (no semantic search) — don't rely on
  `search` alone to find "everything that might be a resource"; the per-document
  content check in step 4 is the real filter.
- Tag placement: always append as a **new block at the end** of the document
  (`--position end`) rather than editing existing content, so this job can never
  clobber something Devon wrote.
- This job only **adds** tags — it never moves documents between folders or edits
  existing text. Scope creep here should be a deliberate follow-up, not silent.
- Currently scoped to `--location unsorted` only. Daily notes sometimes contain
  single-link clips too, but are treated as journal space — extending this job to
  daily notes needs an explicit go-ahead from Devon first.
