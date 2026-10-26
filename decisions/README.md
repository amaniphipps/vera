# Decision layer

The part of Vera that picks models. It is an interface, not an
implemented router. You connect your own model router to it.

## What it decides

Vera routes each task to a model by reading two things:

1. **Benchmark sources** — a configurable list of public leaderboards and
   evaluation pages (see `model-sources.example.yaml`).
2. **Your priority** — cost, quality, or speed. Set once; it is the knob
   the whole layer turns.

The layer scores candidate models against those inputs and recommends one.
It also lists alternatives, so you can see what a different priority would
have picked.

## Why it ships unwired

Vera is open source and runs on OpenRouter by default, and OpenRouter
already does its own routing. Baking in a second router would tie Vera to
one provider's curve.

So this ships as a contract. The shape lives in `interface.yaml`. Any
GPT-style routing service can implement that shape. You wire your router
to it and Vera uses it.

## The shape

`interface.yaml` defines the contract in three parts:

- **inputs**: `task_type`, `priority`, `budget_hint`
- **outputs**: `recommended_model`, `provider`, `rationale`,
  `alternatives`
- **routing**: `route` then `score` then `recommend`

A conforming service accepts the inputs and returns the outputs. Vera does
not care what runs inside.

## Connecting a router

1. Copy `model-sources.example.yaml` to `model-sources.yaml` and point the
   URL slots at leaderboards you trust.
2. Point the model-router endpoint at your router (see `.env.example`).
3. Confirm the router returns JSON in the `interface.yaml` shape.