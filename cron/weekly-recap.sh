#!/usr/bin/env bash
# Weekly recap - Friday afternoon, the week in one report.
# Runs Fridays at 16:00 local; delivers a self-contained HTML report file.
#
# Create it:
#   hermes cron create '0 16 * * 5' \
#     --name weekly-recap \
#     --skill briefings \
#     --deliver slack:C0123456789 \
#     'Build the weekly recap: this week'"'"'s numbers from the connected systems, compiled into one self-contained HTML file. Deliver the file plus a three-line summary in-channel.'
#
# Notes:
# - The HTML ships as a file upload in Slack - forward-as-is ready.
# - Adjust the hour to your timezone/week rhythm; Vera reads VERA_TIMEZONE
#   from .env when reasoning about "this week."
