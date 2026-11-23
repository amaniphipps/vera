---
name: build-it
description: Use when the user asks whether Vera can do something, wishes she had a capability, or says "build it". Reverse-engineer what is necessary, plan the smallest useful version with the user, then build and test it through visible checkpoints.
---

# Build It

A capability question is not a dead end. If the capability can be built from
available tools, files, APIs, and permissions, Vera can build it with the
user. Never promise an unconditional yes: diagnose feasibility first, then
say what can be built and what is missing.

## Opening response

When the user asks "can you do X?", "do you support X?", or "I wish you could
X", check the bundled skills and connected tools first. If the capability is
missing but plausible, say:

"I don't have that as a finished capability yet, but I can help build it.
I'll work out the smallest useful version, show you the plan, and build it
with you in checkpoints."

If it already exists, use or demonstrate it instead of rebuilding.

## The flow

### 1. Define the outcome

Write down the trigger, the user, one concrete example, and the observable
definition of done. Ask only the questions needed to remove real ambiguity.
One capability at a time.

### 2. Reverse-engineer what is necessary

Inspect before designing:

- Existing skills, helpers, tools, runtime profiles, and memory stores.
- Required inputs, outputs, data shapes, and permissions.
- The target system's official docs or a small safe read. If a system study
  is needed, ask the `learn-a-system` permission question first; consent is
  per system.
- Runtime constraints using the capability contract/doctor when relevant.

Separate confirmed facts, assumptions, and unknowns. Identify the smallest
vertical slice that produces real value. Do not design a platform when a
single workflow solves the request.

### 3. Plan with the user

Present a short implementation plan: chosen approach, exact artifacts/files,
dependencies, tests, and user checkpoints. Include known limits and what is
not being built. Use Plannotator when available and useful, but do not make
it a dependency. Obtain approval before implementation, external writes, or
installing dependencies. Material scope changes go back to the user.

### 4. Build in checkpoints

Build the smallest slice first. Run it against a concrete example, test the
success path and the important failure path, and show the resulting artifact
or behavior—not just a description. Keep the user involved at each decision
that changes cost, access, scope, or architecture. If blocked, state the
exact missing dependency or permission and offer the available paths.

### 5. Package learning honestly

If the result should become a reusable Vera capability, draft its skill into
`skills-live/<capability-slug>/` with `status: unreviewed`, its manifest,
evidence, and org slots. Never write a learned capability directly into
`skills/`; `skill-vetter` and human promotion are the gate. Project code and
the learned skill are separate deliverables.

## Hard rules

1. No fake capability claims. A plan is not a build; a mock is labeled a mock.
2. Approval before implementation and again before material scope changes.
3. Read-only discovery unless the user explicitly approves another action.
4. Never request or record secret values. Auth is described by type and
   mediated by the runtime/helper.
5. No silent skill promotion, dependency installation, or external writes.
6. Finish with evidence: tests run, artifact shown, limitations named, and
   the next user choice stated plainly.

## Definition of done

The user has a working, tested artifact or workflow; they have seen it run;
they know its limits and where it lives. Any reusable skill remains
quarantined until reviewed and promoted.
