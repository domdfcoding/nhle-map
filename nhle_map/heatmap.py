#!/usr/bin/env python3
#
#  heatmap.py
"""
Heatmap generation.
"""
#
#  Copyright © 2026 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import datetime
import json

# 3rd party
import domdf_folium_tools
import domdf_folium_tools.heatmap
import geopandas
import numpy
import pandas
from domdf_python_tools.stringlist import StringList
from folium.template import Template

__all__ = ["HeatMapWithTime", "make_data_js", "prepare_heatmap_data"]


# TODO: allow default_weight to be specified for domdf_folium_tools.heatmap.HeatMapWithTime
class HeatMapWithTime(domdf_folium_tools.heatmap.HeatMapWithTime):  # noqa: D101
	default_js = domdf_folium_tools.heatmap.HeatMapWithTime.default_js + [
			("nhle_heatmap", "static/js/heatmap.js"),
			]

	_template = Template(
			"""
		{% macro script(this, kwargs) %}
			var {{this.get_name()}} = new TDHeatmapCustom(
				heatmapData,
				{heatmapOptions: {{ this.options|tojson(indent=20) }}},
			);
		{% endmacro %}
		""".replace('\t', "    "),
			)


def make_data_js(data: list[list[tuple[float, float, float]]]) -> str:
	"""
	Format the heatmap data (nested list of coordinates, grouped by year) as javascript.

	:param data:
	"""

	heatmap_data_js = StringList("const heatmapData = [")
	with heatmap_data_js.with_indent("    ", 1):
		for month in data:
			heatmap_data_js.append('[')
			with heatmap_data_js.with_indent_size(2):
				for point in month:
					heatmap_data_js.append(json.dumps(point) + ',')
			heatmap_data_js.append("],")

	heatmap_data_js.append(']')

	return str(heatmap_data_js)


def prepare_heatmap_data(gdf: geopandas.GeoDataFrame) -> tuple[list[list[tuple[float, float, float]]], list[str]]:
	"""
	Take the given listed building etc. data and prepare for display in a heatmap, grouped by year.

	:param gdf:

	:returns: Nested list of coordinates, and a list of years.
	"""

	gdf = gdf[["ListEntry", "Grade", "ListDate", "geometry"]].set_index("ListEntry").sort_values("ListDate")
	gdf["ListDate"] = pandas.to_datetime(gdf["ListDate"], unit="ms")
	# print(gdf.columns)
	# print(gdf)

	heatmap_data = []
	index = []

	points = []

	timestamp: datetime.datetime
	for timestamp, group in gdf.groupby(pandas.Grouper(key="ListDate", freq="YE")):
		points = []
		for item in group.to_dict("records"):
			coords = tuple(map(float, numpy.round(item["geometry"].bounds[:2], 10)))[::-1]
			# TODO: use default option rather than specify for every point
			points.append((*coords, 0.00001))  # TODO: divide 300,000 by area of England
		if points:
			index.append(timestamp.strftime("%Y"))
			heatmap_data.append(sorted(points))

	return heatmap_data, index
