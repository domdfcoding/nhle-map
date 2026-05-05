# stdlib
import json

# 3rd party
import folium
import folium.plugins
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


class HeatMapWithTime(folium.plugins.HeatMapWithTime):
	default_js = folium.plugins.HeatMapWithTime.default_js + [("nhle_heatmap", "static/js/heatmap.js")]

	_template = Template(
			"""
        {% macro script(this, kwargs) %}

            var times = {{this.times}};

            {{this._parent.get_name()}}.timeDimension = L.timeDimension(
                {times : times, currentTime: new Date(1)}
            );

            var {{this._control_name}} = new L.Control.TimeDimensionCustom({{this.index}}, {
                autoPlay: {{this.auto_play}},
                backwardButton: {{this.backward_button}},
                displayDate: {{this.display_index}},
                forwardButton: {{this.forward_button}},
                limitMinimumRange: {{this.limit_minimum_range}},
                limitSliders: {{this.limit_sliders}},
                loopButton: {{this.loop_button}},
                maxSpeed: {{this.max_speed}},
                minSpeed: {{this.min_speed}},
                playButton: {{this.play_button}},
                playReverseButton: {{this.play_reverse_button}},
                position: "{{this.position}}",
                speedSlider: {{this.speed_slider}},
                speedStep: {{this.speed_step}},
                styleNS: "{{this.style_NS}}",
                timeSlider: {{this.time_slider}},
                timeSliderDragUpdate: {{this.time_slider_drag_update}},
                timeSteps: {{this.index_steps}}
                })
                .addTo({{this._parent.get_name()}});

                {# var {{this.get_name()}} = new TDHeatmap({{this.data}}, #}
                var {{this.get_name()}} = new TDHeatmap(heatmapData,
                {heatmapOptions: {
                        radius: {{this.radius}},
                        blur: {{this.blur}},
                        minOpacity: {{this.min_opacity}},
                        maxOpacity: {{this.max_opacity}},
                        scaleRadius: {{this.scale_radius}},
                        useLocalExtrema: {{this.use_local_extrema}},
                        defaultWeight: 1,
                        {% if this.gradient %}gradient: {{ this.gradient }}{% endif %}
                    }
                });

        {% endmacro %}
        """,
			)


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
		coords = list(map(float, numpy.round(item["geometry"].bounds[:2], 10)))[::-1]
		points.append([*coords, 0.00001])  # TODO: divide 300,000 by area of England
	# points.extend(list(map(float, numpy.round(item["geometry"].bounds[:2], 10)))[::-1] for item in group.to_dict("records"))
	if points:
		index.append(timestamp.strftime("%Y"))
		heatmap_data.append(points)

output_dir = PathPlus("output")

copy_static_files(output_dir / "static")

m = folium.Map(
		location=(52.561928, -1.464854),
		minZoom=7,
		zoom_start=7,
		wheelPxPerZoomLevel=80,
		control_scale=True,
		)

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

hm.add_to(m)
m.add_js_link("heatmap_data", "data/heatmap.js")

output_dir.joinpath("heatmap.html").write_clean(m.get_root().render())

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
