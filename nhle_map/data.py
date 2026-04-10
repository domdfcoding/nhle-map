#!/usr/bin/env python3
#
#  data.py
"""
Data preparation.
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
import datetime
import json
from collections import defaultdict
from collections.abc import Iterable
from operator import itemgetter
from typing import Any

# 3rd party
import geopandas  # type: ignore[import-untyped]
from arcgis.features import FeatureLayer, FeatureSet  # type: ignore[import-untyped]
from arcgis.gis import GIS, ContentManager  # type: ignore[import-untyped]
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from domdf_python_tools.typing import PathLike

# this package
from nhle_map._arcgis_fix import to_geojson
from nhle_map.utils import get_id

__all__ = ["chunk_data", "download_data", "get_chunk_js", "make_polygon_points"]

DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"


def get_chunk_js(features: list, chunk_id: str | int, variable_prefix: str = "listedBuildings") -> str:
	"""
	Returns the javascript array for the given features chunk.

	:param features:
	:param chunk_id:
	:param variable_prefix: String to prefix javascript variables with.
	"""

	output = StringList()

	output.append("// Lat,Lng,Number,Name,Grade,ListDate,Link")
	output.append(f"var {variable_prefix}{chunk_id} = [")

	item: dict[str, Any]
	for item in sorted(features, key=itemgetter("ListEntry")):
		number = item["ListEntry"]
		name = item["Name"]
		grade = item.get("Grade")
		list_date = item.get("ListDate", item.get("DesigDate"))
		if isinstance(list_date, int):
			# Timestamp in milliseconds
			list_date = datetime.datetime.fromtimestamp(
					list_date / 1000,
					tz=datetime.timezone.utc,
					).strftime(DATE_FORMAT)
		link = item["hyperlink"]
		coord = item["geometry"].bounds[:2]
		output.append(json.dumps([coord[1], coord[0], number, name, grade, list_date, link]) + ',')

	output.append(']')
	output.blankline()

	return str(output)


# TODO: camel to snake for default value
# TODO: optional tqdm progress bar
# TODO: split generation and writing, and use iterator for generation?
def chunk_data(
		data: geopandas.GeoDataFrame,
		lat_range: Iterable[float],
		lng_range: Iterable[float],
		output_directory: PathLike,
		variable_prefix: str = "listedBuildings",
		filename_prefix: str = "listed_buildings",
		) -> None:
	"""
	Split the data into chunks for the given latitudes and longitudes.

	:param data:
	:param lat_range: Range of latitude values (southern edge of square)
	:param lng_range: Range of longitude values (western edge of square)
	:param output_directory: Directory to write files to.
	:param variable_prefix: String to prefix javascript variables with.
	:param filename_prefix: String to prefix javascript filenames with.
	"""

	output_dir = PathPlus(output_directory)
	output_dir.maybe_make(parents=True)

	id_lookup: dict[float, dict[float, int]] = defaultdict(dict)

	for latitude in lat_range:
		for longitide in lng_range:
			chunk_id = get_id()
			subset = data.cx[longitide:longitide + 1, latitude:latitude + 1]  # type: ignore[misc]  # TODO
			if not len(subset):
				continue

			id_lookup[latitude][longitide] = chunk_id
			chunk_js = get_chunk_js(subset.to_dict("records"), chunk_id, variable_prefix=variable_prefix)
			output_dir.joinpath(f"{filename_prefix}_{chunk_id}.js").write_clean(chunk_js)

	id_lookup_js = f"{variable_prefix}IDLookup = {json.dumps(id_lookup, indent=4)}"
	output_dir.joinpath(f"{filename_prefix}_id_lookup.js").write_clean(id_lookup_js)


def download_data(output_directory: PathLike) -> dict[str, Any]:
	"""
	Download data from the Historic England Open Data Hub on ArcGIS.

	:param output_directory: Directory to write files to.
	"""

	# TODO: De-designated sites 8836370be44f4916b9ba7d350df24902_0

	output_dir = PathPlus(output_directory)
	output_dir.maybe_make(parents=True)

	meta: dict[str, Any] = {
			"start_time": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
			"layers": [],
			}

	# TODO: check last edit date against meta.json to see if update needed

	gis = GIS()

	data_item_id = "767f279327a24845bf47dfe5eae9862b"

	content: ContentManager = gis.content
	data_item = content.get(data_item_id)

	layer: FeatureLayer

	for layer in data_item.layers:
		# print(layer)
		# print("  ", layer.properties.id)
		# print("  ", layer.properties.name)
		# print("  ", layer.properties.type)
		# print("  ", str(layer.properties.geometryType))
		meta["layers"] = dict(layer.properties)

		query: FeatureSet = layer.query(out_sr=4326)

		# if query.geometry_type == "esriGeometryMultipoint":
		# 	query._geometry_type = "esriGeometryMultiPoint"

		print(repr(query))

		if query.features:  # If no features (e.g. no preservation notices at this time) dont proceed
			(output_dir / f"{layer.properties.name}.geojson").write_clean(to_geojson(query))

	output_dir.joinpath("meta.json").dump_json(meta, indent=2)
	return meta


# TODO: camel to snake for default value
def make_polygon_points(
		data: geopandas.GeoDataFrame,
		output_directory: PathLike,
		variable_prefix: str = "protectedWreckSites",
		filename_prefix: str = "protected_wreck_sites",
		) -> None:
	"""
	Convert polygons into representative points and write to javascript.
	Split the data into chunks for the given latitudes and longitudes.

	:param data:
	:param output_directory: Directory to write files to.
	:param variable_prefix: String to prefix javascript variables with.
	:param filename_prefix: String to prefix javascript filenames with.
	"""

	output_dir = PathPlus(output_directory)
	output_dir.maybe_make(parents=True)

	data["geometry"] = data["geometry"].representative_point()
	chunk_js = get_chunk_js(
			data.to_dict("records"),
			chunk_id='',
			variable_prefix=variable_prefix,
			)
	(output_dir / f"{filename_prefix}.js").write_clean(chunk_js)
