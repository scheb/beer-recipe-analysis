#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

# Update max number if necessary
for i in {1..1400}
do
	curl "https://www.maischemalzundmehr.de/export.php?id=${i}" -o $parent_path/../raw_data/mmum/${i}.json
done

find $parent_path/../raw_data/mmum -name "*.json" -type 'f' -size 1k -delete
