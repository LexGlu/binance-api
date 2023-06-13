#!/bin/bash

# export environment variables from .env file (used for cron job to run python script with environment variables from .env file)
export $(grep -v '^#' /usr/src/app/.env | xargs -d '\n')

# Run the command
/usr/local/bin/python /usr/src/app/get_kline_data.py