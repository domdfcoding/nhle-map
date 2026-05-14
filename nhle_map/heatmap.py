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
import folium
import geopandas  # type: ignore[import-untyped]
import numpy  # nodep
import pandas  # type: ignore[import-untyped]
from domdf_folium_tools.elements import add_to, set_id
from domdf_python_tools.stringlist import StringList
from folium.elements import JSCSSMixin
from folium.map import Layer
from folium.template import Template
from folium.utilities import TypeJsonValue
from folium_about_button import AboutControl
from folium_map_search import MapSearchControl, OpenStreetMapProvider
from folium_map_swap_control import MapSwapControl
from folium_zoom_state import ZoomStateJS

# this package
from nhle_map import constants
from nhle_map.map import Map

__all__ = ["HeatMapWithTime", "make_data_js", "make_map", "prepare_heatmap_data"]


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


def make_data_js(data: list[list[tuple[float, float]]]) -> str:
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


def prepare_heatmap_data(gdf: geopandas.GeoDataFrame) -> tuple[list[list[tuple[float, float]]], list[str]]:
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

	points: list[tuple[float, float]] = []

	timestamp: datetime.datetime
	for timestamp, group in gdf.groupby(pandas.Grouper(key="ListDate", freq="YE")):
		points = []
		for item in group.to_dict("records"):
			bounds = numpy.round(item["geometry"].bounds[:2], 10)
			coords: tuple[float, float] = tuple(map(float, bounds))[::-1]  # type: ignore[assignment]
			points.append(coords)
		if points:
			index.append(timestamp.strftime("%Y"))
			heatmap_data.append(sorted(points))

	return heatmap_data, index


class GroupedLayerControl(JSCSSMixin, folium.LayerControl):
	r"""
	Creates a GroupedLayerControl object to be added to a folium map.

	.. note::

		The LayerControl should be added last to the map. Otherwise, the GroupedLayerControl and/or the controlled layers may not appear.

	:param groups: Grouped layers to display in the control.
	:param position: The position of the control (one of the map corners).
		Can be 'topleft', 'topright', 'bottomleft' or 'bottomright'.
	:param collapsed: If :py:obj:`True` the control will be collapsed into an icon and expanded on mouse hover or touch.
	:param autoZIndex: If :py:obj:`True` the control assigns zIndexes in increasing order to all of its layers so that the order is preserved when switching them on/off.
	:param draggable: By default the layer control has a fixed position. Set this argument to :py:obj:`True` to allow dragging the control around.
	:param \*\*kwargs: Additional keyword arguments for the javascript class.
	"""

	_template = Template(
			"""
		{% macro script(this, kwargs) %}
			var {{ this.get_name() }}_layers = {
				base_layers : {
					{%- for key, val in this.base_layers.items() %}
					{{ key|tojson }} : {{val}},
					{%- endfor %}
				},
				overlays :  {
					{% for group_name, group_data in this.groups.items() %}
						{{ group_name|tojson }}: {
							{% for layer_name, layer in group_data.items() %}
								{{ layer_name|tojson }}: {{ layer.get_name() }},
							{% endfor %}
						},
					{% endfor %}
				},
			};

			let {{ this.get_name() }} = new L.Control.GroupedLayers(
				{{ this.get_name() }}_layers.base_layers,
				{{ this.get_name() }}_layers.overlays,
				{{ this.options|tojavascript }}
			).addTo({{this._parent.get_name()}});

			{%- if this.draggable %}
			new L.Draggable({{ this.get_name() }}.getContainer()).enable();
			{%- endif %}

		{% endmacro %}
		""".replace('\t', "    "),
			)

	default_js = [
			(
					"groupedlayercontrol-js",
					"https://cdn.jsdelivr.net/gh/ismyrnow/leaflet-groupedlayercontrol@0.6.1/dist/leaflet.groupedlayercontrol.min.js",
					),
			]
	default_css = [
			(
					"groupedlayercontrol-css",
					"https://cdn.jsdelivr.net/gh/ismyrnow/leaflet-groupedlayercontrol@0.6.1/dist/leaflet.groupedlayercontrol.min.css",
					),
			]

	def __init__(
			self,
			groups: dict[str, dict[str, Layer]],
			position: str = "topright",
			collapsed: bool = True,
			autoZIndex: bool = True,
			draggable: bool = False,
			**kwargs: TypeJsonValue,
			):
		super().__init__(
				position=position,
				collapsed=collapsed,
				autoZIndex=autoZIndex,
				draggable=draggable,
				**kwargs,
				)
		self._name = "GroupedLayerControl"
		self.groups = groups


# TODO: do away with index variable in favour of loading from JS
def make_map(index: list[str]) -> folium.Map:  # noqa: PRM002  # TODO
	"""
	Make the listed buildings folium heatmap.
	"""

	# TODO: option to set times and their labels from variables
	# TODO: transition to markers at highest zoom levels
	# TODO: to start/to end buttons for TimeDimension
	# TODO: save year in URL params
	# TODO: heatmap layers as radio not checkbox so one at a time, and save in URL

	MAX_ZOOM = 20

	osm_tiles = set_id(
			folium.TileLayer(
					tiles="OpenStreetMap",
					name="OpenStreetMap",
					# show=False,
					control=False,
					max_zoom=MAX_ZOOM,
					max_native_zoom=19,
					referrerPolicy="strict-origin-when-cross-origin",
					attr='Map &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
					),
			"osm_carto",
			)

	m = Map(
			location=(52.561928, -1.464854),
			minZoom=5,
			maxZoom=MAX_ZOOM,
			zoom_start=7,
			wheelPxPerZoomLevel=80,
			tiles=osm_tiles,
			control_scale=True,
			)

	# set_id(os10k, "os10k").add_to(m)
	# set_id(os1250, "os1250").add_to(m)
	# set_id(os2500, "os2500").add_to(m)
	# # set_id(os25inch, "os25inch").add_to(m)

	td_control = domdf_folium_tools.heatmap.TimeDimensionControl(
			index=index,
			speed_step=1,
			min_speed=1,
			)
	add_to(td_control, m, "heatmap")

	hm = HeatMapWithTime(
			data=None,
			data_variable="heatmapData",
			index=index,
			name="Style 1",  # TODO: proper name
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
			default_weight=0.00001,  # TODO: divide 300,000 by area of England
			)

	add_to(hm, m, "style1")

	hm2 = domdf_folium_tools.heatmap.HeatLayerWithTime(
			data=None,
			data_variable="heatmapData",
			name="Style 2",  # TODO: proper name
			index=index,
			show=False,
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

	add_to(hm2, m, "style2")

	m.add_js_link("heatmap_data", "data/heatmap.js")
	ZoomStateJS(setup_basemap_state=False).add_to(m)
	AboutControl("aboutModal").add_to(m)
	search_provider = OpenStreetMapProvider(
			viewbox=f"{constants.MIN_LNG},{constants.MIN_LAT},{constants.MAX_LNG},{constants.MAX_LAT}",
			feature_type="settlement",
			)
	MapSearchControl(
			provider=search_provider,
			auto_complete_delay=1000,  # Effectively turns off autocomplete to comply with Nominatum TOS
			show_marker=False,
			max_suggestions=15,
			search_label="Enter town or city",
			disable_enter_search=True,  # Otherwise markers don't appear 🤷
			close_on_submit=True,
			).add_to(m)
	MapSwapControl(
			maps={
					# '<i class="fa-solid fa-fire fa-fw"></i> Heatmap': "/heatmap.html",
					'<i class="fa-solid fa-map fa-fw"></i> Default': '/',
					},
			).add_to(m)

	# TODO: track layers in URL parameters (pack into int, one bit per layer)

	layer_control = add_to(
			GroupedLayerControl(
					groups={
							"Heatmap Styles": {
									"Style 1": hm,
									"Style 2": hm2,
									},
							},
					exclusiveGroups=["Heatmap Styles"],
					groupCheckboxes=True,
					collapsed=False,
					),
			m,
			"heatmap",
			)
	# TODO: BasemapFromURL(osm_tiles.tile_name, layer_control).add_to(m)

	return m
