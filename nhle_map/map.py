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

# 3rd party
import branca.element
import folium
import folium.elements
from domdf_folium_tools import markercluster
from domdf_folium_tools.elements import NLSTileLayer, add_to, set_id
from domdf_folium_tools.template import SubclassingTemplate
from folium.plugins import LocateControl as FoliumLocateControl
from folium.template import Template
from folium_layerscontrol_minimap.toggle import ToggleMinimapLayerControl
from folium_zoom_state import BasemapFromURL, ZoomStateJS, ZoomStateMap

# this package
from nhle_map.nls_basemaps import os10k, os1250, os2500

__all__ = ["LocateControl", "Map", "MarkerLoadingJS", "make_map"]


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


class MarkerLoadingJS(folium.elements.JSCSSMixin, branca.element.MacroElement):

	def __init__(self, max_zoom: int):
		super().__init__()
		self.max_zoom = max_zoom

	default_js = [
			("nhle_markers_js", "static/js/markers.js"),
			("listed_buildings_id_lookup", "data/listed_buildings_id_lookup.js"),
			]

	_template = Template(
			"""
        {% macro script(this, kwargs) %}
            const MAX_ZOOM = {{ this.max_zoom }};

            const progress = document.getElementById('progress')
            var modal = bootstrap.Modal.getOrCreateInstance(progress)
            var progressBar = document.getElementById('progress-bar');

            console.log('start creating markers: ' + window.performance.now());
            map.addLayer(marker_cluster_listed_buildings);

            var loaded_ids = [];

            load_new_markers()

            // map.on('zoomend', load_new_markers);
            map.on('moveend', load_new_markers);

        {% endmacro %}
""",
			)


def make_map() -> folium.Map:
	"""
	Make the listed buildings folium map.
	"""

	MAX_ZOOM = 20

	osm_tiles = set_id(
			folium.TileLayer(
					tiles="OpenStreetMap",
					name="OpenStreetMap",
					show=False,
					max_zoom=MAX_ZOOM,
					max_native_zoom=19,
					referrerPolicy="strict-origin-when-cross-origin",
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
			control_scale=True,  # prefer_canvas=True,
			)

	set_id(os10k, "os10k").add_to(m)
	set_id(os1250, "os1250").add_to(m)
	set_id(os2500, "os2500").add_to(m)
	# set_id(os25inch, "os25inch").add_to(m)

	add_to(
			markercluster.MarkerCluster(
					chunkedLoading=True,
					chunk_progress_function="updateProgressBar",
					max_cluster_radius_function="getClusterRadius",
					show=False,
					control=False,
					),
			m,
			"listed_buildings",
			)

	MarkerLoadingJS(max_zoom=MAX_ZOOM).add_to(m)
	ZoomStateJS(setup_basemap_state=True).add_to(m, embed_script=True)  # TODO: copy external script
	LocateControl().add_to(m)

	layer_control = add_to(ToggleMinimapLayerControl(), m, "basemap")
	BasemapFromURL(osm_tiles.tile_name, layer_control).add_to(m)

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
