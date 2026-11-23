#!/usr/bin/env bash
# Isolated Graphify CLI + MCP installer for Vera.
# Uses uv to provision standalone Python 3.12 + graphifyy[mcp] without touching system Python.
#
# Usage:
#   install_graphify.sh [--runtime opencode|hermes|generic|none] [--repo PATH] [--hermes-home PATH] [--dry-run]

set -euo pipefail

RUNTIME="none"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --runtime) RUNTIME="$2"; shift 2 ;;
    --repo) REPO_ROOT="$2"; shift 2 ;;
    --hermes-home) HERMES_HOME="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) grep '^#' "$0" | head -12; exit 0 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
done

export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

say()  { printf '%s\n' "$*"; }
ok()   { printf '  [ok] %s\n' "$*"; }
warn() { printf '  [warn] %s\n' "$*"; }
die()  { printf '  [fail] %s\n' "$*" >&2; exit 1; }

find_bin() {
  local name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    command -v "$name"
    return 0
  fi
  for p in "$HOME/.local/bin/$name" "$HOME/.cargo/bin/$name"; do
    if [ -x "$p" ]; then
      printf '%s\n' "$p"
      return 0
    fi
  done
  return 1
}

run_cmd() {
  if [ "$DRY_RUN" = 1 ]; then
    say "  [dry-run] $*"
  else
    "$@"
  fi
}

say "Graphify setup (isolated uv + Python 3.12; system Python untouched)"

# 1. Ensure uv is present
UV_BIN="$(find_bin uv || true)"
if [ -n "$UV_BIN" ]; then
  ok "uv found: $UV_BIN"
else
  command -v curl >/dev/null || die "curl is required to install uv"
  say "  installing uv..."
  if [ "$DRY_RUN" = 1 ]; then
    say "  [dry-run] curl -LsSf https://astral.sh/uv/install.sh | sh"
    UV_BIN="$HOME/.local/bin/uv"
  else
    curl -LsSf https://astral.sh/uv/install.sh | sh || die "uv install failed"
    UV_BIN="$(find_bin uv || true)"
    [ -n "$UV_BIN" ] || die "uv installed but not found in PATH or ~/.local/bin"
    ok "uv installed: $UV_BIN"
  fi
fi

# 2. Install graphifyy[mcp] with standalone Python 3.12
GRAPHIFY_BIN="$(find_bin graphify || true)"
MCP_BIN="$(find_bin graphify-mcp || true)"
if [ -n "$GRAPHIFY_BIN" ] && [ -n "$MCP_BIN" ]; then
  ok "graphify + graphify-mcp already installed ($MCP_BIN)"
else
  say "  installing graphifyy[mcp] into isolated Python 3.12 tool env..."
  run_cmd "$UV_BIN" tool install --python 3.12 "graphifyy[mcp]" || die "graphifyy[mcp] install failed"
  if [ "$DRY_RUN" = 1 ]; then
    GRAPHIFY_BIN="$HOME/.local/bin/graphify"
    MCP_BIN="$HOME/.local/bin/graphify-mcp"
  else
    GRAPHIFY_BIN="$(find_bin graphify || true)"
    MCP_BIN="$(find_bin graphify-mcp || true)"
    [ -n "$GRAPHIFY_BIN" ] && [ -n "$MCP_BIN" ] || die "graphify binaries missing after install (try: $UV_BIN tool update-shell)"
    ok "installed: $GRAPHIFY_BIN and $MCP_BIN"
  fi
fi

# 3. Verify binaries run cleanly
if [ "$DRY_RUN" = 0 ]; then
  "$GRAPHIFY_BIN" --help >/dev/null 2>&1 || die "graphify --help failed"
  "$MCP_BIN" --help >/dev/null 2>&1 || die "graphify-mcp --help failed"
  ok "verified graphify and graphify-mcp CLI entrypoints"
fi

# 4. Wire runtime MCP config
case "$RUNTIME" in
  opencode)
    # Locate opencode.jsonc / opencode.json in repo or parent workspace dir
    OC_CFG=""
    for candidate in "$REPO_ROOT/opencode.jsonc" "$REPO_ROOT/opencode.json" \
                     "$(dirname "$REPO_ROOT")/opencode.jsonc" "$(dirname "$REPO_ROOT")/opencode.json"; do
      if [ -f "$candidate" ]; then
        OC_CFG="$candidate"
        break
      fi
    done
    if [ -z "$OC_CFG" ]; then
      OC_CFG="$REPO_ROOT/opencode.jsonc"
    fi
    if [ "$DRY_RUN" = 1 ]; then
      say "  [dry-run] wire graphify-mcp ($MCP_BIN) into $OC_CFG under mcp.servers.graphify"
    else
      python3 - "$OC_CFG" "$MCP_BIN" <<'PY'
import json, os, re, sys

cfg_path, mcp_bin = sys.argv[1], sys.argv[2]
entry = {
    "type": "local",
    "command": [mcp_bin],
}

if not os.path.exists(cfg_path):
    data = {
        "$schema": "https://opencode.ai/config.json",
        "mcp": {"servers": {"graphify": entry}},
    }
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"  [ok] created {cfg_path} with mcp.servers.graphify")
    sys.exit(0)

raw = open(cfg_path, "r", encoding="utf-8").read()
# Strip // line comments outside strings to inspect existing JSONC structure
def strip_comments(text):
    out, i, in_str, esc = [], 0, False, False
    while i < len(text):
        ch = text[i]
        if in_str:
            out.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            i += 1
        else:
            if ch == '"':
                in_str = True
                out.append(ch)
                i += 1
            elif text[i:i+2] == "//":
                while i < len(text) and text[i] != "\n":
                    i += 1
            else:
                out.append(ch)
                i += 1
    return "".join(out)

parsed = json.loads(strip_comments(raw))
servers = parsed.get("mcp", {}).get("servers", {})
if "graphify" in servers:
    print(f"  [ok] {cfg_path} already has mcp.servers.graphify")
    sys.exit(0)

# Comment-preserving insertion before final closing brace when "mcp" is absent,
# or clean JSON rewrite fallback if "mcp" already exists.
if "mcp" not in parsed:
    idx = raw.rfind("}")
    if idx != -1:
        before = raw[:idx].rstrip()
        comma = "," if before and not before.endswith("{") and not before.endswith(",") else ""
        block = (
            f'{comma}\n  "mcp": {{\n'
            f'    "servers": {{\n'
            f'      "graphify": {json.dumps(entry)}\n'
            f'    }}\n'
            f'  }}\n'
        )
        updated = before + block + raw[idx:]
        # Validate result parses cleanly
        json.loads(strip_comments(updated))
        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"  [ok] added mcp.servers.graphify to {cfg_path}")
        sys.exit(0)

parsed.setdefault("mcp", {}).setdefault("servers", {})["graphify"] = entry
with open(cfg_path, "w", encoding="utf-8") as f:
    json.dump(parsed, f, indent=2)
    f.write("\n")
print(f"  [ok] updated mcp.servers.graphify in {cfg_path}")
PY
    fi
    ;;
  hermes)
    HERMES_CFG="$HERMES_HOME/config.yaml"
    if [ "$DRY_RUN" = 1 ]; then
      say "  [dry-run] register graphify-mcp ($MCP_BIN) in $HERMES_CFG"
    elif [ -f "$HERMES_CFG" ]; then
      PY_BIN="python3"
      if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
        PY_BIN="$REPO_ROOT/.venv/bin/python"
      fi
      "$PY_BIN" - "$HERMES_CFG" "$MCP_BIN" <<'PY' || warn "could not auto-edit $HERMES_CFG (register capability/mcp.graphify.json manually)"
import shutil, sys, yaml

cfg_path, mcp_bin = sys.argv[1], sys.argv[2]
with open(cfg_path, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f) or {}

mcp = data.setdefault("mcp", {})
if "graphify" in mcp:
    print(f"  [ok] {cfg_path} already defines mcp.graphify")
    sys.exit(0)

shutil.copy2(cfg_path, cfg_path + ".bak-graphify")
mcp["graphify"] = {
    "command": mcp_bin,
    "args": [],
    "env": {"GRAPHIFY_QUERY_LOG_DISABLE": "1"},
}
with open(cfg_path, "w", encoding="utf-8") as f:
    yaml.safe_dump(data, f, sort_keys=False)
print(f"  [ok] registered mcp.graphify in {cfg_path}")
PY
    else
      warn "$HERMES_CFG not found; copy capability/mcp.graphify.json into your Hermes MCP config later"
    fi
    ;;
  generic|none)
    ok "skipping runtime MCP wiring (--runtime $RUNTIME); MCP template is at capability/mcp.graphify.json"
    ;;
  *)
    die "unknown runtime: $RUNTIME (expected opencode|hermes|generic|none)"
    ;;
esac

say "Graphify ready."
