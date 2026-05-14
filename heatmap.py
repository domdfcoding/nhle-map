# stdlib
import datetime
from typing import Any

# 3rd party
import branca.element
from domdf_folium_tools import set_branca_random_seed
from domdf_folium_tools.elements import render_figure
from domdf_python_tools.paths import PathPlus

# this package
from nhle_map.heatmap import make_map
from nhle_map.templates import render_template
from nhle_map.utils import copy_static_files, format_datetime, format_description

# TODO: option to set times and their labels from variables, and then not load the dataframe except in prepare_data

set_branca_random_seed("NHLE")

output_dir = PathPlus("output")
copy_static_files(output_dir / "static")

index = output_dir.joinpath("data/heatmap_index.json").load_json()

# TODO: transition to markers at highest zoom levels
# TODO: to start/to end buttons for TimeDimension
# TODO: save year in URL params
# TODO: heatmap layers as radio not checkbox so one at a time, and save in URL

m = make_map(index)

root: branca.element.Figure = m.get_root()  # type: ignore[assignment]

layers_data: dict[str, Any] = output_dir.joinpath("data", "meta.json").load_json()
layer_mod_times = [v.get("dataLastEditDate", -1) for v in layers_data.values()]
most_recent_modification = datetime.datetime.fromtimestamp(
		max(layer_mod_times) / 1000,
		tz=datetime.timezone.utc,
		)

map_html = render_template(
		"map.jinja2",
		**render_figure(root)._asdict(),
		title="England Listed Buildings Heatmap",
		layers=[],
		layers_data={},
		most_recent_modification=most_recent_modification,
		generated_date=datetime.datetime.now(tz=datetime.timezone.utc),
		format_description=format_description,
		format_datetime=format_datetime,
		)
output_dir.joinpath("heatmap.html").write_clean(map_html)
