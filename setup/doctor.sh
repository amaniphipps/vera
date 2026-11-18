#!/usr/bin/env bash
# Vera doctor - is this install honest?
# Prints a pass/warn/fail table. Exit 0 = healthy, 1 = something needs you.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
CONFIG="$HERMES_HOME/config.yaml"
ENVF="$HERMES_HOME/.env"
FAILS=0; WARNS=0

pass() { printf '  PASS  %s\n' "$*"; }
warn() { printf '  WARN  %s\n' "$*"; WARNS=$((WARNS+1)); }
fail() { printf '  FAIL  %s\n' "$*"; FAILS=$((FAILS+1)); }

say_section() { printf '\n%s\n' "$*"; }

say_section "Runtime"
if command -v hermes >/dev/null; then
  pass "hermes: $(hermes --version 2>/dev/null | head -1 || echo present)"
else
  fail "hermes not on PATH"
fi
command -v python3 >/dev/null && pass "python3 present" || fail "python3 missing"

say_section "Config & secrets"
[ -f "$CONFIG" ] && pass "config.yaml exists" || fail "config.yaml missing at $CONFIG"
if [ -f "$CONFIG" ] && grep -q '^  default: .\+' "$CONFIG"; then
  pass "model.default set: $(grep '^  default:' "$CONFIG" | head -1 | awk '{print $2}')"
else
  fail "config.yaml has no model.default"
fi
if [ -f "$ENVF" ]; then
  keys=$(grep -cE '^[A-Z_]+=.' "$ENVF" 2>/dev/null || true); keys=${keys:-0}
  [ "$keys" -gt 0 ] && pass ".env has $keys key(s) set" || warn ".env exists but looks empty"
  if grep -qE '(your-key-here|placeholder|CHANGEME)' "$ENVF" 2>/dev/null; then
    warn ".env still contains placeholder values"
  fi
else
  fail ".env missing at $ENVF"
fi

say_section "Skills"
count=$(find "$HERMES_HOME/skills" -mindepth 3 -maxdepth 3 -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
[ "${count:-0}" -ge 5 ] && pass "$count skills installed" || warn "only $count skills found (expected 5)"
manifest_report=$(python3 - "$HERMES_HOME" <<'PYEOF'
import glob, os, sys
try:
    import yaml
except ImportError:
    print("noyaml"); sys.exit(0)
home = sys.argv[1]
required = {"name","version","tier","scope","secret_policy","env_layer","provenance"}
tiers = {"draft","candidate","hardened"}
scopes = {"read-only","write-slack","write-external"}
bad = []
files = glob.glob(os.path.join(home, "skills", "*", "*", "skill.yaml"))
for f in sorted(files):
    try:
        d = yaml.safe_load(open(f)) or {}
        missing = required - set(d)
        if missing: bad.append(f"{f}: missing {sorted(missing)}")
        elif d.get("tier") not in tiers: bad.append(f"{f}: bad tier {d.get('tier')}")
        elif d.get("scope") not in scopes: bad.append(f"{f}: bad scope {d.get('scope')}")
    except Exception as e:
        bad.append(f"{f}: {e}")
print(f"checked {len(files)}")
for b in bad: print("BAD " + b)
PYEOF
)
if printf '%s' "$manifest_report" | grep -q '^noyaml'; then
  warn "pyyaml not available - manifest check skipped"
elif printf '%s' "$manifest_report" | grep -q '^BAD'; then
  fail "skill manifests invalid:"; printf '%s\n' "$manifest_report" | grep '^BAD' | sed 's/^/       /'
else
  pass "all skill manifests valid ($(printf '%s' "$manifest_report" | head -1))"
fi
unfilled=$(grep -rlE '^[a-z_]+: *""' "$HERMES_HOME/skills" 2>/dev/null | grep -cE '/org\.yaml$' || true)
[ "${unfilled:-0}" -gt 0 ] && warn "$unfilled org.yaml file(s) have empty slots (fill during onboarding or by hand)" || pass "no empty org slots"

say_section "Policy"
if [ -f "$HERMES_HOME/policy/guardrails.yaml" ]; then
  pass "guardrails.yaml present"
  grep -q 'default: read-only' "$HERMES_HOME/policy/guardrails.yaml" \
    && pass "write posture: read-only (safe default)" \
    || warn "write posture widened - confirm that was a deliberate owner decision"
else
  warn "guardrails.yaml missing - seed: cp $REPO_ROOT/policy/guardrails.example.yaml $HERMES_HOME/policy/guardrails.yaml"
fi

say_section "Secret hygiene"
hits=$(grep -rlE '(xox[baprs]-[A-Za-z0-9-]{10,}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)' \
  "$HERMES_HOME/skills" "$HERMES_HOME/policy" "$HERMES_HOME/knowledge" 2>/dev/null | wc -l | tr -d ' ')
[ "${hits:-0}" -eq 0 ] && pass "no secret-shaped strings outside .env" || fail "$hits file(s) outside .env contain secret-shaped strings"

say_section "Summary"
if [ "$FAILS" -gt 0 ]; then
  printf '  %d FAIL, %d WARN - fix the FAILs and re-run.\n' "$FAILS" "$WARNS"; exit 1
elif [ "$WARNS" -gt 0 ]; then
  printf '  0 FAIL, %d WARN - usable; review warnings when convenient.\n' "$WARNS"; exit 0
else
  printf '  All checks pass.\n'; exit 0
fi
