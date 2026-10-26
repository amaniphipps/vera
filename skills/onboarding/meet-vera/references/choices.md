# Memory and model choices

## Memory (step 4)

Present the options plainly. There is no wrong answer, and they can switch
later - the working profile survives any switch.

| Option | What it is | Good for |
|---|---|---|
| Working profile only | Small always-on profile (user + org), no extra infra | Trying Vera out |
| Supabase | Real database; shell schema included in `memory/supabase/` | Teams, durable records, dashboards later |
| Hindsight | Durable memory layer with retrieval over past sessions | Heavy daily use, long memory |
| Obsidian | Local markdown files | Local-first people who want to read everything |

Whatever they pick: explain what gets remembered (env facts, conventions,
corrections, preferences), what never does (policy-blocked topics, secrets),
and where to look at it.

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
