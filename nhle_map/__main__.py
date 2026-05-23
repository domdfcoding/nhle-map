#!/usr/bin/env python3
#
#  __main__.py
"""
Map showing places on the National Heritage List for England.
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
from typing import Any

# 3rd party
from consolekit import CONTEXT_SETTINGS, SuggestionGroup, click_group
from consolekit.options import auto_default_option

__all__ = ["main", "make_map", "prepare_data"]


@click_group(
		cls=SuggestionGroup,
		invoke_without_command=False,
		context_settings={**CONTEXT_SETTINGS, "show_default": True},
		)
def main() -> None:
	"""
	Map showing listed buildings in England and Wales.
	"""


@auto_default_option("-d/-D", "--download/--no-download", is_flag=True)
@main.command()
def prepare_data(download: bool = False) -> None:
	"""
	Prepare data for the map.
	"""

	# 3rd party
	import geopandas  # type: ignore[import-untyped]
	import pyogrio  # type: ignore[import-untyped]
	from domdf_python_tools.paths import PathPlus

	# this package
	from nhle_map import constants, heatmap
	from nhle_map.data import chunk_data, download_data, download_welsh_data

	data_directory = PathPlus("data")

	if download:
		# data_directory is the local data folder, not the processed data within the output folder
		download_data(data_directory)
		download_welsh_data(data_directory)

	output_dir = PathPlus("output")
	output_dir.maybe_make()

	data = [
			constants.LISTED_BUILDINGS,
			constants.PROTECTED_WRECK_SITES,
			constants.BUILDING_PRESERVATION_NOTICES,
			constants.CERTIFICATES_OF_IMMUNITY,
			constants.PARKS_AND_GARDENS,
			constants.BATTLEFIELDS,
			constants.SCHEDULED_MONUMENTS,
			constants.DE_DESIGNATED,
			constants.WORLD_HERITAGE_SITES,
			constants.REGISTERED_LANDSCAPES_WALES,
			]

	chunk_data(
			data,
			range(constants.MIN_LAT, constants.MAX_LAT),
			range(constants.MIN_LNG, constants.MAX_LNG),
			data_directory=data_directory,
			output_directory=output_dir / "data",
			)

	meta_json = data_directory.joinpath("meta.json").load_json()
	layers_data = {}
	for layer in meta_json["layers"]:
		layers_data[layer["name"]] = {
				"description": layer["description"],
				"copyrightText": layer["copyrightText"],
				"dataLastEditDate": layer["editingInfo"]["dataLastEditDate"],
				}

	for layer in [
			constants.BATTLEFIELDS,
			constants.BUILDING_PRESERVATION_NOTICES,
			constants.CERTIFICATES_OF_IMMUNITY,
			]:
		layers_data[layer.geojson_filename_stem]["description"] += "\nEngland Only"

	de_designated_description = "Sites removed from the National Heritage List for England because they no longer met any of the above criteria.\nEngland Only"
	layers_data[constants.DE_DESIGNATED.geojson_filename_stem]["description"] = de_designated_description

	registered_landscape_description = """\
The Register of Historic Landscapes in Wales.

It is a non-statutory, advisory register. Its primary aim is to provide information and raise awareness of an initial selection of the most important and significant historic landscape areas in Wales in order to aid their protection and conservation. This information is intended to help owners, Government, statutory bodies, Local Authorities, developers and all those who are involved with land management and protection to make better-informed decisions about areas on the Register.

Wales Only
"""
	layers_data[constants.REGISTERED_LANDSCAPES_WALES.geojson_filename_stem] = {
			"description": registered_landscape_description,
			}

	output_dir.joinpath("data", "meta.json").dump_json(layers_data, indent=2)

	dataset = constants.LISTED_BUILDINGS
	assert dataset.geojson_filename is not None
	gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(data_directory / dataset.geojson_filename)
	heatmap_data, index = heatmap.prepare_heatmap_data(gdf)
	output_dir.joinpath("data", "heatmap.js").write_clean(heatmap.make_data_js(heatmap_data))
	output_dir.joinpath("data", "heatmap_index.json").dump_json(index)


@auto_default_option("-O", "--output-dir", "output_directory")
@main.command()
def make_map(output_directory: str = "output") -> None:
	"""
	Create the map and write associated files.
	"""

	# stdlib
	import datetime

	# 3rd party
	import branca.element
	from domdf_folium_tools import set_branca_random_seed
	from domdf_folium_tools.elements import render_figure
	from domdf_python_tools.paths import PathPlus

	# this package
	from nhle_map import constants, heatmap
	from nhle_map.map import make_map
	from nhle_map.templates import render_template
	from nhle_map.utils import copy_static_files

	set_branca_random_seed("NHLE")

	output_dir = PathPlus(output_directory)
	output_dir.maybe_make()

	copy_static_files(output_dir / "static")

	layers_data: dict[str, Any] = output_dir.joinpath("data", "meta.json").load_json()
	layer_mod_times = [v.get("dataLastEditDate", -1) for v in layers_data.values()]
	most_recent_modification = datetime.datetime.fromtimestamp(
			max(layer_mod_times) / 1000,
			tz=datetime.timezone.utc,
			)

	m = make_map()
	root: branca.element.Figure = m.get_root()  # type: ignore[assignment]

	map_html = render_template(
			"map.jinja2",
			**render_figure(root)._asdict(),
			title="England and Wales Listed Buildings Map",
			description='Map showing Listed Buildings, Scheduled Monuments, Parks & Gardens, and more from the <a href="https://historicengland.org.uk/listing/the-list/">National Heritage List for England</a>.',
			uses_welsh_data=True,
			layers=constants.LAYERS,
			layers_data=layers_data,
			most_recent_modification=most_recent_modification,
			generated_date=datetime.datetime.now(tz=datetime.timezone.utc),
			)
	output_dir.joinpath("index.html").write_clean(map_html)

	heatmap_m = heatmap.make_map(output_dir.joinpath("data/heatmap_index.json").load_json())
	heatmap_root: branca.element.Figure = heatmap_m.get_root()  # type: ignore[assignment]

	heatmap_html = render_template(
			"map.jinja2",
			**render_figure(heatmap_root)._asdict(),
			title="England Listed Buildings Heatmap",
			description='Heatmap showing Listed Buildings from the <a href="https://historicengland.org.uk/listing/the-list/">National Heritage List for England</a>.',
			uses_welsh_data=False,
			layers=[],
			layers_data={},
			most_recent_modification=most_recent_modification,
			generated_date=datetime.datetime.now(tz=datetime.timezone.utc),
			)
	output_dir.joinpath("heatmap.html").write_clean(heatmap_html)


if __name__ == "__main__":
	main()
