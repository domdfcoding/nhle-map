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
	Development tools for towpath-walk-tracker.
	"""


@auto_default_option("-d/-D", "--download/--no-download", is_flag=True)
@main.command()
def prepare_data(download: bool = False) -> None:
	"""
	Prepare data for the map.
	"""

	# 3rd party
	import geopandas
	import pyogrio  # type: ignore[import-untyped]
	from domdf_python_tools.paths import PathPlus

	# this package
	from nhle_map import constants
	from nhle_map.data import chunk_data_v2, download_data

	data_directory = PathPlus("data")

	if download:
		download_data(data_directory)  # Local data folder, not the processed data within the output folder

	output_dir = PathPlus("output")
	output_dir.maybe_make()

	listed_buildings_gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(
			data_directory / "Listed Building points.geojson",
			)
	protected_wreck_sites_gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(
			data_directory / "Protected Wreck Sites.geojson",
			)
	building_preservation_notices_gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(
			data_directory / "Building Preservation Notice points.geojson",
			)
	certificates_of_immunity_gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(
			data_directory / "Certificate of Immunity points.geojson",
			)
	parks_gardens_gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(
			data_directory / "Parks and Gardens.geojson",
			)
	battlefields_gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(data_directory / "Battlefields.geojson")
	scheduled_monuments_gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(
			data_directory / "Scheduled Monuments.geojson",
			)
	de_designated_gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(
			data_directory / "De-designated sites.geojson",
			)
	world_heritage_sites_gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(
			data_directory / "World Heritage Sites.geojson",
			)

	data = [
			(listed_buildings_gdf, constants.LISTED_BUILDINGS, False),
			(protected_wreck_sites_gdf, constants.PROTECTED_WRECK_SITES, True),
			(building_preservation_notices_gdf, constants.BUILDING_PRESERVATION_NOTICES, False),
			(certificates_of_immunity_gdf, constants.CERTIFICATES_OF_IMMUNITY, False),
			(parks_gardens_gdf, constants.PARKS_AND_GARDENS, True),
			(battlefields_gdf, constants.BATTLEFIELDS, True),
			(scheduled_monuments_gdf, constants.SCHEDULED_MONUMENTS, True),
			(de_designated_gdf, constants.DE_DESIGNATED, False),
			(world_heritage_sites_gdf, constants.WORLD_HERITAGE_SITES, True),
			]

	chunk_data_v2(data, range(49, 55), range(-7, 3), output_directory=output_dir / "data")


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
	from nhle_map.data import DATE_FORMAT
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
			layers=constants.LAYERS,
			generated_date=datetime.datetime.now(tz=datetime.timezone.utc).strftime(DATE_FORMAT)
			)
	output_dir.joinpath("index.html").write_clean(map_html)


if __name__ == "__main__":
	main()
