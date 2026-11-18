# Deploying Vera

Four supported ways to run her. All of them end at the same place: a Hermes
runtime with the Vera layer (skills, persona, policy, knowledge) installed
into `HERMES_HOME`.

| Path | Best for | Starts with |
|---|---|---|
| Local CLI | Trying Vera on your own machine | `./setup/setup.sh` |
| Local Slack gateway | A team Slack, hosted on your machine | `./setup/setup.sh --platform slack` |
| Docker | A server or NAS you own | `docker build -f deploy/docker/Dockerfile -t vera .` |
| Railway | Always-on, no server to mind | `railway up` |

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

Vera is content, not a fork. Anything that runs Hermes Agent can host her:

- **Hermes desktop app** - run `./setup/setup.sh` against the same
  `HERMES_HOME` the app uses (default `~/.hermes`), then pick Vera's persona
  and skills up in the app. The setup only adds files and backs up any config
  it touches.
- **An existing Hermes install** - same thing: setup detects `hermes` on PATH
  and layers Vera in without reinstalling. `--update` refreshes just the
  skills later.
- **Other platforms** - WhatsApp, SMS, GroupMe, Teams and more are upstream
  Hermes features, not wired here. The Slack path in `policy/profiles/` is
  the pattern to copy; Vera herself can walk you through it (ask her).

The contract any harness must honor: Vera's files land in `HERMES_HOME`
(`skills/`, `personas/`, `policy/`, `knowledge/`), her rules stay in
`policy/guardrails.yaml`, and `skills-live/` stays quarantined until a human
promotes from it.
