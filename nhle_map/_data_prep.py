#!/usr/bin/env python3
#
#  _data_prep.py
"""
Internal data preparation functions.
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
import geopandas  # type: ignore[import-untyped]
import pyogrio  # type: ignore[import-untyped]
from domdf_python_tools.paths import PathPlus

# this package
from nhle_map.constants import (
		BATTLEFIELDS,
		BUILDING_PRESERVATION_NOTICES,
		CERTIFICATES_OF_IMMUNITY,
		DE_DESIGNATED,
		PARKS_AND_GARDENS,
		PROTECTED_WRECK_SITES,
		SCHEDULED_MONUMENTS,
		WORLD_HERITAGE_SITES
		)
from nhle_map.data import make_polygon_points, small_dataset_chunk_ids, write_data

__all__ = [
		"_prepare_battlefields_data",
		"_prepare_building_preservation_notices_data",
		"_prepare_certificates_of_immunity_data",
		"_prepare_de_designated_data",
		"_prepare_parks_gardens_data",
		"_prepare_protected_wreck_sites_data",
		"_prepare_scheduled_monuments_data",
		"_prepare_world_heritage_sites_data",
		]


def _prepare_protected_wreck_sites_data(data_directory: PathPlus, output_directory: PathPlus) -> None:

	gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(data_directory / "Protected Wreck Sites.geojson")

	make_polygon_points(
			gdf,
			output_directory,
			small_dataset_chunk_ids[PROTECTED_WRECK_SITES.filename_prefix],
			PROTECTED_WRECK_SITES.variable_prefix,
			PROTECTED_WRECK_SITES.filename_prefix,
			)


def _prepare_building_preservation_notices_data(data_directory: PathPlus, output_directory: PathPlus) -> None:

	gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(
			data_directory / "Building Preservation Notice points.geojson",
			)
	chunk_id = small_dataset_chunk_ids[BUILDING_PRESERVATION_NOTICES.filename_prefix]
	write_data(
			gdf,
			output_directory,
			chunk_id,
			BUILDING_PRESERVATION_NOTICES.variable_prefix,
			BUILDING_PRESERVATION_NOTICES.filename_prefix,
			)


def _prepare_certificates_of_immunity_data(data_directory: PathPlus, output_directory: PathPlus) -> None:

	gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(
			data_directory / "Certificate of Immunity points.geojson",
			)
	chunk_id = small_dataset_chunk_ids[CERTIFICATES_OF_IMMUNITY.filename_prefix]
	write_data(
			gdf,
			output_directory,
			chunk_id,
			CERTIFICATES_OF_IMMUNITY.variable_prefix,
			CERTIFICATES_OF_IMMUNITY.filename_prefix,
			)


def _prepare_parks_gardens_data(data_directory: PathPlus, output_directory: PathPlus) -> None:

	gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(data_directory / "Parks and Gardens.geojson")

	chunk_id = small_dataset_chunk_ids[PARKS_AND_GARDENS.filename_prefix]
	make_polygon_points(
			gdf,
			output_directory,
			chunk_id,
			PARKS_AND_GARDENS.variable_prefix,
			PARKS_AND_GARDENS.filename_prefix,
			)


def _prepare_battlefields_data(data_directory: PathPlus, output_directory: PathPlus) -> None:

	gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(data_directory / "Battlefields.geojson")

	chunk_id = small_dataset_chunk_ids[BATTLEFIELDS.filename_prefix]
	make_polygon_points(
			gdf,
			output_directory,
			chunk_id,
			BATTLEFIELDS.variable_prefix,
			BATTLEFIELDS.filename_prefix,
			)


def _prepare_scheduled_monuments_data(data_directory: PathPlus, output_directory: PathPlus) -> None:

	gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(data_directory / "Scheduled Monuments.geojson")

	chunk_id = small_dataset_chunk_ids[SCHEDULED_MONUMENTS.filename_prefix]
	make_polygon_points(
			gdf,
			output_directory,
			chunk_id,
			SCHEDULED_MONUMENTS.variable_prefix,
			SCHEDULED_MONUMENTS.filename_prefix,
			)


def _prepare_de_designated_data(data_directory: PathPlus, output_directory: PathPlus) -> None:

	gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(data_directory / "De-designated sites.geojson")

	chunk_id = small_dataset_chunk_ids[DE_DESIGNATED.filename_prefix]
	make_polygon_points(
			gdf,
			output_directory,
			chunk_id,
			DE_DESIGNATED.variable_prefix,
			DE_DESIGNATED.filename_prefix,
			)


def _prepare_world_heritage_sites_data(data_directory: PathPlus, output_directory: PathPlus) -> None:

	gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(data_directory / "World Heritage Sites.geojson")

	chunk_id = small_dataset_chunk_ids[WORLD_HERITAGE_SITES.filename_prefix]
	make_polygon_points(
			gdf,
			output_directory,
			chunk_id,
			WORLD_HERITAGE_SITES.variable_prefix,
			WORLD_HERITAGE_SITES.filename_prefix,
			)
