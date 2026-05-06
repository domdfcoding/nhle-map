# stdlib
import json

# 3rd party
import domdf_folium_tools.heatmap
import folium
import geopandas
import numpy
import pandas
import pyogrio
from domdf_folium_tools import set_branca_random_seed
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from folium.template import Template

# this package
from nhle_map import constants
from nhle_map.utils import copy_static_files

set_branca_random_seed("NHLE")


class HeatMapWithTime(domdf_folium_tools.heatmap.HeatMapWithTime):
	default_js = domdf_folium_tools.heatmap.HeatMapWithTime.default_js[:-1] + [
			("domdf_folium_tools_js", "static/js/domdf-folium-tools.js"),
			("nhle_heatmap", "static/js/heatmap.js"),
			]

	_template = Template(
			"""
		{% macro script(this, kwargs) %}

			var times = {{this.times}};

			{{this._parent.get_name()}}.timeDimension = L.timeDimension(
				{times : times, currentTime: new Date(1)}
			);

			var {{this._control_name}} = new L.Control.TimeDimensionHeatmap(
				{{this.index | tojson}},
				{{ this.control_options | tojson(indent=20) }},
			).addTo({{this._parent.get_name()}});

			var {{this.get_name()}} = new TDHeatmapCustom(
				heatmapData,
				{heatmapOptions: {{ this.heatmap_options|tojson(indent=20) }}},
			);

		{% endmacro %}
		""".replace('\t', "    "),
			)


class HeatLayerWithTime(domdf_folium_tools.heatmap.HeatLayerWithTime):
	default_js = domdf_folium_tools.heatmap.HeatLayerWithTime.default_js[:-1] + [
			("domdf_folium_tools_js", "static/js/domdf-folium-tools.js"),
			]


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


def write_data_js():
	heatmap_data_js = StringList("const heatmapData = [")
	with heatmap_data_js.with_indent("    ", 1):
		for month in heatmap_data:
			heatmap_data_js.append('[')
			with heatmap_data_js.with_indent_size(2):
				for point in month:
					heatmap_data_js.append(json.dumps(point) + ',')
			heatmap_data_js.append("],")

	heatmap_data_js.append(']')

	output_dir.joinpath("data/heatmap.js").write_lines(heatmap_data_js)


# TODO: transition to markers at highest zoom levels

hm = HeatMapWithTime(
		heatmap_data,
		index,
		use_local_extrema=True,
		radius=3,
		scale_radius=True,
		gradient={
				0.25: "rgb(0,0,255)",
				0.55: "rgb(0,255,0)",
				0.75: "rgb(0,255,128)",
				0.99: "yellow",
				1.0: "rgb(255,0,0)",
				},
		)

hm2 = HeatLayerWithTime(
		heatmap_data,
		index,
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

for heatmap, filename in [(hm, "heatmap.html"), (hm2, "heatmap2.html")]:

	m = folium.Map(
			location=(52.561928, -1.464854),
			minZoom=7,
			zoom_start=7,
			wheelPxPerZoomLevel=80,
			control_scale=True,
			)

	heatmap.add_to(m)
	m.add_js_link("heatmap_data", "data/heatmap.js")

	output_dir.joinpath(filename).write_clean(m.get_root().render())
