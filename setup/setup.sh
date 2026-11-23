#!/usr/bin/env bash
# Vera - one-command setup.
# git clone <repo> && cd vera && ./setup/setup.sh
#
# What this does, in plain terms:
#   1. Checks your machine has what Vera needs (and installs Hermes if missing).
#   2. Asks a few questions: model provider + key, platform, your domain.
#   3. Writes two small files (config.yaml, .env) and copies Vera's skills in.
#   4. Proves it worked: Vera introduces herself. Setup is not done until
#      you see her say hello.
#
# Flags:
#   --profile local|docker   how to run Hermes (default: local)
#   --platform cli|slack     first platform to wire (default: cli)
#   --runtime hermes|opencode|generic  target runtime (default: auto-detect, ask if ambiguous)
#   --with-plannotator       install standalone plannotator binary for plan review (verified by SHA256)
#   --non-interactive        read all answers from env vars (see .env.example)
#   --update                 refresh Vera's skills into an existing install
#   --with-rea               also set up the optional REA capability (needs node)
#   --with-plannotator       also install standalone plannotator binary
#   --with-graphify          also install Graphify CLI/MCP (uv + isolated Python 3.12)
#   --runtime <name>         hermes | opencode | generic | auto (default: auto)

set -euo pipefail

# ── Args ─────────────────────────────────────────────────────────────
PROFILE="${VERA_PROFILE:-local}"
PLATFORM="${VERA_PLATFORM:-cli}"
NONINTERACTIVE=0
UPDATE=0
WITH_REA=0
WITH_GRAPHIFY=0
RUNTIME="${VERA_RUNTIME:-auto}"
WITH_PLANNOTATOR=0
while [ $# -gt 0 ]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2 ;;
    --platform) PLATFORM="$2"; shift 2 ;;
    --runtime) RUNTIME="$2"; shift 2 ;;
    --with-plannotator) WITH_PLANNOTATOR=1; shift ;;
    --with-graphify) WITH_GRAPHIFY=1; shift ;;
    --non-interactive) NONINTERACTIVE=1; shift ;;
    --update) UPDATE=1; shift ;;
    --with-rea) WITH_REA=1; shift ;;
    -h|--help) grep '^#' "$0" | head -25; exit 0 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
CONFIG="$HERMES_HOME/config.yaml"
ENVF="$HERMES_HOME/.env"

say()  { printf '%s\n' "$*"; }
ok()   { printf '  [ok] %s\n' "$*"; }
warn() { printf '  [warn] %s\n' "$*"; }
die()  { printf '  [fail] %s\n' "$*" >&2; exit 1; }

ask() { # ask <var> <prompt> [default] - never echoes secrets back
  local var="$1" prompt="$2" default="${3:-}"
  if [ "$NONINTERACTIVE" = 1 ]; then
    eval "val=\"\${$var:-$default}\""
  else
    if [ -n "$default" ]; then printf '%s [%s]: ' "$prompt" "$default" >&2
    else printf '%s: ' "$prompt" >&2; fi
    read -r val </dev/tty || val="$default"
    val="${val:-$default}"
  fi
  eval "$var=\"$val\""
}

say ""
say "Vera setup - a RevOps teammate that grows with you."
say "Repo: $REPO_ROOT"
say "Hermes home: $HERMES_HOME"
say ""

# ── 1. Preflight ─────────────────────────────────────────────────────
say "1/6  Preflight"
case "$(uname -s)" in Darwin|Linux) ok "OS: $(uname -s)" ;; *) die "macOS or Linux required (Windows: use WSL)" ;; esac
command -v curl    >/dev/null || die "curl missing"
command -v python3 >/dev/null || die "python3 missing (install 3.11+)"
ok "python3: $(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
if [ "$WITH_REA" = 1 ]; then
  command -v node >/dev/null || die "node missing - required for --with-rea (or drop the flag)"
  ok "node: $(node --version)"
fi
if [ "$PROFILE" = "docker" ]; then
  command -v docker >/dev/null || die "docker missing - install Docker Desktop or use --profile local"
  ok "docker present"
fi

# ── 2. Hermes runtime ────────────────────────────────────────────────
say "2/6  Hermes runtime"
if command -v hermes >/dev/null; then
  ok "hermes found: $(hermes --version 2>/dev/null | head -1 || echo present)"
else
  if [ "$NONINTERACTIVE" = 1 ]; then
    say "  installing Hermes (upstream installer)…"
    curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash || die "Hermes install failed"
  else
    printf '  Hermes not found. Install it now (official installer)? [Y/n]: ' >&2
    read -r yn </dev/tty || yn="y"
    case "$yn" in
      n|N) die "Hermes is required - install from https://hermes-agent.nousresearch.com/docs then re-run" ;;
      *) curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash || die "Hermes install failed" ;;
    esac
  fi
  command -v hermes >/dev/null || die "hermes installed but not on PATH - open a new shell and re-run"
  ok "hermes installed"
fi
mkdir -p "$HERMES_HOME"

# ── 3. Model provider + key ──────────────────────────────────────────
say "3/6  Model provider"
VERA_PROVIDER="${VERA_PROVIDER:-}"
if [ -z "$VERA_PROVIDER" ] && [ "$NONINTERACTIVE" = 0 ]; then
  say "  1) openrouter  (recommended - one key, many models)"
  say "  2) anthropic   3) openai   4) gemini"
  ask VERA_PROVIDER "  Choose" "openrouter"
fi
VERA_PROVIDER="${VERA_PROVIDER:-openrouter}"
case "$VERA_PROVIDER" in
  openrouter) KEYVAR="OPENROUTER_API_KEY"; DEFAULT_MODEL="anthropic/claude-sonnet-4.5" ;;
  anthropic)  KEYVAR="ANTHROPIC_API_KEY";  DEFAULT_MODEL="claude-sonnet-4-5" ;;
  openai)     KEYVAR="OPENAI_API_KEY";     DEFAULT_MODEL="gpt-4.1" ;;
  gemini)     KEYVAR="GEMINI_API_KEY";     DEFAULT_MODEL="gemini-2.5-pro" ;;
  *) die "unknown provider: $VERA_PROVIDER" ;;
esac
ask VERA_MODEL "  Model (any id your provider serves)" "${VERA_MODEL:-$DEFAULT_MODEL}"
eval "have_key=\"\${$KEYVAR:-}\""
if [ -z "$have_key" ] && ! grep -q "^$KEYVAR=.\+" "$ENVF" 2>/dev/null; then
  ask "$KEYVAR" "  $KEYVAR (not echoed, stored only in $ENVF)" ""
  eval "have_key=\"\${$KEYVAR:-}\""
fi

# Write config.yaml (never clobber: back up first)
if [ -f "$CONFIG" ]; then
  cp "$CONFIG" "$CONFIG.bak-$(date +%Y%m%d%H%M%S)"
  if grep -q '^  default:' "$CONFIG"; then
    ok "config.yaml exists - model left as-is (edit $CONFIG to change)"
  else
    printf 'model:\n  default: %s\n' "$VERA_MODEL" >> "$CONFIG"
    ok "config.yaml: added model.default"
  fi
else
  printf 'model:\n  default: %s\n' "$VERA_MODEL" > "$CONFIG"
  ok "config.yaml written (model: $VERA_MODEL)"
fi

# Append key to .env if we have one and it's missing
touch "$ENVF"; chmod 600 "$ENVF"
if [ -n "$have_key" ] && ! grep -q "^$KEYVAR=" "$ENVF"; then
  printf '%s=%s\n' "$KEYVAR" "$have_key" >> "$ENVF"
  ok "$KEYVAR stored in .env"
else
  ok "$KEYVAR already in .env (or supplied at runtime)"
fi

# ── 4. Vera layer: skills, persona, policy, knowledge ────────────────
say "4/6  Vera layer"
copy_dir() { # copy_dir <src> <dest> - idempotent
  local src="$1" dest="$2"
  if [ -d "$dest" ] && [ "$UPDATE" = 0 ]; then
    ok "$(basename "$dest") already present (use --update to refresh)"
  else
    mkdir -p "$(dirname "$dest")"
    rm -rf "$dest"; cp -R "$src" "$dest"
    ok "$(basename "$dest") installed"
  fi
}
mkdir -p "$HERMES_HOME/skills"
for bucket in onboarding capability-acquisition analysis delivery engineering self-maintenance templates community; do
  copy_dir "$REPO_ROOT/skills/$bucket" "$HERMES_HOME/skills/$bucket"
done
copy_dir "$REPO_ROOT/personas"  "$HERMES_HOME/personas"
copy_dir "$REPO_ROOT/knowledge" "$HERMES_HOME/knowledge"
mkdir -p "$HERMES_HOME/policy"
if [ ! -f "$HERMES_HOME/policy/guardrails.yaml" ]; then
  cp "$REPO_ROOT/policy/guardrails.example.yaml" "$HERMES_HOME/policy/guardrails.yaml"
  ok "guardrails.yaml seeded (read-only, confirm-before-write - the safe default)"
else
  ok "guardrails.yaml exists - untouched"
fi

# Runtime-local dirs: created empty on purpose. Vera fills these as she works.
# They are never shipped with content in the repo.
mkdir -p \
  "$HERMES_HOME/skills-live" \
  "$HERMES_HOME/knowledge/graph/entities/business" \
  "$HERMES_HOME/knowledge/graph/entities/glossary" \
  "$HERMES_HOME/knowledge/graph/entities/people" \
  "$HERMES_HOME/knowledge/graph/entities/systems" \
  "$HERMES_HOME/knowledge/graph/evidence"
ok "runtime dirs created (skills-live, knowledge/graph)"

# ── 5. Platform ──────────────────────────────────────────────────────
say "5/6  Platform: $PLATFORM"
case "$PLATFORM" in
  cli)
    ok "local CLI only - add platforms later (docs/CONNECTING-TOOLS.md)" ;;
  slack)
    if ! grep -q '^SLACK_BOT_TOKEN=xoxb-.\+' "$ENVF" 2>/dev/null; then
      ask SLACK_BOT_TOKEN "  Slack bot token (xoxb-…)" ""
      ask SLACK_APP_TOKEN "  Slack app token (xapp-…)" ""
      [ -n "${SLACK_BOT_TOKEN:-}" ] && printf 'SLACK_BOT_TOKEN=%s\n' "$SLACK_BOT_TOKEN" >> "$ENVF"
      [ -n "${SLACK_APP_TOKEN:-}" ] && printf 'SLACK_APP_TOKEN=%s\n' "$SLACK_APP_TOKEN" >> "$ENVF"
    fi
    ok "tokens in .env - start the gateway and DM Vera; she onboards in-channel" ;;
  *) die "unknown platform: $PLATFORM (cli|slack; other platforms are upstream Hermes - see docs/DEPLOYMENT.md)" ;;
esac
ask VERA_SERVE_ONLY_DOMAIN "  Restrict Vera to one email domain? (blank = everyone)" ""
[ -n "${VERA_SERVE_ONLY_DOMAIN:-}" ] && printf 'VERA_SERVE_ONLY_DOMAIN=%s\n' "$VERA_SERVE_ONLY_DOMAIN" >> "$ENVF"

# ── 5b. Runtime selection + optional plan review ────────────────────
say "Runtime selection: $RUNTIME"
case "$RUNTIME" in
  auto)
    if command -v hermes >/dev/null && [ -f "$REPO_ROOT/opencode.jsonc" -o -f "$REPO_ROOT/../opencode.jsonc" ]; then
      warn "both Hermes and OpenCode detected - onboarding will ask which to use (never guesses)"
    elif command -v opencode >/dev/null || [ -f "$REPO_ROOT/opencode.jsonc" -o -f "$REPO_ROOT/../opencode.jsonc" ]; then
      say "  OpenCode markers present - use the OpenCode path in docs (opencode.jsonc skills array + OPENCODE.md)"
    fi ;;
  hermes|opencode|generic) ok "target runtime: $RUNTIME" ;;
  *) die "unknown runtime: $RUNTIME (hermes|opencode|generic|auto)" ;;
esac
if [ "$WITH_PLANNOTATOR" = 1 ]; then
  say "  Installing standalone plannotator binary (SHA256-verified, no Node/Bun required)…"
  PLANNOTATOR_VERSION="${PLANNOTATOR_VERSION:-v0.29.2}"
  mkdir -p "$REPO_ROOT/.tools/plannotator"
  BASE="https://github.com/backnotprop/plannotator/releases/download/$PLANNOTATOR_VERSION"
  case "$(uname -s)-$(uname -m)" in
    Darwin-arm64) ASSET="plannotator-darwin-arm64.gz" ;;
    Darwin-x86_64) ASSET="plannotator-darwin-x64.gz" ;;
    Linux-x86_64) ASSET="plannotator-linux-x64.gz" ;;
    Linux-aarch64|Linux-arm64) ASSET="plannotator-linux-arm64.gz" ;;
    *) die "unsupported platform for --with-plannotator (install manually)" ;;
  esac
  ( cd "$REPO_ROOT/.tools/plannotator" \
    && curl -fsSL "$BASE/$ASSET" -o plannotator.gz \
    && curl -fsSL "$BASE/$ASSET.sha256" -o plannotator.sha256 \
    && gunzip -kf plannotator.gz && chmod +x plannotator ) \
    || die "plannotator install failed"
  ok "plannotator installed at .tools/plannotator/plannotator (loopback-only, sharing/AI disabled by default)"
else
  say "  Skipping plannotator install (opt-in via --with-plannotator; Build It falls back to inline review with consent)"
fi
if [ "$WITH_GRAPHIFY" = 1 ]; then
  TARGET_RT="$RUNTIME"
  [ "$TARGET_RT" = "auto" ] && TARGET_RT="hermes"
  "$REPO_ROOT/setup/install_graphify.sh" --runtime "$TARGET_RT" --repo "$REPO_ROOT" --hermes-home "$HERMES_HOME" \
    || warn "graphify install did not complete (retry via ./setup/install_graphify.sh)"
else
  say "  Skipping Graphify install (opt-in via --with-graphify or provisioned on demand during system study)"
fi

# ── 6. Visible success ───────────────────────────────────────────────
say "6/6  First run - Vera says hello"
if [ "$NONINTERACTIVE" = 1 ] || [ "${VERA_SKIP_HELLO:-0}" = 1 ]; then
  warn "non-interactive: skipping hello. Run it yourself:"
  say "       hermes chat -q 'Setup just finished. Run your meet-vera onboarding.'"
else
  printf '  Run Vera'\''s hello now? [Y/n]: ' >&2
  read -r yn </dev/tty || yn="y"
  case "$yn" in
    n|N) say "  Skipped. Anytime: hermes chat -q 'Run your meet-vera onboarding.'" ;;
    *)
      ( cd "$HERMES_HOME" && hermes chat --oneshot -q \
        "Setup just finished installing you in a new workspace. Load the meet-vera skill and deliver your step 1 hello message exactly as the skill directs." ) \
        && ok "Vera is live." \
        || warn "hello didn't complete - run ./setup/doctor.sh to see why"
      ;;
  esac
fi

say ""
say "Setup complete. Next:"
say "  • Chat:        hermes"
say "  • Health:      $REPO_ROOT/setup/doctor.sh"
say "  • Add tools:   docs/CONNECTING-TOOLS.md"
say "  • Your rules:  $HERMES_HOME/policy/guardrails.yaml"
if [ "$PROFILE" = "docker" ]; then
  say ""
  say "Docker profile - run Vera in a container instead:"
  say "  • Build:  docker build -f deploy/docker/Dockerfile -t vera ."
  say "  • Run:    docker run -d --env-file $ENVF -v vera-data:/opt/data vera"
  say "  • Detail: docs/DEPLOYMENT.md (Docker + Railway)"
fi
