#!/usr/bin/env bash
# Daily briefing — the habit that makes a team keep Vera.
# Runs every weekday at 08:00 local; delivers into your platform channel.
#
# Create it:
#   hermes cron create '0 8 * * 1-5' \
#     --name daily-briefing \
#     --skill briefings \
#     --deliver slack:C0123456789 \
#     'Run your briefings skill for today. Post the morning briefing: what moved, what needs attention, what is next. Pull live numbers from the connected systems.'
#
# Notes:
# - Schedule is standard cron: minute hour day month weekday. '0 8 * * 1-5' = 08:00 Mon-Fri.
# - --deliver slack:C0123456789 posts into that channel. Use your own channel ID.
# - Vera needs at least one connected system (CRM, warehouse) for real numbers;
#   with none connected she produces a structure-only briefing and says so.
# - Failure notices follow --deliver unless you set --failure-deliver local.
