---
name: thinking
description: "Use when starting multi-step work: analysis, migrations, research, fixes. Plan small, debug root-cause-first."
---

# Thinking

How to approach any multi-step task: analysis, migrations, research, debugging, and building. Two habits in one skill: plan before building, and find root cause before fixing.

## When to plan vs when to just do

Plan when:

- The work has more than a few steps, or several moving parts.
- You will delegate it or hand it off.
- Getting it wrong is expensive to undo.
- Someone will read your reasoning later.

Just do it when:

- It is one or two quick actions.
- The path is obvious and the cost of redoing is near zero.

Default to planning when unsure. A short plan costs less than a wrong start.

## Break work into small tasks

- Each task is one action, sized to a few minutes of focused work.
- Name the exact file, command, or output each task produces. "Add validation" is too vague. "Create config.py with the validate function" is not.
- Order tasks so each one depends only on what came before.
- Include a way to check each task worked. A task with no check is a guess.
- Keep scope to what is needed now. Do not pre-build for imagined future needs.

A good plan makes the next step obvious. If the next person has to guess, the plan is incomplete.

## Debug root cause, not symptoms

Random fixes waste time and create new problems. Quick patches mask the issue.

The iron rule: no fix without understanding why.

Four phases, in order:

1. Reproduce. Read the error fully. Build a repeatable check that fails on the real symptom and passes when it is fixed. Check what changed recently. Trace the data or logic back to where it originates.
2. Understand. Find a working example nearby and compare. List every difference, however small. Form a few falsifiable guesses, ranked by likelihood, each stating what it predicts.
3. Fix. Test the top guess with the smallest probe. Change one thing at a time. Fix at the source, not at the visible symptom.
4. Verify. Confirm the check passes and nothing else broke.

If three fixes in a row fail, stop. The problem is likely a wrong approach, not the latest fix. Question the structure before trying a fourth.

## Useful when stuck

- Say plainly "I do not understand X" rather than pretending.
- A check that only sometimes fails is still workable. Raise the rate: run it more times, narrow the timing, add stress.
- Do not fix multiple things at once. You cannot tell which change mattered.