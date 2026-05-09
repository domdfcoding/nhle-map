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
import json

# 3rd party
import domdf_folium_tools
import domdf_folium_tools.heatmap
from domdf_python_tools.stringlist import StringList
from folium.template import Template

__all__ = ["HeatMapWithTime", "make_data_js"]


class HeatMapWithTime(domdf_folium_tools.heatmap.HeatMapWithTime):
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


# TODO: run in prepare_data
def make_data_js(data: list[list[tuple[float, float, float]]]) -> str:
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
