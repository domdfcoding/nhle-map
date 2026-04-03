# stdlib
from collections import defaultdict

# 3rd party
import pyogrio

# this package
from nhle_map.data import get_chunk_js
from nhle_map.utils import get_id


# stdlib
import json

gdf = pyogrio.read_dataframe("National_Heritage_List_for_England_NHLE_v02_VIEW_8753755809632832301.geojson")


id_lookup = defaultdict(dict)

print(gdf.head())

for latitude in range(49, 55):
	for longitide in range(-7, 3):
		id = get_id()
		id_lookup[latitude][longitide] = id
		subset = gdf.cx[longitide:longitide + 1, latitude:latitude + 1]
		if not len(subset):
			continue

		# print(subset.head())
		print(len(subset))

		with open(f"output/data/listed_buildings_{id}.js", 'w', encoding="UTF-8") as data_fp:
			data_fp.write(get_chunk_js(subset.to_dict("records"), id))

with open("id_lookup.json", 'w', encoding="UTF-8") as fp:
	json.dump(id_lookup, fp, indent=2)
