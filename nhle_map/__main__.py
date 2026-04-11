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
from geopandas import GeoDataFrame  # type: ignore[import-untyped]

# this package
from nhle_map.data import make_polygon_points

__all__ = ["main", "make_map", "prepare_data"]


@click_group(
		cls=SuggestionGroup,
		invoke_without_command=False,
		context_settings={**CONTEXT_SETTINGS, "show_default": True},
		)
def main() -> None:
	"""
	Development tools for towpath-walk-tracker.
	"""


@auto_default_option("-d/-D", "--download/--no-download", is_flag=True)
@main.command()
def prepare_data(download: bool = False) -> None:
	"""
	Prepare data for the map.
	"""

	# 3rd party
	import pyogrio  # type: ignore[import-untyped]
	from domdf_python_tools.paths import PathPlus

	# this package
	from nhle_map.data import chunk_data, download_data

	data_directory = PathPlus("data")

	if download:
		download_data(data_directory)  # Local data folder, not the processed data within the output folder

	output_dir = PathPlus("output")
	output_dir.maybe_make()

	listed_buildings_gdf = pyogrio.read_dataframe(data_directory / "Listed Building points.geojson")

	chunk_data(
			listed_buildings_gdf,
			range(49, 55),
			range(-7, 3),
			output_dir / "data",
			)

	protected_wreck_sites_gdf: GeoDataFrame = pyogrio.read_dataframe(
			data_directory / "Protected Wreck Sites.geojson",
			)

	make_polygon_points(protected_wreck_sites_gdf, output_dir / "data", chunk_id=0)


@auto_default_option("-O", "--output-dir", "output_directory")
@main.command()
def make_map(output_directory: str = "output") -> None:
	"""
	Create the map and write associated files.
	"""

	# 3rd party
	import branca.element
	from domdf_folium_tools import set_branca_random_seed
	from domdf_folium_tools.elements import render_figure
	from domdf_python_tools.paths import PathPlus

	# this package
	from nhle_map.map import make_map
	from nhle_map.templates import render_template
	from nhle_map.utils import copy_static_files

	set_branca_random_seed("NHLE")

	output_dir = PathPlus(output_directory)
	output_dir.maybe_make()

	copy_static_files(output_dir / "static")

	m = make_map()
	root: branca.element.Figure = m.get_root()  # type: ignore[assignment]

	map_html = render_template(
			"map.jinja2",
			**render_figure(root)._asdict(),
			)
	output_dir.joinpath("index.html").write_clean(map_html)


if __name__ == "__main__":
	main()
