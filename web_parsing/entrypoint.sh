#!/bin/bash

# Set up Python path
export PYTHONPATH=/app:$PYTHONPATH

# Run the scheduler
cd /app/web_parsing
exec python scheduler.py 