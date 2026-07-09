---
name: decision-coach
description: Run a rigorous, multi-perspective panel process to decide BETWEEN 2-3 already-narrowed options, when the decision is hard, big, one-way, or Devon is stuck. Sequential partner to brainstorm, not a slower alternative to it — brainstorm gets a vague problem down to 2-3 real options; decision-coach decides among them when that decision has earned real rigor. Use when brainstorm's calibration escalates here, when Devon explicitly asks for the "full treatment," or when Devon names a hard decision directly (skill does a condensed narrowing first if needed). Fans the decision out to 4 grounded AI personas (subject-matter-expert, conscious-leadership coach, personal-values coach, first-principles reasoner) in a two-round RFP process — clarifying questions, then full decision reports on a fixed template — then Sunny coalesces them into a final decision memo, published to a hosted decision-memos site.
---

# Decision-coach — the panel process

Brainstorm and decision-coach are **sequential, not parallel alternatives**. Brainstorm's job
is getting from a vague problem to 2-3 genuinely distinct, well-formed options — that's problem
discovery and divergence. Decision-coach's job starts where brainstorm's ends: **deciding
between those options**, with real rigor, when the decision has earned it (big, one-way,
high-stakes, or Devon is genuinely stuck). Don't think of this as "brainstorm but slower" —
think of it as "the step brainstorm hands off to once there's something concrete to decide
between."

Never run the full panel on something small; that's resolved inside brainstorm's own
lightweight recommend-and-commit path. Running this on a reversible, low-stakes call is exactly
the "uniform rigor" trap Devon called out when this system was designed.

Tell Devon up front this is slower than a normal conversation — a few subagent rounds, not an
instant reply — and that you're on it (see the delegation skill for how to phrase this).

## 0. Entry — how a decision gets here

Two paths in:
1. **Escalated from brainstorm** — brainstorm hands off a structured record (decision
   question, 2-3 named options with thesis/trade-offs, reversibility, stakes, constraints,
   values at stake, open questions, escalation reason). Use it directly as round 1 input;
   don't re-discover the problem from scratch.
2. **Invoked directly** — Devon names a decision without going through brainstorm first. Do a
   condensed version of brainstorm's problem-discovery (real goal, success criteria, hard
   constraints) and get to 2-3 named options yourself before starting round 1. Don't skip
   straight to the panel on a vague, un-narrowed question — the options need to exist and be
   distinct before four personas can usefully react to them.

If you genuinely don't have 2-3 distinct options yet, get there first (a light version of
brainstorm's fan-out/narrow) — the panel process needs concrete options as raw material, not
an open-ended "what should I do."

## 1. Completeness pass — fill the obvious gaps yourself before the panel sees it

Before spawning anyone, do your own logical pass over the decision record and fill what's
missing — either from context you already have, or by asking Devon directly. This is cheap and
it's yours to do alone (don't delegate it); skipping it means round 1's clarifying questions get
spent re-deriving basics that should've been in the framing from the start, instead of digging a
level deeper into the problem the way a real panel should. The whole point of this gate: round 1
should come back sharper *because* of this pass, not redundant with it.

Check the record against these categories, and fill any real gap before moving on:

- **Facts** — the concrete, checkable specifics (numbers, names, dates, terms) the panel will
  need to reason about. Missing facts here just become the SME persona's round-1 questions
  restating "what is the actual number" — cheap for you to nail down now, wasteful to punt.
- **Feelings / psychological context** — how Devon actually feels about this, not just the
  logical shape of it: what's driving urgency, what he's afraid of, what he's excited about,
  where he's already leaning even if he hasn't said so outright. This is easy for a "logical
  pass" to skip entirely since it isn't a fact — but it's exactly what the conscious-leadership
  persona needs to do its job, and it's rarely volunteered unprompted.
- **Constraints & stakes** — hard constraints (time, money, people, non-negotiables), the
  reversibility read, and the regret-minimization read (see personas/first-principles.md) —
  confirm these are actually stated, not just implied.
- **Values at stake** — which of Devon's core values (topic:values) are genuinely in tension
  here; don't leave this for the values persona to discover from nothing.
- **Who's affected / who owns the call** — solo decision, or does it touch Kate/family/others;
  who's the actual decision-owner.
- **Options themselves** — each surviving option still needs its thesis + honest trade-offs +
  rough cost/effort (per brainstorm's schema); don't let a thin option slide through.

If a gap is something you can reasonably infer or already have context for, fill it yourself and
note the inference. If it genuinely needs Devon's input, ask him directly — batched (three at a
time, same instinct as brainstorm) — before proceeding to §2. This is a distinct step from
round 1: round 1 is the PANEL's questions after seeing a complete framing; this is YOUR
housekeeping pass so their questions aren't wasted on it.

## 2. The four personas — grounded system prompts, not descriptions to translate

Each persona has its own file under `personas/` written as a system prompt — pass its contents
directly to the subagent as the persona's instructions, don't summarize or re-translate it.
A panelist producing generic AI-training-data flavor text indistinguishable from any other
lens has failed its job; the point of a real system prompt per persona is to make that failure
mode harder.

**Before pasting a persona file into a brief, replace its `[REPORT_FORMAT]` placeholder** with
the single shared block in `references/memo-templates.md` ("Panelist report template"
section). Every persona file ends with this placeholder.

1. **`personas/sme.md`** — Subject-matter expert on the decision's specific domain. Uses
   expertise/judgment freely to decide what's worth checking, then verifies the specific
   checkable claims via **skill:web-search** (primary), a direct fetch against a known
   authoritative source, or **skill:browse** for anything needing real interaction — see the
   persona file for the full order of operations. You still need to tell it the specific domain
   and the actual claims/numbers in Devon's decision when you brief it — the system prompt
   covers HOW, your brief covers WHAT.
2. **`personas/conscious-leadership.md`** — the 15 Commitments (Dethmer/Chapman/Klemp). Gets
   at the CONTEXT behind the decision (Devon's stance, above/below the line, where he might be
   stuck) — not the decision's content.
3. **`personas/values.md`** — maps options against Devon's 5 core values (you must paste the
   current topic:values text into the brief — the prompt expects it supplied, not memorized),
   naming trade-offs explicitly, not just alignments.
4. **`personas/first-principles.md`** — four lenses: first-principles reasoning (Feynman/Musk),
   inversion + premortem (Munger/Klein), outside view/base rates (Kahneman-Tversky), regret
   minimization (Bezos). The prompt tells it to apply 2-3 as fit, not mechanically all four.

## 3. Round 1 — clarifying questions (fan out, then combine)

Spawn all 4 personas as separate subagents (delegate_task, toolset: host so the SME can
actually search/fetch, model: **opus for all four** — this panel is exactly the
high-stakes/judgment-quality case the delegation skill reserves opus for).

Brief each with: the full contents of its persona file (pasted as the system-prompt-equivalent
instructions — a child sees none of your context, so paste the whole file, don't paraphrase),
the decision record (from §0, completed per §1), and this explicit ask: **"Before you can write
a real decision report, what do you need to know from Devon? List your specific clarifying
questions — the things that would materially change your analysis if you knew the answer. Don't
ask questions you could answer yourself from what's already given."**

Once all 4 report back, YOU combine their questions into one list for Devon:
- De-duplicate ruthlessly — multiple personas often converge on the same underlying gap.
- Group by topic, not by persona (Devon shouldn't have to mentally sort "which coach asked this").
- Cut anything answerable from context already in the decision record.
- Keep it batched and skimmable for iMessage — same "three at a time" instinct as brainstorm,
  though a decision-coach round can reasonably run longer than 3 if the decision is genuinely
  complex; use judgment, don't pad for padding's sake.

Send Devon the combined list. Wait for his answers before round 2 — don't guess on his behalf.

## 4. Round 2 — full decision reports (fan out again, fresh context)

Re-spawn all 4 personas as fresh subagents (they don't persist between rounds — a finished
subagent doesn't stay open waiting), again on **opus**. Brief each with: their full persona
file again (with `[REPORT_FORMAT]` filled in, per §2), the full decision record, their own
round-1 questions AND Devon's answers to the FULL combined list (maximum context — every
persona gets everyone's answers, not just the ones addressed to them; a question one persona
asked can matter to another's analysis).

Do NOT feed any persona your own tentative lean on the decision (if you have one) — that's
private to your own coalescing step (§5), never shared with panelists, to avoid anchoring four
supposedly-independent reads on the same gut call.

## 5. Coalescing — your job, not a delegated one

This step is yours alone — reconciling and weighing is exactly the judgment a subagent
shouldn't be doing on your behalf.

1. **Read all 4 reports.** Note where they agree, where they genuinely conflict, and where one
   persona surfaced something the others missed entirely.
2. **Apply believability-weighting (Dalio)** — don't average the four opinions naively. Weight
   each persona's take by its demonstrated relevant credibility on THIS TYPE of question (e.g.
   the SME's verified-source claims about advisor fee structures outweigh a framework-based
   persona's speculation on the same fact; conversely, the conscious-leadership read on "is
   Devon actually stuck out of fear vs. genuine uncertainty" isn't something the SME persona
   has any real standing to weigh in on). Say explicitly, in the memo, which persona's read you
   weighted more heavily on which specific question and why.
3. **Aggregate option-quality ratings** per option (Bad/Good/Great/Best from each persona) into
   one verdict per option, and note whether the panel agreed or split on it. A landslide where
   every persona rates the top option Great-or-Best is real signal — say so plainly, it means
   Devon can move fast with confidence. A split is equally real signal — don't smooth it into
   false consensus.
4. **Decide whether to trigger the adversarial pass.** Only if the panel's leading
   recommendation ISN'T a clear landslide — i.e., the top two options both land Great-or-better
   and stay close, or the panel's option-quality calls genuinely split. If triggered: take the
   panel's actual leading recommendation (a real position now, not an empty chair) and ask 1-2
   of the personas who didn't already argue against it to make the strongest case against it.
   This is a single targeted follow-up call, not a full third round — keep it lightweight. If
   not triggered, say so in the memo with a one-line reason ("skipped — panel converged clearly").
5. **Compare against your own private lean** (if you had one going in) — did the panel confirm
   it, or diverge? If it diverged, that's worth surfacing to Devon as its own signal ("I
   expected X going in; the panel talked me out of it because...").
6. **Write the final memo** using the exact template in `references/memo-templates.md` ("Final
   memo template" section). Every memo uses this same structure — that consistency is what
   makes memos comparable and skimmable over time.

## 6. Publish

- Write the memo as one JSON file per the schema in `references/memo-templates.md`, into
  `~/.sunny/sites/decisions/data/memos/<slug>.json` (slug = kebab-case of the decision
  question, short — e.g. `financial-advisor-2026`).
- The site (a devbox project named `decisions`, static HTML + a small server reading the JSON
  directory — see the site's own README in `~/.sunny/sites/decisions/`) picks up new/updated
  memo files automatically; no rebuild step needed beyond writing the file.
- Confirm the memo is live: `curl -sI https://decisions.waywardlane.com` and check the index
  lists the new memo, then send Devon the direct memo URL (not just the index) in your reply.
- Tell Devon the memo's status is `Open` by default — it stays editable in place until he
  actually decides.

## 7. Memo lifecycle

- **Editable in place** while status is `Open` — revise the same JSON file as new information
  comes in (e.g. Devon answers round-1 questions differently on reflection, or a new option
  emerges). Bump `updated`.
- **Mark `Decided (date)` when Devon actually commits** — set `status: "decided"` and
  `decided_date`. From that point, the memo is a historical record — don't silently rewrite it.
- **Reversing a decided call = a NEW memo**, never an edit to the old one. Set the new memo's
  content, then go back and set the OLD memo's `status: "superseded"` and `superseded_by` to
  the new memo's id, so the index shows the lineage. This preserves the actual decision
  history — including the ones that didn't hold up — rather than quietly erasing it.

## Don'ts

- Don't treat this as a slower version of brainstorm — it's the next sequential step,
  operating on options brainstorm (or a condensed stand-in) already produced.
- Don't run this on a small/reversible/low-stakes call — that's brainstorm's job; sending
  everything here defeats the calibration Devon explicitly asked for.
- Don't skip the completeness pass (§1) — sending a thin record straight to round 1 wastes the
  panel's questions on basics you could've filled yourself.
- Don't summarize or paraphrase a persona file when briefing its subagent — paste the whole
  thing; it's written as a system prompt precisely so it can be handed over directly.
- Don't let any persona produce generic, ungrounded reasoning — every persona has a grounded
  file; if a report reads like it could've come from any of the other three, it's drifted.
- Don't skip round 1 to save time — clarifying questions before the full report is the whole
  point of the RFP shape; guessing Devon's answers defeats it.
- Don't feed panelists your own lean, or each other's round-2 reports mid-round — independence
  across the panel is what makes believability-weighting meaningful at coalescing time.
- Don't silently average conflicting persona opinions — weight them, and say how.
- Don't smooth over genuine panel disagreement into false consensus in the final memo.
- Don't edit a `decided` memo in place — supersede it with a new one instead.
