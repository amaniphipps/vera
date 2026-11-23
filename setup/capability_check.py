#!/usr/bin/env python3
"""Capability checks for Vera — shared by doctor.sh and onboarding diagnosis.

Reads capability/core-capabilities.yaml + deploy/runtimes/<runtime>.yaml and
runs read-only probes against the runtime root. Never prints secret values;
checks key existence only.

Usage:
  capability_check.py --repo /path/to/vera [--runtime hermes|opencode|generic]
                      [--hermes-home PATH] [--json]

Exit codes: 0 = all core capabilities pass, 1 = a core capability failed,
2 = usage/startup error.
"""
import argparse
import json
import os
import shutil
import sys

import yaml

CORE_KEYS = ["OPENROUTER_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]
BUCKETS = ["onboarding", "capability-acquisition", "analysis", "delivery",
           "engineering", "self-maintenance", "community"]
GRAPH_DIRS = ["knowledge/graph/entities/business", "knowledge/graph/entities/glossary",
              "knowledge/graph/entities/people", "knowledge/graph/entities/systems",
              "knowledge/graph/evidence"]


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def expand(value, repo, hermes_home):
    if not isinstance(value, str):
        return value
    return (value.replace("<repo>", repo)
                 .replace("$HERMES_HOME", hermes_home or ""))


def detect_runtime(repo, hermes_home):
    """Return (runtime, confidence). Ambiguous -> ('unknown', 'ambiguous')."""
    scores = {"hermes": 0, "opencode": 0}
    if shutil.which("hermes"):
        scores["hermes"] += 1
    if shutil.which("opencode"):
        scores["opencode"] += 1
    if hermes_home and os.path.isfile(os.path.join(hermes_home, "config.yaml")):
        scores["hermes"] += 2
    for marker in ("opencode.json", "opencode.jsonc", ".opencode"):
        if os.path.exists(os.path.join(repo, marker)):
            scores["opencode"] += 2
            break
    if scores["hermes"] == 0 and scores["opencode"] == 0:
        return "unknown", "none"
    if scores["hermes"] > scores["opencode"]:
        return "hermes", "high" if scores["hermes"] >= 3 else "medium"
    if scores["opencode"] > scores["hermes"]:
        return "opencode", "high" if scores["opencode"] >= 3 else "medium"
    return "unknown", "ambiguous"


def env_key_present(key, env_file):
    if os.environ.get(key):
        return True
    if env_file and os.path.isfile(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith(key + "=") and len(line.strip()) > len(key) + 1:
                    return True
    return False


def probe(cap_id, root, repo, profile):
    """Return (status, detail). status: pass | fail | info | manual."""
    support = profile.get("capabilities", {}).get(cap_id, "native")

    def root_path(rel):
        return os.path.join(root, rel)

    if cap_id == "skills-bundled":
        if support == "config":
            # OpenCode config may live at the repo root or any ancestor
            # (a parent directory's opencode.jsonc can expose this repo's skills).
            cfg_dirs = []
            d = repo
            while True:
                cfg_dirs.append(d)
                parent = os.path.dirname(d)
                if parent == d:
                    break
                d = parent
            for cfg_dir in cfg_dirs:
                for name in ("opencode.jsonc", "opencode.json"):
                    cfg = os.path.join(cfg_dir, name)
                    if os.path.isfile(cfg):
                        with open(cfg) as f:
                            text = f.read()
                        missing = [b for b in BUCKETS if "skills/" + b not in text]
                        if missing:
                            return "fail", f"{name} skills array missing buckets: {', '.join(missing)}"
                        return "pass", f"{cfg} covers all {len(BUCKETS)} buckets"
            return "fail", "no opencode.jsonc/opencode.json with a skills array (searched repo and ancestors)"
        count = 0
        for bucket in BUCKETS:
            bdir = root_path(os.path.join("skills", bucket))
            for dirpath, _dirnames, filenames in os.walk(bdir):
                count += filenames.count("SKILL.md")
        if count >= 40:
            return "pass", f"{count} skills installed"
        return "fail", f"only {count} skills found under {root}/skills (expected >= 40)"

    if cap_id == "skills-quarantine":
        return ("pass", "skills-live/ present") if os.path.isdir(root_path("skills-live")) \
            else ("fail", f"missing {root}/skills-live")

    if cap_id == "knowledge-graph":
        missing = [d for d in GRAPH_DIRS if not os.path.isdir(root_path(d))]
        return ("pass", "graph dirs present") if not missing \
            else ("fail", "missing: " + ", ".join(missing))

    if cap_id == "policy-guardrails":
        path = root_path("policy/guardrails.yaml")
        if not os.path.isfile(path):
            return "fail", f"missing {path} (seed from policy/guardrails.example.yaml)"
        try:
            data = load_yaml(path)
            posture = (data or {}).get("writes", {}).get("default", "unknown")
            return "pass", f"guardrails present, write posture: {posture}"
        except Exception as e:
            return "fail", f"guardrails.yaml does not parse: {e}"

    if cap_id == "working-profile":
        return ("pass", "memory/ present") if os.path.isdir(root_path("memory")) \
            else ("fail", f"missing {root}/memory")

    if cap_id == "model-provider":
        env_file = expand(profile.get("env-file"), repo, os.environ.get("HERMES_HOME", ""))
        present = [k for k in CORE_KEYS if env_key_present(k, env_file)]
        return ("pass", f"provider key present ({len(present)})") if present \
            else ("fail", "no provider key in environment or env file")

    if cap_id == "tool-connections":
        # Onboarding records deferral in the working profile; doctor reports
        # configured MCP servers if the runtime config declares any.
        for name in ("opencode.jsonc", "opencode.json"):
            cfg = os.path.join(repo, name)
            if os.path.isfile(cfg):
                with open(cfg) as f:
                    text = f.read()
                if '"mcp"' in text:
                    return "pass", "MCP configuration present"
        return "info", "none detected (connect during onboarding, or defer explicitly)"

    # Enhanced capabilities: availability comes from the profile, never a FAIL.
    if support == "native":
        if cap_id == "nightly-vetting":
            return "info", "schedule via hermes cron (cron/nightly-skill-vetter.sh)"
        if cap_id == "slack-gateway":
            env_file = expand(profile.get("env-file"), repo, os.environ.get("HERMES_HOME", ""))
            if env_key_present("SLACK_BOT_TOKEN", env_file) and env_key_present("SLACK_APP_TOKEN", env_file):
                return "pass", "slack tokens present"
            return "info", "available; tokens not configured"
        return "info", "available"
    if support == "optional":
        return "info", "optional; not verified by doctor"
    if support in ("degraded", "manual"):
        return "info", "on-demand" if support == "degraded" else "manual setup required"
    return "info", "unavailable on this runtime"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--runtime", choices=["hermes", "opencode", "generic"])
    ap.add_argument("--hermes-home", default=os.environ.get("HERMES_HOME", ""))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    repo = os.path.abspath(args.repo)
    contract_path = os.path.join(repo, "capability", "core-capabilities.yaml")
    if not os.path.isfile(contract_path):
        print(f"error: {contract_path} not found", file=sys.stderr)
        return 2
    contract = load_yaml(contract_path)

    hermes_home = args.hermes_home or os.path.expanduser("~/.hermes")
    if args.runtime:
        runtime, confidence = args.runtime, "selected"
    else:
        runtime, confidence = detect_runtime(repo, hermes_home)
        if runtime == "unknown":
            runtime = "generic"
            confidence = "fallback (no runtime detected; using generic profile)"

    profile_path = os.path.join(repo, "deploy", "runtimes", runtime + ".yaml")
    if not os.path.isfile(profile_path):
        print(f"error: runtime profile {profile_path} not found", file=sys.stderr)
        return 2
    profile = load_yaml(profile_path)

    root = expand(profile.get("runtime-root", "<repo>"), repo, hermes_home)
    override_root = os.environ.get("VERA_RUNTIME_ROOT")
    if override_root:
        root = os.path.abspath(override_root)
        # With an isolated runtime root, env files resolve inside it too
        # (keeps probes and tests honest about which install they inspect).
        profile = dict(profile)
        profile["env-file"] = os.path.join(root, ".env")
    rows = []
    core_fails = 0
    for cap in contract["capabilities"]:
        cap_id = cap["id"]
        if cap_id == "tool-connections":
            status, detail = probe(cap_id, root, repo, profile)
            # core capability: info (not yet connected) does not fail doctor;
            # onboarding resolves it via connect-or-defer.
        else:
            status, detail = probe(cap_id, root, repo, profile)
        if cap["tier"] == "core" and status == "fail":
            core_fails += 1
        rows.append({"id": cap_id, "tier": cap["tier"], "status": status,
                     "detail": detail, "degraded": cap.get("degraded", "")})

    result = {"runtime": runtime, "confidence": confidence,
              "runtime_root": root, "capabilities": rows,
              "core_failures": core_fails}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Runtime: {runtime} ({confidence})")
        print(f"Runtime root: {root}")
        for r in rows:
            label = {"pass": "PASS", "fail": "FAIL", "info": "INFO", "manual": "MANUAL"}[r["status"]]
            line = f"  {label:6} [{r['tier']:8}] {r['id']}: {r['detail']}"
            if r["status"] == "info" and r["tier"] == "enhanced" and r["degraded"]:
                line += f" — {r['degraded']}"
            print(line)
        print(f"Core failures: {core_fails}")
    return 1 if core_fails else 0


if __name__ == "__main__":
    sys.exit(main())
