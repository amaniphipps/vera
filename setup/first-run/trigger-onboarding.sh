#!/usr/bin/env bash
# Fire Vera's onboarding hello as a real first message.
# Local:  ./setup/first-run/trigger-onboarding.sh
# Slack:  start the gateway (hermes gateway) and DM the bot "hello" —
#         meet-vera takes it from there.
set -euo pipefail
hermes chat --oneshot -q "Setup just finished installing you in a new workspace. Load the meet-vera skill and begin onboarding, step by step."
