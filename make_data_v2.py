# 3rd party
import pyogrio

# this package
from nhle_map.data import chunk_data

gdf = pyogrio.read_dataframe("National_Heritage_List_for_England_NHLE_v02_VIEW_8753755809632832301.geojson")

print(gdf.head())

chunk_data(
		gdf,
		range(49, 55),
		range(-7, 3),
		"output/data",
		)
