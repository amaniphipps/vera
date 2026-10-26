# Cron — Vera's habits

Vera is most useful when she acts without being asked. These are the three
canonical jobs. Each `.sh` file here is documentation: it contains the exact
`hermes cron create` command to install the job.

| Job | Schedule | What it does |
|---|---|---|
| `daily-briefing.sh` | 08:00 Mon–Fri | Morning briefing in your channel: what moved, what needs you, what's next |
| `nightly-skill-vetter.sh` | 02:00 nightly | Vera vets her own `skills-live/` learnings; proposes, never promotes |
| `weekly-recap.sh` | 16:00 Friday | Self-contained HTML recap report + three-line summary |

## Install

```bash
# pick a job, edit the channel ID in the command inside, run it
hermes cron create '0 8 * * 1-5' --name daily-briefing --skill briefings \
  --deliver slack:C0123456789 'Run your briefings skill for today. ...'
```

## Operating notes

- `hermes cron list` shows what's installed; `hermes cron run <name>` fires one
  immediately (good for testing); `hermes cron doctor` checks job health.
- Schedules are standard cron expressions, evaluated in the host's local time.
- `--deliver slack:<channel-id>` posts to a channel; `--deliver origin` replies
  wherever the job was created from. `--failure-deliver local` silences failure
  pings while keeping run state in `hermes cron list`.
- Jobs respect guardrails like any other Vera action: a briefing job cannot
  post into a `channels.blocked_send` channel, and a vetter job can't promote
  a draft skill.
- Keep prompts self-contained. A cron run starts a fresh session; anything the
  job needs to know must be in the prompt, the skill, or memory.
