#!/bin/bash

set -e

source venv/bin/activate
python3 allen_edmonds_price_tracker/get_prices.py
python3 allen_edmonds_price_tracker/update_data_extracts.py

git add data
git commit -m "Update prices $(date -u --iso-8601=seconds)"
git push origin master
