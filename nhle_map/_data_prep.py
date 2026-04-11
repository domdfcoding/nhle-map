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
from nhle_map.data import make_polygon_points, small_dataset_chunk_ids, write_data

__all__ = [
		"_prepare_building_preservation_notices_data",
		"_prepare_certificates_of_immunity_data",
		"_prepare_protected_wreck_sites_data",
		]


def _prepare_protected_wreck_sites_data(data_directory: PathPlus, output_directory: PathPlus) -> None:

	wreck_prefixes = ("protectedWreckSites", "protected_wreck_sites")
	protected_wreck_sites_gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(
			data_directory / "Protected Wreck Sites.geojson",
			)

	make_polygon_points(
			protected_wreck_sites_gdf,
			output_directory,
			small_dataset_chunk_ids[wreck_prefixes[1]],
			*wreck_prefixes,
			)


def _prepare_building_preservation_notices_data(data_directory: PathPlus, output_directory: PathPlus) -> None:

	bpn_gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(
			data_directory / "Building Preservation Notice points.geojson",
			)
	bpn_prefixes = ("buildingPreservationNotices", "building_preservation_notices")
	bpn_chunk_id = small_dataset_chunk_ids[bpn_prefixes[1]]
	write_data(
			bpn_gdf,
			output_directory,
			bpn_chunk_id,
			*bpn_prefixes,
			)


def _prepare_certificates_of_immunity_data(data_directory: PathPlus, output_directory: PathPlus) -> None:

	bpn_gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(
			data_directory / "Certificate of Immunity points.geojson",
			)
	bpn_prefixes = ("certificatesOfImmunity", "certificates_of_immunity")
	bpn_chunk_id = small_dataset_chunk_ids[bpn_prefixes[1]]
	write_data(
			bpn_gdf,
			output_directory,
			bpn_chunk_id,
			*bpn_prefixes,
			)
