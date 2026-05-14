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
from collections.abc import Iterable

# 3rd party
import branca.element
import folium
import folium.elements
from domdf_folium_tools import markercluster
from domdf_folium_tools.elements import Preload, add_to, set_id
from domdf_folium_tools.template import SubclassingTemplate
from folium.plugins import LocateControl as FoliumLocateControl
from folium.template import Template
from folium_about_button import AboutControl
from folium_layerscontrol_minimap.toggle import ToggleMinimapLayerControl
from folium_map_search import MapSearchControl, MapSearchProvider
from folium_map_swap_control import MapSwapControl
from folium_zoom_state import BasemapFromURL, ZoomStateJS, ZoomStateMap

# this package
from nhle_map import constants
from nhle_map.nls_basemaps import os10k, os1250, os2500

__all__ = ["LayerControl", "MarkerLoadingJS", "make_map"]


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
	"""
	Adds javascript logic for marker loading and display.

	:param max_zoom: The map's maximum zoom level.
	:param layers: Data about layers to add to the map.
	"""

	# TODO: get max_zoom from the map itself?

	def __init__(self, max_zoom: int, layers: Iterable[constants.Dataset]):
		super().__init__()
		self.max_zoom = max_zoom
		self._layers = layers

	default_js = [
			(
					"awesome_markers_js",
					"https://unpkg.com/leaflet-extra-markers@1.2.2/dist/js/leaflet.extra-markers.js",
					),
			("nhle_markers_js", "static/js/markers.js"),
			("layer_data_js_js", "static/js/layer_data.js"),
			("nhle_id_lookup", "data/nhle_id_lookup.js"),
			]

	default_css = [
			(
					"awesome_markers_css",
					"https://unpkg.com/leaflet-extra-markers@1.2.2/dist/css/leaflet.extra-markers.min.css",
					),
			]

	_template = Template(
			"""
        {% macro script(this, kwargs) %}
            const MAX_ZOOM = {{ this.max_zoom }};

            const progress = document.getElementById('progress')
            var modal = bootstrap.Modal.getOrCreateInstance(progress)
            var progressBar = document.getElementById('progress-bar');

            console.log('start creating markers: ' + window.performance.now());
            {{ this._parent.get_name() }}.addLayer(marker_cluster_nhle);

			{% for layer in this._layers -%}
			{{ this._parent.get_name() }}.addLayer(marker_cluster_{{ layer.identifier }});
			{% endfor %}

            var loaded_ids = [];

			load_new_markers().then(function (result){
				console.log("All markers loaded")
				});

            // {{ this._parent.get_name() }}.on('zoomend', load_new_markers);
            {{ this._parent.get_name() }}.on('moveend', load_new_markers);

        {% endmacro %}
""",
			)


class MarkerGroup(markercluster.MarkerGroup):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._name = "MarkerCluster"  # To keep old variable names


class LayerControl(ToggleMinimapLayerControl):
	"""
	Customised layer control.

	Shows minimap preview for base layers, and opens/closes on click not mouseover.
	"""

	control_class_name = "customlayercontrol"

	default_js = ToggleMinimapLayerControl.default_js + [(
			"custom_layer_control.js",
			"static/js/custom_layer_control.js",
			)]


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
					attr='Map &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
					),
			"osm_carto",
			)

	m = Map(
			location=(52.561928, -1.464854),
			minZoom=9,
			maxZoom=MAX_ZOOM,
			zoom_start=11,
			wheelPxPerZoomLevel=80,
			tiles=osm_tiles,
			control_scale=True,  # prefer_canvas=True,
			max_bounds=True,
			min_lat=constants.MIN_LAT - 2,
			min_lon=constants.MIN_LNG - 2,
			max_lat=constants.MAX_LAT + 2,
			max_lon=constants.MAX_LNG + 3,
			)

	set_id(os10k, "os10k").add_to(m)
	set_id(os1250, "os1250").add_to(m)
	set_id(os2500, "os2500").add_to(m)
	# set_id(os25inch, "os25inch").add_to(m)

	preloads = Preload()
	# preloads.add_preload("https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/images/marker-icon.png", "image")
	# preloads.add_preload("https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/images/marker-icon-2x.png", "image")
	# preloads.add_preload("https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/images/marker-shadow.png", "image")
	preloads.add_preload("https://unpkg.com/leaflet-extra-markers@1.2.2/dist/img/markers_default.png", "image")
	preloads.add_preload("https://unpkg.com/leaflet-extra-markers@1.2.2/dist/img/markers_shadow.png", "image")
	preloads.add_to(m)

	# TODO: layer selection background colours to match pins/polygons
	# TODO: handle polygons

	mcg = markercluster.MarkerCluster(
			chunkedLoading=True,
			chunk_progress_function="updateProgressBar",
			max_cluster_radius_function="getClusterRadius",
			control=False,
			show=False,
			)
	add_to(mcg, m, "nhle")

	# TODO: for BPN and COI, show polygon on click. Or always show?
	# TODO: make layer dialog wider to show full names
	layer: constants.Dataset
	for layer in constants.LAYERS:

		add_to(
				MarkerGroup(
						cluster=mcg,
						show=False,
						name=layer.layer_label,
						),
				m,
				layer.identifier,
				)

	MarkerLoadingJS(max_zoom=MAX_ZOOM, layers=constants.LAYERS).add_to(m)
	ZoomStateJS(setup_basemap_state=True).add_to(m)
	LocateControl().add_to(m)
	AboutControl("aboutModal").add_to(m)
	search_provider = MapSearchProvider(
			layer=mcg,
			map=m,
			viewbox=f"{constants.MIN_LNG},{constants.MIN_LAT},{constants.MAX_LNG},{constants.MAX_LAT}",
			feature_type="settlement",
			)
	MapSearchControl(
			provider=search_provider,
			auto_complete_delay=1000,  # Effectively turns off autocomplete to comply with Nominatum TOS
			show_marker=False,
			max_suggestions=15,
			search_label="Enter town or list entry name",
			disable_enter_search=True,  # Otherwise markers don't appear 🤷
			close_on_submit=True,
			).add_to(m)
	MapSwapControl(
			maps={
					'<i class="fa-solid fa-fire fa-fw"></i> Heatmap': "/heatmap.html",
					# '<i class="fa-solid fa-map fa-fw"></i> Default': '/',
					},
			).add_to(m)

	# TODO: track layers in URL parameters (pack into int, one bit per layer)

	layer_control = add_to(LayerControl(), m, "basemap")
	BasemapFromURL(osm_tiles.tile_name, layer_control).add_to(m)

	return m


class LocateControl(FoliumLocateControl):
	default_css = [
			(
					"fontawesome_css",
					"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.7.2/css/all.min.css",
					),
			] + FoliumLocateControl.default_css

	def __init__(self):
		super().__init__(icon="fa-solid fa-location-crosshairs")

	def get_name(self) -> str:
		return "locate_control"
