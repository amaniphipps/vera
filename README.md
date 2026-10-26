# Vera

Vera is a RevOps teammate that grows with you.

She runs on [Hermes Agent](https://github.com/NousResearch/hermes-agent) (open source) and meets you where you already talk — Slack, WhatsApp, SMS, GroupMe, or Teams. Connect your tools and she studies how they work, drafts her own skills for them, and gets better every week.

**Status: pre-release.** The repo is being built in the open. Things will move. Star it if you want to follow along; hold off on production use until v0.1.0.

## What she does

- **Onboards herself.** One setup command, then Vera introduces herself in your channel and walks you through connecting tools, memory, and models.
- **Learns your systems.** Point her at a connected app and — with your approval — she maps its endpoints, auth, and data shapes, then drafts a working skill for it.
- **Runs the analyses.** ARR roll-forwards, forecasts, pipeline and funnel reads, cited company profiles, daily recaps.
- **Delivers finished work.** Reports, docs, diagrams, and visuals that are ready to forward as-is.
- **Keeps herself tidy.** Everything Vera learns lands in a quarantined `skills-live/` folder, gets vetted nightly, and only graduates into the shipped skill set through review.

## Quickstart

```bash
git clone https://github.com/amaniphipps/vera.git
cd vera
./setup/setup.sh
```

Setup ends when Vera says hello — not before. Afterward, `./setup/doctor.sh` tells you the honest state of the install.

## Guardrails are a feature

Vera's rules live in `policy/guardrails.yaml` — data, not prompt text. What she can read, where she can write, what she never touches. Ships read-only; you widen it deliberately.

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
