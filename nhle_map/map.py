#!/usr/bin/env python3
#
#  map.py
"""
Map generation.
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
from collections import OrderedDict
from typing import Any, NamedTuple

# 3rd party
import branca.element
import folium
import folium.elements
from domdf_folium_tools.elements import set_id
from domdf_folium_tools.template import SubclassingTemplate
from folium.plugins import LocateControl as FoliumLocateControl
from folium.plugins import MarkerCluster as FoliumMarkerCluster
from folium.template import Template
from folium_zoom_state import ZoomStateJS, ZoomStateMap

__all__ = ["Components", "Map", "MarkerCluster", "MarkerLoadingJS", "make_map", "render_figure"]


class Map(ZoomStateMap):

	# Remove outdated bootstrap and unused glyphicons and awesome markers

	default_js = [
			("leaflet", "https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"),
			]

	default_css = [
			("leaflet_css", "https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css"),
			]

	_template = SubclassingTemplate(
			"""
        {% macro header(this, kwargs) %}
        {% endmacro %}
        """,
			base_template=ZoomStateMap._template,
			)

	def get_name(self) -> str:
		return "map"


class MarkerCluster(FoliumMarkerCluster):
	"""
	Customised MarkerCluster plugin with support for ``chunkProgress`` and ``maxClusterRadius`` functions.
	"""

	# TODO: params in docstring

	_template = Template(
			"""
        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = L.markerClusterGroup(
                {{ this.options|tojavascript }}
            );
            {%- if this.icon_create_function is not none %}
            {{ this.get_name() }}.options.iconCreateFunction =
                {{ this.icon_create_function.strip() }};
            {%- endif %}
			{%- if this.chunk_progress_function is not none %}
            {{ this.get_name() }}.options.chunkProgress =
                {{ this.chunk_progress_function.strip() }};
            {%- endif %}
			{%- if this.max_cluster_radius_function is not none %}
            {{ this.get_name() }}.options.maxClusterRadius =
                {{ this.max_cluster_radius_function.strip() }};
            {%- endif %}
        {% endmacro %}
        """,
			)

	def __init__(
			self,
			name: str | None = None,
			overlay: bool = True,
			control: bool = True,
			show: bool = True,
			icon_create_function: str | None = None,
			chunk_progress_function: str | None = None,
			max_cluster_radius_function: str | None = None,
			options: dict[str, Any] | None = None,
			**kwargs: Any,
			):
		super().__init__(
				name=name,
				overlay=overlay,
				control=control,
				show=show,
				icon_create_function=icon_create_function,
				options=options,
				**kwargs,
				)

		self.chunk_progress_function = chunk_progress_function
		self.max_cluster_radius_function = max_cluster_radius_function

	def get_name(self) -> str:
		return "markers"


class MarkerLoadingJS(folium.elements.JSCSSMixin, branca.element.MacroElement):

	def __init__(self, max_zoom: int):
		super().__init__()
		self.max_zoom = max_zoom

	default_js = [
			("nhle_markers_js", "markers.js"),
			("listed_buildings_id_lookup", "output/data/listed_buildings_id_lookup.js"),
			]

	_template = Template(
			"""
        {% macro script(this, kwargs) %}
            const MAX_ZOOM = {{ this.max_zoom }};

            const progress = document.getElementById('progress')
            var modal = bootstrap.Modal.getOrCreateInstance(progress)
            var progressBar = document.getElementById('progress-bar');

            console.log('start creating markers: ' + window.performance.now());
            map.addLayer(markers);

            var loaded_ids = [];

            load_new_markers()

            // map.on('zoomend', load_new_markers);
            map.on('moveend', load_new_markers);

        {% endmacro %}
""",
			)


class Components(NamedTuple):
	"""
	Figure elements produced by :func:`~.render_figure`.
	"""

	#: Header tags
	header: str
	#: Page body tags
	body: str
	#: Javascript code to insert within `<script>` tags.
	script: str
	#: Script tags to load external javascript
	scripts: str


def render_figure(figure: branca.element.Figure) -> Components:
	"""
	Render a figure for insertion into another template (flask, jinja2 etc.).

	:param figure:
	"""

	for child in figure._children.values():
		child.render()

	header_elems = OrderedDict()
	js_libs = branca.element.Element()
	js_libs._parent = figure

	for name, elem in figure.header._children.items():
		if isinstance(elem, branca.element.JavascriptLink):
			js_libs.add_child(elem, name)
		else:
			header_elems[name] = elem

	figure.header._children = header_elems

	return Components(
			header=figure.header.render(),
			body=figure.html.render(),
			script=figure.script.render(),
			scripts=js_libs.render(),
			)


def make_map() -> folium.Map:
	"""
	Make the listed buildings folium map.
	"""

	MAX_ZOOM = 18

	osm_tiles = set_id(
			folium.TileLayer(
					tiles="OpenStreetMap",
					name="OpenStreetMap",
					# show=False,
					max_zoom=MAX_ZOOM,
					max_native_zoom=18,
					),
			"osm_carto",
			)

	m = Map(
			location=(52.561928, -1.464854),
			minZoom=10,
			maxZoom=MAX_ZOOM,
			zoom_start=13,
			wheelPxPerZoomLevel=80,
			tiles=osm_tiles,
			)

	MarkerCluster(
			chunkedLoading=True,
			chunk_progress_function="updateProgressBar",
			max_cluster_radius_function="getClusterRadius",
			show=False,
			).add_to(m)

	MarkerLoadingJS(max_zoom=MAX_ZOOM).add_to(m)

	ZoomStateJS(setup_basemap_state=True).add_to(m, embed_script=True)  # TODO: copy external script

	LocateControl().add_to(map)

	return m


class LocateControl(FoliumLocateControl):
	default_css = [
			(
					"fontawesome_css",
					"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.2.0/css/all.min.css",
					),
			] + FoliumLocateControl.default_css

	def __init__(self):
		super().__init__(icon="fas fa-location-crosshairs")

	def get_name(self) -> str:
		return "locate_control"
