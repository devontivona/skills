# Templates & schema — decision-coach

Two templates (panelist report, final memo) plus the on-disk JSON schema the site renders.
Keep both templates FIXED across every decision — that consistency is what lets Sunny compare
panelist reports to each other and lets Devon skim any memo the same way.

This is the SINGLE SOURCE OF TRUTH for the panelist report shape — it lives here only. Each
persona file (personas/*.md) has a `[REPORT_FORMAT]` placeholder marking where this section
goes; when briefing a subagent, paste the persona's full file with `[REPORT_FORMAT]` replaced
by the block below. Do not let a copy of this drift into an individual persona file again — if
the shape ever needs to change, change it here once and every persona picks it up on its next
brief.

## Panelist report template (round 2 — same shape from all 4 personas)

Replace `[REPORT_FORMAT]` in the persona file with exactly this (adjust only the italicized
framing words in brackets to match that persona's own voice/lane if genuinely helpful — the six
numbered fields and their order must not change):

```
# Output format — use exactly this structure, nothing more

1. **Headline stance** — one sentence. Where this lens lands.
2. **The one insight only this lens catches** — the thing the other three panelists would
   likely miss. If nothing distinct, say so plainly rather than padding.
3. **Reasoning / evidence** — the actual argument. Cite real sources for any checkable claim;
   cite the specific framework/commitment/values-mapping being applied and why it's live here.
4. **Risk or blind spot flagged** — the thing this lens sees as the biggest danger, even if
   Devon or the other personas aren't naming it.
5. **Option-quality call, per option** — Bad / Good / Great / Best, one rating per surviving
   option, plus a one-line reason for each rating.
6. **What would change this persona's mind** — the specific info or event that would flip
   this persona's stance.
```

## Final memo template (Sunny writes this, after coalescing)

1. **The decision** — the question, door type (one-way / two-way), cost of delay vs. cost of
   being wrong, and whether regret-minimization is a live consideration (see
   personas/first-principles.md).
2. **Options considered** — the 2-3 named options, thesis + trade-offs (carried from the
   brainstorm handoff, or established here if invoked directly).
3. **Panel summary** — each persona's headline stance, one line each.
4. **Aggregated option-quality verdict** — per option, the combined Bad/Good/Great/Best call
   across all four personas, and whether the panel agreed or split. If all surviving options
   land Great-or-better and are genuinely close, say so explicitly — that's a real finding
   ("there is no bad choice here, so don't let this stall you").
5. **Disagreements, named explicitly** — where personas landed on different options or
   different risk reads. Don't smooth this over into false consensus.
6. **Adversarial pass** — included ONLY if triggered (see SKILL.md's coalescing step). If
   skipped, say why in one line ("skipped — panel converged clearly on Option B, ratings not
   close").
7. **Sunny's recommendation** — the actual call, with reasoning, including how believability-
   weighting shaped it (i.e., which persona's read Sunny weighted more heavily on this
   particular type of question, and why).
8. **What would change it** — the single most decision-relevant piece of info or event that
   would flip the recommendation.
9. **Status** — `Open` / `Decided (date)` / `Superseded by <link to new memo>`.
10. **Next concrete action** — the one thing Devon should actually do next.

## On-disk JSON schema (one file per memo, in the site's data/memos/ directory)

```json
{
  "id": "kebab-case-slug",
  "created": "ISO date",
  "updated": "ISO date",
  "status": "open | decided | superseded",
  "decided_date": "ISO date or null",
  "superseded_by": "memo id or null",

  "decision_question": "string",
  "context": "string",
  "success_criteria": "string",
  "reversibility": "one-way | two-way",
  "reversibility_note": "string",
  "stakes": "string",
  "regret_minimization_note": "string or null",
  "who_is_affected": "string",
  "decision_owner": "string",
  "constraints": "string",
  "deadline_or_cost_of_delay": "string",
  "values_at_stake": "string",
  "escalation_reason": "string",

  "options": [
    { "name": "string", "thesis": "string", "pros": ["string"], "cons": ["string"],
      "rough_cost_effort": "string" }
  ],

  "round1_questions": ["string"],
  "round1_answers": "string",

  "panel": [
    { "persona": "sme | conscious_leadership | values | first_principles",
      "headline_stance": "string",
      "unique_insight": "string",
      "reasoning": "string",
      "risk_flagged": "string",
      "option_ratings": [ { "option": "string", "rating": "Bad|Good|Great|Best", "why": "string" } ],
      "what_would_change_mind": "string" }
  ],

  "option_quality_verdict": [ { "option": "string", "aggregated_rating": "string", "agreement": "unanimous|split" } ],
  "disagreements": "string",
  "adversarial_pass": { "triggered": true, "argued_against": "string", "content": "string" },

  "recommendation": "string",
  "believability_weighting_note": "string",
  "what_would_change_it": "string",
  "next_action": "string"
}
```

Missing/optional fields render as omitted sections on the site, not blank placeholders — the
renderer is defensive about partial memos (e.g. an in-progress one saved mid-flow).
