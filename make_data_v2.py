from collections import defaultdict
import random
import geopandas, pyogrio

gdf = pyogrio.read_dataframe("National_Heritage_List_for_England_NHLE_v02_VIEW_8753755809632832301.geojson")


import json, geopandas, uuid
from shapely.geometry import Point


id_lookup = defaultdict(dict)

def write_chunk(features: list, fp):

	for item in features:
		number = item["ListEntry"]
		name = item["Name"]
		grade = item["Grade"]
		list_date = item["ListDate"]
		link = item["hyperlink"]
		# coord = Point(*item["geometry"]["coordinates"])
		coord = item["geometry"].bounds[:2]
		# data_fp.write(f"{number},{json.dumps(name)},{grade},\"{list_date}\",{link},{coord[0]},{coord[1]}\n")
		fp.write(json.dumps([coord[1], coord[0], number, name, grade, list_date, link]))
		# data_fp.write(json.dumps([coord[1], coord[0], number]))
		fp.write(",\n")
	
	fp.write("]\n")

print(gdf.head())

rng = random.Random("NHLE")

def get_id():
	# return str(uuid.UUID(int=rng.getrandbits(128), version=4))
	return rng.getrandbits(32)

for latitude in range(49, 55):
	for longitide in range(-7, 3):
		id = get_id()
		id_lookup[latitude][longitide] = id
		subset = gdf.cx[longitide:longitide+1, latitude:latitude+1]
		if not len(subset):
			continue

		# print(subset.head())
		print(len(subset))

		with open(f"points_{id}.js", "w", encoding="UTF-8") as data_fp:
			data_fp.write("// Lat,Lng,Number,Name,Grade,ListDate,Link\n")
			data_fp.write(f"var addressPoints{id} = [\n")
			write_chunk(subset.to_dict("records"), data_fp)

with open("id_lookup.json", "w", encoding="UTF-8") as fp:
	json.dump(id_lookup, fp, indent=2)
