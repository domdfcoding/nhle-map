# stdlib
import datetime
import json
from typing import Any

# 3rd party
import branca.element
import domdf_folium_tools.heatmap
import folium
import geopandas
import numpy
import pandas
import pyogrio
from domdf_folium_tools import set_branca_random_seed
from domdf_folium_tools.elements import render_figure, set_id
from domdf_python_tools.paths import PathPlus
from folium_zoom_state import ZoomStateJS

# this package
from nhle_map import constants
from nhle_map.heatmap import HeatMapWithTime, make_data_js
from nhle_map.map import Map
from nhle_map.templates import render_template
from nhle_map.utils import copy_static_files, format_datetime, format_description

set_branca_random_seed("NHLE")

dataset = constants.LISTED_BUILDINGS

assert dataset.geojson_filename is not None
gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(PathPlus("data") / dataset.geojson_filename)

gdf = gdf[["ListEntry", "Grade", "ListDate", "geometry"]].set_index("ListEntry").sort_values("ListDate")
gdf["ListDate"] = pandas.to_datetime(gdf["ListDate"], unit="ms")
# print(gdf.columns)
# print(gdf)

heatmap_data = []
index = []

points = []

for timestamp, group in gdf.groupby(pandas.Grouper(key="ListDate", freq="YE")):
	points = []
	for item in group.to_dict("records"):
		coords = tuple(map(float, numpy.round(item["geometry"].bounds[:2], 10)))[::-1]
		points.append((*coords, 0.00001))  # TODO: divide 300,000 by area of England
	if points:
		index.append(timestamp.strftime("%Y"))
		heatmap_data.append(points)

output_dir = PathPlus("output")

copy_static_files(output_dir / "static")

output_dir.joinpath("data/heatmap.js").write_clean(make_data_js(heatmap_data))

# TODO: transition to markers at highest zoom levels

hm = HeatMapWithTime(
		heatmap_data,
		data_variable="heatmapData",
		index=index,
		use_local_extrema=True,
		radius=3,
		scale_radius=True,
		speed_step=1,
		min_speed=1,
		gradient={
				0.25: "rgb(0,0,255)",
				0.55: "rgb(0,255,0)",
				0.75: "rgb(0,255,128)",
				0.99: "yellow",
				1.0: "rgb(255,0,0)",
				},
		)

hm2 = domdf_folium_tools.heatmap.HeatLayerWithTime(
		heatmap_data,
		data_variable="heatmapData",
		index=index,
		speed_step=1,
		# radius=20,
		# blur=1.0,
		# gradient={
		# 		0.25: "rgb(0,0,255)",
		# 		0.55: "rgb(0,255,0)",
		# 		0.75: "rgb(0,255,128)",
		# 		0.99: "yellow",
		# 		1.0: "rgb(255,0,0)",
		# 		},
		)

MAX_ZOOM = 20

osm_tiles = set_id(
		folium.TileLayer(
				tiles="OpenStreetMap",
				name="OpenStreetMap",
				# show=False,
				max_zoom=MAX_ZOOM,
				max_native_zoom=19,
				referrerPolicy="strict-origin-when-cross-origin",
				attr='Map &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
				),
		"osm_carto",
		)

for heatmap, filename in [(hm, "heatmap.html"), (hm2, "heatmap2.html")]:

	m = Map(
			location=(52.561928, -1.464854),
			minZoom=5,
			maxZoom=MAX_ZOOM,
			zoom_start=7,
			wheelPxPerZoomLevel=80,
			tiles=osm_tiles,
			control_scale=True,
			)

	heatmap.add_to(m)
	m.add_js_link("heatmap_data", "data/heatmap.js")

	# TODO: to start/to end buttons for TimeDimension

	ZoomStateJS(setup_basemap_state=False).add_to(m)
	# TODO: AboutControl("aboutModal").add_to(m)
	# TODO: OSM onlysearch_provider = MapSearchProvider(
	# 	layer=mcg,
	# 	map=m,
	# 	viewbox=f"{constants.MIN_LNG},{constants.MIN_LAT},{constants.MAX_LNG},{constants.MAX_LAT}",
	# 	feature_type="settlement",
	# 	)

	root: branca.element.Figure = m.get_root()  # type: ignore[assignment]

	layers_data: dict[str, Any] = output_dir.joinpath("data", "meta.json").load_json()
	layer_mod_times = [v.get("dataLastEditDate", -1) for v in layers_data.values()]
	most_recent_modification = datetime.datetime.fromtimestamp(
			max(layer_mod_times) / 1000,
			tz=datetime.timezone.utc,
			)

	map_html = render_template(
			"map.jinja2",
			**render_figure(root)._asdict(),
			title="England Listed Buildings Heatmap",
			layers=[],
			layers_data={},
			most_recent_modification=most_recent_modification,
			generated_date=datetime.datetime.now(tz=datetime.timezone.utc),
			format_description=format_description,
			format_datetime=format_datetime,
			)
	output_dir.joinpath(filename).write_clean(map_html)
