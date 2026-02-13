#!/usr/bin/env bash
# Run the SDE demo from the project directory.
cd "$(dirname "$0")"
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi
exec python3 run.py
