#!/usr/bin/env bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]:-$0}")" || exit 1 ; pwd -P )

python3 $parent_path/../src/mmum_fetch_data.py
python3 $parent_path/../src/mb_fetch_data.py

python3 $parent_path/../src/mb_transform.py
python3 $parent_path/../src/mmum_transform.py

python3 $parent_path/../src/aggregate.py
