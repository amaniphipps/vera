<p align="center">
  <img src="docs/assets/vera-mark.png" alt="Vera" width="140">
</p>

# Vera

A RevOps teammate that grows with you. She runs on [Hermes Agent](https://github.com/NousResearch/hermes-agent) and lives in your terminal or in Slack.

**Status: pre-release.** Built in the open. Things will move.

## Get started

You need: macOS or Linux (WSL2 on Windows), and one LLM API key. [OpenRouter](https://openrouter.ai/keys) is the easy default - one key, every model.

```bash
git clone https://github.com/amaniphipps/vera.git
cd vera
./setup/setup.sh
```

Setup installs Hermes if you don't have it, asks for your model provider and key, installs Vera's skills and rules, and finishes by having Vera introduce herself. **Setup isn't done until she says hello.** If anything is off, `./setup/doctor.sh` tells you what.

Then talk to her:

```bash
hermes
```

## What she does

- **Onboards herself.** She says hello, then walks you through connecting tools, memory, and models - in order, at your pace.
- **Works from day 1.** 45 preset skills: briefings, ARR roll-forwards, forecasts, pipeline reads, cited company profiles, documents, reports, code review - plus 28 community skills from top practitioner authors (forecasting, deal intelligence, signals, planning), selected by real install rank and reshaped to her standards. See [skills/community/](skills/community/).
- **Learns your systems.** Point her at a connected app and - with your approval - she maps its endpoints, auth, and data shapes, then drafts a skill for it. Drafts sit in `skills-live/` quarantine until you promote them.
- **Keeps herself tidy.** A nightly vetting pass reviews what she learned. Nothing graduates into her shipped skills without your yes.

## The rules are data

Her guardrails live in `policy/guardrails.yaml` - what she can read, where she can write, what she never touches. Ships read-only; you widen it deliberately.

## Where she runs

- **Your terminal** - the quickstart above. Start here.
- **Slack** - `./setup/setup.sh --platform slack`, then `hermes gateway run`. She onboards in-channel.
- **Always-on (optional)** - Docker and Railway recipes in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for a team Slack that never sleeps. You do not need these to use Vera.
- **Other harnesses** - Hermes only, today. Her skills are plain markdown; if you want her running somewhere else, ask her - porting herself to a new host is exactly the kind of job she does with you.

## Docs

- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - every way to run her
- [docs/CONNECTING-TOOLS.md](docs/CONNECTING-TOOLS.md) - MCP servers and plain REST APIs
- [docs/GUARDRAILS.md](docs/GUARDRAILS.md) - the policy model
- [docs/VOICE-AND-TONE.md](docs/VOICE-AND-TONE.md) - how she talks, formats, and avoids AI slop

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
