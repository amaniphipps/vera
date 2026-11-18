# Deploying Vera

Vera runs on Hermes Agent. Every path below ends at the same place: a Hermes
runtime with the Vera layer (skills, persona, policy, knowledge) installed
into `HERMES_HOME`.

**Start local.** The CLI path is the tested, golden path - Docker and Railway
are optional extras for an always-on team Slack. You do not need them to use
Vera.

| Path | Best for | Starts with |
|---|---|---|
| Local CLI | Trying Vera on your own machine. **Start here.** | `./setup/setup.sh` |
| Local Slack gateway | A team Slack, hosted on your machine | `./setup/setup.sh --platform slack` |
| Docker (optional) | Always-on, a server or NAS you own | `docker build -f deploy/docker/Dockerfile -t vera .` |
| Railway (optional) | Always-on, no server to mind | `railway up` |

Something else (an IDE, a different agent host)? See
[Other harnesses](#other-harnesses).

---

## Local CLI

The quickstart. Vera lives in your terminal; you talk to her with `hermes`.

```bash
git clone https://github.com/amaniphipps/vera.git
cd vera
./setup/setup.sh
hermes
```

Setup installs Hermes if missing, asks for a model provider + key, copies the
Vera layer into `~/.hermes`, and ends with Vera introducing herself.
`./setup/doctor.sh` reports the honest state of the install afterward.

## Local Slack gateway

Same install, plus Slack:

```bash
./setup/setup.sh --platform slack
hermes gateway run
```

You need a Slack app of your own (bot token `xoxb-`, app-level token `xapp-`
for Socket Mode). Create one at https://api.slack.com/apps: enable Socket Mode,
add the bot scopes for reading and posting messages, install it to your
workspace, invite the bot to a channel. Setup stores both tokens in
`~/.hermes/.env`; Vera onboards in-channel on first DM.

## Docker

One image: the official Hermes runtime plus the Vera layer, seeded into a
volume on first boot.

```bash
cp .env.example .env   # fill in your keys
docker build -f deploy/docker/Dockerfile -t vera .
docker run -d --name vera --restart unless-stopped \
  --env-file .env \
  -v vera-data:/opt/data \
  vera
```

- First boot runs `setup/setup.sh --non-interactive` against the volume.
  Answers come from env vars (`VERA_PROVIDER`, `VERA_PLATFORM`, your API key),
  exactly like `--non-interactive` locally.
- For Slack, set `VERA_PLATFORM=slack` plus both Slack tokens in `.env`.
- To chat by CLI instead of running the gateway:
  `docker run -it --rm --env-file .env -v vera-data:/opt/data vera`
- The image only ever *seeds* the volume. After first boot, `/opt/data` is
  yours - skills Vera learns, memory, config changes all live there and
  survive image rebuilds. Re-seed deliberately: delete `.vera-seeded` in the
  volume.
- The base image is pinned as `nousresearch/hermes-agent:latest`. Pin a tag
  (e.g. `:v0.23.2`) in `deploy/docker/Dockerfile` for reproducible deploys.

## Railway

`deploy/railway/railway.toml` builds the same Dockerfile on Railway.

```bash
railway init        # once, to link a project
railway up          # builds + deploys
```

Two one-time steps the config file cannot do for you (dashboard):

1. **Attach a volume mounted at `/opt/data`.** Without it every redeploy
   wipes Vera's memory and learned skills.
2. **Set variables** from `.env.example`: at minimum `OPENROUTER_API_KEY`
   (or another provider key). For Slack add `VERA_PLATFORM=slack`,
   `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`.

Pushing to the repo changes nothing in prod; deploys are `railway up`.

## Other harnesses

Vera works with Hermes today. That is the supported runtime - setup.sh,
doctor.sh, the guardrails model, and the skills-live vetting loop are all
built on it.

She is not welded to it. Everything that makes her Vera is plain files -
markdown skills, a persona file, a YAML policy, a knowledge seed - so porting
her to another agent host is a content job, not a code fork. If you want her
running somewhere else, that is a job you can do *with Vera*: point her at
the target host's skill/persona conventions and she will help you map her
skills, translate her guardrails into the host's policy shape, and flag what
has no equivalent.

Two things any host must honor, however it is implemented:

1. Her rules stay data (`policy/guardrails.yaml`), read-only by default,
   widened only by deliberate owner action.
2. `skills-live/` stays quarantined. Nothing she drafts becomes a shipped
   skill without a vetting pass and a human yes.

Other platforms within Hermes (WhatsApp, SMS, GroupMe, Teams) are upstream
features, not wired here - the Slack path in `policy/profiles/` is the
pattern to copy, and Vera can walk you through it.
