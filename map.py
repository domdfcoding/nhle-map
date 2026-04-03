# 3rd party
import folium
from branca.element import Figure, MacroElement
from domdf_folium_tools.elements import set_id
from domdf_python_tools.paths import PathPlus
from folium.elements import JSCSSMixin
from folium.plugins import MarkerCluster
from folium.template import Template

# this package
from nhle_map.templates import render_template

MAX_ZOOM = 18


class Map(folium.Map):

	_template = Template(
			"""
        {% macro header(this, kwargs) %}
        {% endmacro %}

        {% macro html(this, kwargs) %}
            <div class="folium-map" id={{ this.get_name()|tojson }} ></div>
        {% endmacro %}

        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = L.map(
                {{ this.get_name()|tojson }},
                {
                    center: {{ this.location|tojson }},
                    crs: L.CRS.{{ this.crs }},
                    ...{{this.options|tojavascript}}

                }
            );

            {%- if this.control_scale %}
            L.control.scale().addTo({{ this.get_name() }});
            {%- endif %}

            {%- if this.zoom_control_position %}
            L.control.zoom( { position: {{ this.zoom_control|tojson }} } ).addTo({{ this.get_name() }});
            {%- endif %}

            {% if this.objects_to_stay_in_front %}
            function objects_in_front() {
                {%- for obj in this.objects_to_stay_in_front %}
                    {{ obj.get_name() }}.bringToFront();
                {%- endfor %}
            };
            {{ this.get_name() }}.on("overlayadd", objects_in_front);
            $(document).ready(objects_in_front);
            {%- endif %}

        {% endmacro %}
        """,
			)

	def get_name(self) -> str:
		return "map"


class MarkerLoadingJS(JSCSSMixin, MacroElement):

	def __init__(self, max_zoom: int):
		super().__init__()
		self.max_zoom = max_zoom

	default_js = [
			("nhle_markers_js", "markers.js"),
			("listed_buildings_id_lookup", "output/data/listed_buildings_id_lookup.js"),
			] + MarkerCluster.default_js
	default_css = MarkerCluster.default_css[:]
	_template = Template(
			"""

        {% macro script(this, kwargs) %}
const MAX_ZOOM = {{ this.max_zoom }};


    const progress = document.getElementById('progress')
    var modal = bootstrap.Modal.getOrCreateInstance(progress)
    var progressBar = document.getElementById('progress-bar');

    var markers = L.markerClusterGroup({ chunkedLoading: true, chunkProgress: updateProgressBar, maxClusterRadius: getClusterRadius });

    var markerList = [];

    console.log('start creating markers: ' + window.performance.now());
    map.addLayer(markers);

    var loaded_ids = [];

    load_new_markers()

    // map.on('zoomend', load_new_markers);
    map.on('moveend', load_new_markers);

            {% endmacro %}

""",
			)


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

# marker_cluster: MarkerCluster = MarkerCluster().add_to(map)
marker_loading_js: MarkerLoadingJS = MarkerLoadingJS(max_zoom=MAX_ZOOM).add_to(map)

root: Figure = map.get_root()  # type: ignore[assignment]

# TODO: make branca put JS in right place directly
# js_libs = map.default_js + marker_cluster.default_js + marker_loading_js.default_js
js_libs = map.default_js + marker_loading_js.default_js
# marker_cluster.default_js = []
marker_loading_js.default_js = []
map.default_js = []
map.default_css = []

scripts = [folium.JavascriptLink(lib[1]).render() for lib in js_libs]

for child in root._children.values():
	child.render()

PathPlus("index.html").write_clean(
		render_template(
				"map.jinja2",
				header=root.header.render(),
				body=root.html.render(),
				script=root.script.render(),
				scripts='\n'.join(scripts),
				),
		)
