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
	from domdf_python_tools.paths import PathPlus

	# this package
	from nhle_map import constants
	from nhle_map.data import chunk_data, download_data, download_welsh_data

	data_directory = PathPlus("data")

	if download:
		# data_directory is the local data folder, not the processed data within the output folder
		download_data(data_directory)
		download_welsh_data(data_directory)

	output_dir = PathPlus("output")
	output_dir.maybe_make()

	data = [
			(constants.LISTED_BUILDINGS, False),
			(constants.PROTECTED_WRECK_SITES, True),
			(constants.BUILDING_PRESERVATION_NOTICES, False),
			(constants.CERTIFICATES_OF_IMMUNITY, False),
			(constants.PARKS_AND_GARDENS, True),
			(constants.BATTLEFIELDS, True),
			(constants.SCHEDULED_MONUMENTS, True),
			(constants.DE_DESIGNATED, False),
			(constants.WORLD_HERITAGE_SITES, True),
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

	output_dir.joinpath("data", "meta.json").dump_json(layers_data, indent=2)


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
	from nhle_map import constants
	from nhle_map.map import make_map
	from nhle_map.templates import render_template
	from nhle_map.utils import copy_static_files, format_datetime, format_description

	set_branca_random_seed("NHLE")

	output_dir = PathPlus(output_directory)
	output_dir.maybe_make()

	copy_static_files(output_dir / "static")

	m = make_map()
	root: branca.element.Figure = m.get_root()  # type: ignore[assignment]

	layers_data = output_dir.joinpath("data", "meta.json").load_json()
	layer_mod_times = [v["dataLastEditDate"] for k, v in layers_data.items()]
	most_recent_modification = datetime.datetime.fromtimestamp(
			max(layer_mod_times) / 1000,
			tz=datetime.timezone.utc,
			)

	map_html = render_template(
			"map.jinja2",
			**render_figure(root)._asdict(),
			layers=constants.LAYERS,
			layers_data=layers_data,
			most_recent_modification=most_recent_modification,
			generated_date=datetime.datetime.now(tz=datetime.timezone.utc),
			format_description=format_description,
			format_datetime=format_datetime,
			)
	output_dir.joinpath("index.html").write_clean(map_html)


if __name__ == "__main__":
	main()
