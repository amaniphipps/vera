#!/usr/bin/env bash
# Nightly skill-vetter - Vera reviews her own learnings while you sleep.
# Runs every night at 02:00 local; delivers a digest only when something changed.
#
# Create it:
#   hermes cron create '0 2 * * *' \
#     --name nightly-skill-vetter \
#     --skill skill-vetter \
#     --deliver slack:C0123456789 \
#     'Run your skill-vetter skill against skills-live/. Mark duplicates, flag anything that touched secrets or tried write-external, and propose promotions. If nothing needs attention, say so in one line.'
#
# Notes:
# - Drafts stay quarantined regardless of what this job proposes.
#   Promotion to skills/ always needs a human yes.
# - Pair with the weekly learnings digest (weekly-learnings-digest.sh) if
#   you want a Sunday summary instead of nightly notes.
