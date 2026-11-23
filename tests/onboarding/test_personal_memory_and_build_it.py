#!/usr/bin/env python3
"""Acceptance checks for personal onboarding, multi-store memory, and build-it."""
import os
import re
import sys

import yaml

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PASSED = 0
FAILED = []


def check(name, condition, detail=""):
    global PASSED
    if condition:
        PASSED += 1
        print(f"  PASS  {name}")
    else:
        FAILED.append(name)
        print(f"  FAIL  {name} {detail}")


def read(rel):
    with open(os.path.join(REPO, rel)) as f:
        return f.read()


def main():
    meet = re.sub(r"\s+", " ", read("skills/onboarding/meet-vera/SKILL.md"))
    check("onboarding asks the person's name verbatim",
          "What should I call you?" in meet)
    check("onboarding waits and never infers identity from metadata",
          "wait for the answer" in meet and
          "Never infer" in meet and "machine" in meet)
    check("name enters the working profile and confirmed durable memory",
          "working profile immediately" in meet and
          "confirmed-admin-statement" in meet and "reading it back" in meet)
    check("declining a name or memory is respected",
          "decline" in meet and "respect that" in meet)
    check("onboarding permits multiple memory stores",
          "one or several stores at once" in meet and
          "memory/stores.yaml" in meet and "default write store" in meet)

    registry = yaml.safe_load(read("memory/stores.example.yaml"))
    stores = registry["stores"]
    check("registry supports at least four memory backends",
          len(stores) >= 4 and len({s["id"] for s in stores}) == len(stores))
    check("local files are the safe default write store",
          registry["default_write_store"] == "local-files" and
          next(s for s in stores if s["id"] == "local-files")["enabled"] is True)
    check("optional stores ship disabled and read-only",
          all((not s["enabled"]) and (not s["write"])
              for s in stores if s["id"] != "local-files"))
    check("multi-store recall is exhaustive, sourced, and conflict-safe",
          registry["recall"] == {"read_all_enabled": True,
                                 "require_provenance": True,
                                 "on_conflict": "ask"})
    check("no secret values in the registry template",
          all("credential_env" not in s or not str(s["credential_env"]).startswith("sk-")
              for s in stores))

    curator = re.sub(r"\s+", " ", read("skills/self-maintenance/memory-curator/SKILL.md"))
    for phrase in ["What should I call you?", "every enabled readable store",
                   "Never silently choose", "Forget X", "draft-tier"]:
        check(f"memory-curator rule: {phrase}", phrase in curator)

    build = re.sub(r"\s+", " ", read("skills/capability-acquisition/build-it/SKILL.md"))
    for phrase in ["Reverse-engineer what is necessary", "smallest vertical slice",
                   "Obtain approval before implementation", "test the success path",
                   "status: unreviewed", "A plan is not a build"]:
        check(f"build-it rule: {phrase}", phrase in build)

    required = {"name", "version", "tier", "scope", "secret_policy", "env_layer", "provenance"}
    for skill in ("memory-curator", "build-it"):
        base = ("skills/self-maintenance/" if skill == "memory-curator"
                else "skills/capability-acquisition/")
        manifest = yaml.safe_load(read(base + skill + "/skill.yaml"))
        check(f"{skill} manifest valid", required <= set(manifest) and
              manifest["tier"] == "hardened" and manifest["name"] == skill)

    for runtime in ("hermes", "opencode", "generic"):
        profile = yaml.safe_load(read(f"deploy/runtimes/{runtime}.yaml"))
        check(f"{runtime} permits multiple memory stores",
              profile.get("memory-selection") == "multiple")

    persona_raw = read("personas/vera.md")
    persona = re.sub(r"\s+", " ", persona_raw)
    for phrase in [
        "## Who you are",
        "## How you see RevOps",
        "RevOps exists to generate, protect, and scale revenue.",
        "Where is the revenue, and how does this create, protect, or accelerate it?",
        "Strategy", "Systems", "People", "Execution",
        "policy/guardrails.yaml", "analysis-validator", "voice-curator", "brand-design",
        "## Voice and personality",
        "docs/VOICE-AND-TONE.md",
        "Claim Compressor",
    ]:
        check(f"persona includes: {phrase}", phrase in persona)
    check("persona has zero em-dashes", "—" not in persona_raw)

    vt_raw = read("docs/VOICE-AND-TONE.md")
    vt = re.sub(r"\s+", " ", vt_raw)
    for phrase in [
        "## 1. The Five Voice Anchors",
        "## 2. The Claim Compressor Rule",
        "## 3. Condensed Replies & The Three Pre-Send Tests",
        "The 5-Second Test",
        "The Follow-Up Test",
        "The Approver Test",
        "## 6. Functional Emoji Grammar",
        "## 7. High-EQ Thread & Room Manners",
        "## 8. The Anti-Claude / Anti-AI Kill List",
    ]:
        check(f"VOICE-AND-TONE.md includes: {phrase}", phrase in vt)
    check("VOICE-AND-TONE.md has zero em-dashes", "—" not in vt_raw)

    vc_raw = read("skills/self-maintenance/voice-curator/SKILL.md")
    check("voice-curator references VOICE-AND-TONE.md and Claim Compressor",
          "docs/VOICE-AND-TONE.md" in vc_raw and "Claim Compressor" in vc_raw)
    check("voice-curator links the canonical voice examples",
          "../../onboarding/meet-vera/examples/voice-examples.md" in vc_raw)
    vc_ex_raw = read("skills/onboarding/meet-vera/examples/voice-examples.md")
    check("voice-examples covers all 5 registers with zero em-dashes",
          all(h in vc_ex_raw for h in [
              "## 1. Social, banter, and team belonging",
              "## 2. Executive & analytical readout",
              "## 3. Multi-task parallel dispatch",
              "## 4. New capability / integration live",
              "## 5. Serious register",
          ]) and "—" not in vc_ex_raw)

    bd_raw = read("skills/delivery/brand-design/SKILL.md")
    check("brand-design includes banned_phrases and Claim Compressor",
          "banned_phrases" in bd_raw and "Claim Compressor" in bd_raw and "—" not in bd_raw)

    print(f"\n{PASSED} passed, {len(FAILED)} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
