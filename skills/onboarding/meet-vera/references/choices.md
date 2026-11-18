# Memory and model choices

## Memory (step 4)

Present the options plainly. They are quick defaults, not a fence - the user
may bring something else entirely. There is no wrong answer, and they can
switch later - the working profile survives any switch.

| Option | What it is | Good for |
|---|---|---|
| Working profile only | Small always-on profile (user + org), no extra infra | Trying Vera out |
| Supabase | Real database; shell schema included in `memory/supabase/` | Teams, durable records, dashboards later |
| Hindsight | Durable memory layer with retrieval over past sessions | Heavy daily use, long memory |
| Obsidian | Local markdown files | Local-first people who want to read everything |

Whatever they pick: explain what gets remembered (env facts, conventions,
corrections, preferences), what never does (policy-blocked topics, secrets),
and where to look at it.

## Carrying over what they already have (step 4, always offer)

After the options, invite it directly. Many users arrive from another agent
or tool with things worth keeping: memory exports, notes, markdown skills,
a glossary of how their org talks. Ask, plainly:

"Already have memory, skills, or conventions from another agent or tool?
Name them and I'll bring them across properly."

Handle each kind deliberately. Hard rule first: carry-over never uses the
runtime's native memory-write or skill-create tools directly - those bypass
the review trail. Memory goes through the durable-entry shape with read-back
confirmation; skills land as files in `skills-live/` for the vetter.

- **Memory exports** (JSON, markdown, pasted notes): read them, propose each
  candidate fact as a durable-memory entry in the standard shape (fact,
  category, confidence, source), and read the list back for confirmation
  before admitting any of it. Their old memory becomes durable only with
  their yes, fact by fact or batch-approved.
- **Skills from other agents** (markdown files): drop them into
  `skills-live/` - never directly into `skills/`. They enter the normal
  vetting flow and graduate only through review, same as anything Vera
  drafts herself. Say this plainly so the quarantine reads as care, not
  bureaucracy.
- **Conventions and org vocabulary**: seed the knowledge graph
  (`knowledge/graph/entities/glossary/`), marked with their source.
- **Anything else** (a memory store the table doesn't list, a homegrown
  format): work with what they have. Map it to the closest shape above and
  say what mapped cleanly and what did not.

Record what was carried over, and where it landed, in the working profile.

## Models (step 5)

Explain the decision layer in one breath: Vera reads a configurable list of
public model benchmarks plus the user's priority, and recommends models for
each kind of work. Ask the priority:

- **Cost** - good-enough models, cheapest that holds quality.
- **Quality** - best available, cost secondary.
- **Speed** - fast responses for chatty work.

Provider options: OpenRouter (default, one key for many models), or direct
Anthropic, OpenAI, or Gemini keys. Connection shells for each live in
`deploy/hermes/providers/`. They can mix: a cheap model for chatter, a strong
one for hard work.

Record both choices in the working profile when made.
