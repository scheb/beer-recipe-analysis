for i in {1..1190}
do
	curl "https://www.maischemalzundmehr.de/export.php?id=${i}" -o ./raw_data/${i}.json
done

find ./raw_data -name "*.json" -type 'f' -size 1k -delete
