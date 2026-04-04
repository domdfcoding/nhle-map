# 3rd party
import branca.element
import folium
from domdf_folium_tools.elements import set_id
from domdf_python_tools.paths import PathPlus

# this package
from nhle_map.map import Map, MarkerCluster, MarkerLoadingJS, render_figure
from nhle_map.templates import render_template

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

map = Map(
		location=[52.561928, -1.464854],
		minZoom=10,
		maxZoom=MAX_ZOOM,
		zoom_start=13,
		wheelPxPerZoomLevel=80,
		tiles=osm_tiles,
		)

marker_cluster: MarkerCluster = MarkerCluster(
		chunkedLoading=True,
		chunk_progress_function="updateProgressBar",
		max_cluster_radius_function="getClusterRadius",
		show=False,
		).add_to(map)
marker_loading_js: MarkerLoadingJS = MarkerLoadingJS(max_zoom=MAX_ZOOM).add_to(map)

root: branca.element.Figure = map.get_root()  # type: ignore[assignment]

PathPlus("index.html").write_clean(render_template(
		"map.jinja2",
		**render_figure(root)._asdict(),
		))
