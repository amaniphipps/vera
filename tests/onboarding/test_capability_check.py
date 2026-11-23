#!/usr/bin/env python3
"""PR 1 tests: capability contract, runtime profiles, probes, doctor.

Run via tests/run.sh (uses the isolated venv). No network, no secrets,
all fixtures under tests/onboarding/fixtures/.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

import yaml

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CHECK = os.path.join(REPO, "setup", "capability_check.py")
DOCTOR = os.path.join(REPO, "setup", "doctor.sh")

PASSED = 0
FAILED = []


def check(name, cond, detail=""):
    global PASSED
    if cond:
        PASSED += 1
        print(f"  PASS  {name}")
    else:
        FAILED.append(name)
        print(f"  FAIL  {name} {detail}")


def run_check(repo, runtime=None, hermes_home=None, extra_env=None, runtime_root=None):
    cmd = [sys.executable, CHECK, "--repo", repo, "--json"]
    if runtime:
        cmd += ["--runtime", runtime]
    env = dict(os.environ)
    if hermes_home:
        env["HERMES_HOME"] = hermes_home
        cmd += ["--hermes-home", hermes_home]
    if extra_env:
        env.update(extra_env)
    if runtime_root:
        env["VERA_RUNTIME_ROOT"] = runtime_root
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    data = json.loads(p.stdout) if p.stdout.strip().startswith("{") else {}
    return p.returncode, data, p.stderr


def seed_runtime_dirs(root):
    for d in ["skills-live", "memory",
              "knowledge/graph/entities/business", "knowledge/graph/entities/glossary",
              "knowledge/graph/entities/people", "knowledge/graph/entities/systems",
              "knowledge/graph/evidence", "policy"]:
        os.makedirs(os.path.join(root, d), exist_ok=True)
    shutil.copy(os.path.join(REPO, "policy", "guardrails.example.yaml"),
                os.path.join(root, "policy", "guardrails.yaml"))


def main():
    # 1. Contract and profiles are valid and aligned.
    contract = yaml.safe_load(open(os.path.join(REPO, "capability", "core-capabilities.yaml")))
    caps = contract["capabilities"]
    ids = [c["id"] for c in caps]
    check("contract: 12 capabilities", len(caps) == 12, f"got {len(caps)}")
    check("contract: 7 core, 5 enhanced",
          sum(c["tier"] == "core" for c in caps) == 7 and
          sum(c["tier"] == "enhanced" for c in caps) == 5)
    check("contract: every capability has verify + degraded",
          all(c.get("verify") and c.get("degraded") for c in caps))
    for rt in ("hermes", "opencode", "generic"):
        prof = yaml.safe_load(open(os.path.join(REPO, "deploy", "runtimes", rt + ".yaml")))
        check(f"profile {rt}: covers every capability",
              set(prof["capabilities"].keys()) == set(ids),
              f"diff: {set(ids) ^ set(prof['capabilities'].keys())}")
        check(f"profile {rt}: buckets match 7, excludes templates+schema",
              len(prof["skill-discovery"]["buckets"]) == 7 and
              prof["skill-discovery"]["exclude"] == ["templates", "schema"])

    # 2. Fresh generic install: seeded dirs + key => all core pass.
    # Generic uses directory-scan skill discovery, so mirror skills/ into the root.
    with tempfile.TemporaryDirectory() as tmp:
        seed_runtime_dirs(tmp)
        for bucket in ["onboarding", "capability-acquisition", "analysis", "delivery",
                       "engineering", "self-maintenance", "community"]:
            shutil.copytree(os.path.join(REPO, "skills", bucket),
                            os.path.join(tmp, "skills", bucket))
        code, data, err = run_check(REPO, runtime="generic", runtime_root=tmp,
                                    extra_env={"OPENROUTER_API_KEY": "test-fixture-key"})
        check("generic fresh install: core failures = 0", data.get("core_failures") == 0,
              f"code={code} err={err} data={json.dumps(data)[:400]}")
        check("generic fresh install: exit 0", code == 0)

    # 3. Missing guardrails is a core FAIL.
    with tempfile.TemporaryDirectory() as tmp:
        seed_runtime_dirs(tmp)
        os.remove(os.path.join(tmp, "policy", "guardrails.yaml"))
        code, data, _ = run_check(REPO, runtime="generic", runtime_root=tmp,
                                  extra_env={"OPENROUTER_API_KEY": "test-fixture-key"})
        rows = {r["id"]: r for r in data.get("capabilities", [])}
        check("missing guardrails: policy-guardrails FAILs",
              rows.get("policy-guardrails", {}).get("status") == "fail")
        check("missing guardrails: exit 1", code == 1)

    # 4. No provider key is a core FAIL.
    with tempfile.TemporaryDirectory() as tmp:
        seed_runtime_dirs(tmp)
        env = {k: "" for k in ["OPENROUTER_API_KEY", "ANTHROPIC_API_KEY",
                               "OPENAI_API_KEY", "GEMINI_API_KEY"]}
        code, data, _ = run_check(REPO, runtime="generic", runtime_root=tmp, extra_env=env)
        rows = {r["id"]: r for r in data.get("capabilities", [])}
        check("no provider key: model-provider FAILs",
              rows.get("model-provider", {}).get("status") == "fail")

    # 5. OpenCode config discovered in an ancestor directory.
    with tempfile.TemporaryDirectory() as tmp:
        parent = os.path.join(tmp, "parent")
        repo = os.path.join(parent, "vera")
        os.makedirs(repo)
        seed_runtime_dirs(repo)
        for bucket in ["onboarding", "capability-acquisition", "analysis", "delivery",
                       "engineering", "self-maintenance", "community"]:
            shutil.copytree(os.path.join(REPO, "skills", bucket),
                            os.path.join(repo, "skills", bucket))
        for tree in ["capability", "deploy"]:
            shutil.copytree(os.path.join(REPO, tree), os.path.join(repo, tree))
        with open(os.path.join(parent, "opencode.jsonc"), "w") as f:
            json.dump({"skills": [f"./vera/skills/{b}" for b in
                                  ["onboarding", "capability-acquisition", "analysis",
                                   "delivery", "engineering", "self-maintenance", "community"]]}, f)
        code, data, err = run_check(repo, runtime="opencode", runtime_root=repo,
                                    extra_env={"OPENROUTER_API_KEY": "test-fixture-key"})
        rows = {r["id"]: r for r in data.get("capabilities", [])}
        check("opencode ancestor config: skills-bundled PASSes",
              rows.get("skills-bundled", {}).get("status") == "pass",
              json.dumps(rows.get("skills-bundled", {})) + err[:200])
        check("opencode ancestor config: core failures = 0", data.get("core_failures") == 0)

    # 6. OpenCode config missing buckets FAILs.
    with tempfile.TemporaryDirectory() as tmp:
        seed_runtime_dirs(tmp)
        for tree in ["capability", "deploy"]:
            shutil.copytree(os.path.join(REPO, tree), os.path.join(tmp, tree))
        with open(os.path.join(tmp, "opencode.jsonc"), "w") as f:
            json.dump({"skills": ["./vera/skills/onboarding"]}, f)
        code, data, err = run_check(tmp, runtime="opencode", runtime_root=tmp,
                                    extra_env={"OPENROUTER_API_KEY": "test-fixture-key"})
        rows = {r["id"]: r for r in data.get("capabilities", [])}
        check("opencode incomplete config: skills-bundled FAILs",
              rows.get("skills-bundled", {}).get("status") == "fail",
              json.dumps(rows.get("skills-bundled", {})) + err[:200])

    # 7. Hermes directory-scan counts real bundled skills.
    with tempfile.TemporaryDirectory() as home:
        for bucket in ["onboarding", "capability-acquisition", "analysis", "delivery",
                       "engineering", "self-maintenance", "community"]:
            src = os.path.join(REPO, "skills", bucket)
            dst = os.path.join(home, "skills", bucket)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
        seed_runtime_dirs(home)
        with open(os.path.join(home, "config.yaml"), "w") as f:
            f.write("model:\n  default: test-model\n")
        code, data, _ = run_check(REPO, runtime="hermes", hermes_home=home,
                                  extra_env={"OPENROUTER_API_KEY": "test-fixture-key"})
        rows = {r["id"]: r for r in data.get("capabilities", [])}
        check("hermes fixture: skills-bundled PASSes (directory scan)",
              rows.get("skills-bundled", {}).get("status") == "pass",
              json.dumps(rows.get("skills-bundled", {})))
        check("hermes fixture: core failures = 0", data.get("core_failures") == 0,
              json.dumps(data)[:400])

    # 8. Enhanced capabilities never FAIL on any runtime.
    for rt in ("hermes", "opencode", "generic"):
        with tempfile.TemporaryDirectory() as tmp:
            seed_runtime_dirs(tmp)
            code, data, _ = run_check(REPO, runtime=rt,
                                      extra_env={"OPENROUTER_API_KEY": "test-fixture-key"})
            bad = [r["id"] for r in data.get("capabilities", [])
                   if r["tier"] == "enhanced" and r["status"] == "fail"]
            check(f"enhanced never FAILs on {rt}", not bad, str(bad))

    # 9. Manifest schema validation across bundled skills.
    schema_required = {"name", "version", "tier", "scope", "secret_policy", "env_layer", "provenance"}
    tiers = {"draft", "candidate", "hardened"}
    scopes = {"read-only", "write-slack", "write-external"}
    bad = []
    checked = 0
    for dirpath, _dirs, files in os.walk(os.path.join(REPO, "skills")):
        if "skill.yaml" in files and "templates" not in dirpath:
            path = os.path.join(dirpath, "skill.yaml")
            checked += 1
            try:
                d = yaml.safe_load(open(path)) or {}
                missing = schema_required - set(d)
                if missing:
                    bad.append(f"{path}: missing {sorted(missing)}")
                elif d.get("tier") not in tiers:
                    bad.append(f"{path}: bad tier {d.get('tier')}")
                elif d.get("scope") not in scopes:
                    bad.append(f"{path}: bad scope {d.get('scope')}")
            except Exception as e:
                bad.append(f"{path}: {e}")
    check(f"manifest schema: {checked} skill.yaml files valid", not bad, "\n".join(bad[:8]))

    # 10. Hygiene: no secret-shaped strings in shipped trees.
    secret_hits = []
    for tree in ("skills", "policy", "knowledge", "deploy", "capability"):
        p = subprocess.run(["grep", "-rlE",
                            r"(xox[baprs]-[A-Za-z0-9-]{10,}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)",
                            os.path.join(REPO, tree)], capture_output=True, text=True)
        if p.stdout.strip():
            secret_hits += p.stdout.strip().splitlines()
    check("hygiene: no secret-shaped strings in shipped trees", not secret_hits, str(secret_hits))

    # 11. Doctor end-to-end on the generic fixture.
    with tempfile.TemporaryDirectory() as tmp:
        seed_runtime_dirs(tmp)
        env = dict(os.environ, OPENROUTER_API_KEY="test-fixture-key")
        p = subprocess.run([DOCTOR, "--runtime", "generic"], capture_output=True, text=True, env=env)
        check("doctor generic on repo fixture: runs and reports",
              "Capabilities" in p.stdout and "Secret hygiene" in p.stdout,
              p.stdout[-300:] + p.stderr[-300:])

    print(f"\n{PASSED} passed, {len(FAILED)} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
