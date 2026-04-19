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
from typing import Any

# 3rd party
import geopandas  # type: ignore[import-untyped]
import numpy  # nodep
import pandas
import pyogrio  # type: ignore[import-untyped]
import requests
from arcgis.features import FeatureLayer, FeatureSet  # type: ignore[import-untyped]
from arcgis.gis import GIS, ContentManager  # type: ignore[import-untyped]
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from domdf_python_tools.typing import PathLike
from shapely import MultiPolygon, Polygon

# this package
from nhle_map._arcgis_fix import to_geojson
from nhle_map.constants import LISTED_BUILDINGS, WELSH_LAYERS, Dataset
from nhle_map.utils import DATE_FORMAT, DATE_ONLY_FORMAT, format_datetime, from_iso_zulu, get_id

__all__ = [
		"chunk_data",
		"dict_get_oneof",
		"download_data",
		"download_welsh_data",
		"get_chunk_js",
		"get_data_chunks",
		"get_list_date",
		"set_polygon_marker",
		]

Chunks = dict[float, dict[float, geopandas.GeoDataFrame]]


def get_chunk_js(
		features: list,
		chunk_id: str | int,
		variable_prefix: str = LISTED_BUILDINGS.variable_prefix,
		include_polygon: bool = False,
		) -> str:
	"""
	Returns the javascript array for the given features chunk.

	:param features:
	:param chunk_id:
	:param variable_prefix: String to prefix javascript variables with.
	:param include_polygon: Include the outline polygon points (from the ``polygon`` column) and not merely the central coordinates.
	"""

	output = StringList()

	output.append("// Lat,Lng,Number,Name,Grade,ListDate,Link,Notes?, Polygon Points?,")
	output.append(f"var {variable_prefix}{chunk_id} = [")

	item: dict[str, Any]
	for item in sorted(features, key=_chunk_sort_fn):
		# TODO: add "Period" to notes
		notes = dict_get_oneof(item, ["Notes", "Location"], default=None, err_missing=False)

		if notes and "Buffer Zone" in notes:
			# TODO: find a way to indicate this still
			continue

		number = _get_list_entry_no(item)
		name = _get_list_entry_name(item)
		grade = item.get("Grade")
		list_date = format_datetime(get_list_date(item), DATE_ONLY_FORMAT)
		link = item.get("hyperlink")
		coord = item["geometry"].bounds[:2]
		values = [coord[1], coord[0], number, name, grade, list_date, link]

		poly_points = []
		if include_polygon:
			polygon = item["polygon"]
			if isinstance(polygon, Polygon):
				poly_points.append(_get_poly_points(polygon))
			elif isinstance(polygon, MultiPolygon):
				for sub_poly in polygon.geoms:
					if not isinstance(sub_poly, Polygon):
						raise NotImplementedError(sub_poly)
					poly_points.append(_get_poly_points(sub_poly))

		if poly_points or notes:
			values.append(notes or None)
			values.append(poly_points)

		if poly_points and len(poly_points[0][0]) > 10:
			# Nicer formatting
			as_js = json.dumps(values)[1:] + ','
			split_at_square_brackets = as_js.split("[")
			line = ''
			indent = ''
			
			for line_chunk in split_at_square_brackets:
				line += f"{indent}[{line_chunk}"
				indent = ''
				if len(line) > 200:
					output.append(line)
					line = ''
					indent = "    "
			
			if line:
				output.append(line)

		else:
			output.append(json.dumps(values) + ',')

	output.append(']')
	output.blankline()

	return str(output)


def _get_poly_points(sub_poly: Polygon) -> list[list[tuple[float, float]]]:
	this_poly_points = []
	this_poly_points.append([(lat, lng) for (lng, lat) in sub_poly.exterior.coords])

	for hole in sub_poly.interiors:
		this_poly_points.append([(lat, lng) for (lng, lat) in hole.coords])

	return this_poly_points


def get_data_chunks(
		data: geopandas.GeoDataFrame,
		lat_range: Iterable[float],
		lng_range: Iterable[float],
		) -> Chunks:
	"""
	Split the data into chunks for the given latitudes and longitudes.

	:param data:
	:param lat_range: Range of latitude values (southern edge of square)
	:param lng_range: Range of longitude values (western edge of square)
	"""

	chunks: Chunks = defaultdict(dict)

	for latitude in lat_range:
		for longitude in lng_range:
			subset = data.cx[longitude:longitude + 1, latitude:latitude + 1]  # type: ignore[misc]  # TODO

			# Remove all sites we've taken in this chunk,
			# to avoid duplicating those than span chunk boundaries
			data = data.filter(items=(data.index.difference(subset.index)), axis=0)

			if len(subset):
				chunks[latitude][longitude] = subset

	return chunks


def download_data(output_directory: PathLike) -> dict[str, Any]:
	"""
	Download data from the Historic England Open Data Hub on ArcGIS.

	:param output_directory: Directory to write files to.
	"""

	output_dir = PathPlus(output_directory)
	output_dir.maybe_make(parents=True)

	meta: dict[str, Any] = {
			"start_time": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
			"layers": [],
			}

	# TODO: check last edit date against meta.json to see if update needed

	gis = GIS()

	for data_item_id in [
			"8836370be44f4916b9ba7d350df24902",
			"767f279327a24845bf47dfe5eae9862b",
			]:
		content: ContentManager = gis.content
		data_item = content.get(data_item_id)

		layer: FeatureLayer

		for layer in data_item.layers:
			# print(layer)
			# print("  ", layer.properties.id)
			# print("  ", layer.properties.name)
			# print("  ", layer.properties.type)
			# print("  ", str(layer.properties.geometryType))
			meta["layers"].append(dict(layer.properties))

			query: FeatureSet = layer.query(out_sr=4326)

			# if query.geometry_type == "esriGeometryMultipoint":
			# 	query._geometry_type = "esriGeometryMultiPoint"

			print(repr(query))

			if query.features:  # If no features (e.g. no preservation notices at this time) dont proceed
				(output_dir / f"{layer.properties.name}.geojson").write_clean(to_geojson(query))

	output_dir.joinpath("meta.json").dump_json(meta, indent=2)
	return meta


wales_datamap_url = "https://datamap.gov.wales/geoserver/ows"


def download_welsh_data(output_directory: PathLike) -> dict[str, Any]:
	"""
	Download data from the cadw datasets on ``datamap.gov.wales``.

	:param output_directory: Directory to write files to.
	"""

	output_dir = PathPlus(output_directory)
	output_dir.maybe_make(parents=True)

	data_common_params = {
			"service": "WFS",
			"version": "1.0.0",
			"request": "GetFeature",
			"outputFormat": "json",
			"srs": "EPSG:4326",
			"srsName": "EPSG:4326",
			}

	for dataset in WELSH_LAYERS:
		response = requests.get(
				wales_datamap_url,
				params={**data_common_params, "typename": dataset.welsh_api_typename},
				)
		response.raise_for_status()
		geojson = response.json()
		for feature in geojson["features"]:
			feature_properties = {}
			for key, value in feature["properties"].items():
				if key in {"RecordNumber", "reference_number"}:
					feature_properties["ListEntry"] = value
				elif key == "Report":
					feature_properties["hyperlink"] = value
				elif key == "Report_welsh":
					feature_properties["hyperlink_welsh"] = value
				elif key == "site_name_en":
					feature_properties["Name"] = value
				elif key == "site_name_cy":
					feature_properties["Name_cy"] = value
				elif key == "DesignationDate":
					if value:
						feature_properties["ListDate"] = from_iso_zulu(value).timestamp() * 1000  # To milliseconds
					else:
						feature_properties["ListDate"] = None
				else:
					feature_properties[key] = value

			feature["properties"] = feature_properties

		output_dir.joinpath(dataset.welsh_geojson_filename).dump_json(geojson)

	# TODO: metadata. Have to hardcode descriptions
	# based on links from https://cadw.gov.wales/advice-support/cof-cymru/downloads
	# as the provided downloads give too verbose descriptions


def set_polygon_marker(data: geopandas.GeoDataFrame) -> geopandas.GeoDataFrame:
	"""
	Sets the marker position for the given data's polygon.

	Saves the actual polygon in the ``polygon`` column.

	:param data:
	"""

	data["polygon"] = data["geometry"]

	# TODO: get point in centre of largest polygon if multiple (and centre of sole poly otherwise)
	# data["geometry"] = data["geometry"].representative_point()
	data["geometry"] = data.to_crs(epsg=27700).representative_point().to_crs(epsg=4326)
	# data["geometry"] = data["geometry"].centroid
	# data["geometry"] = data.to_crs(epsg=27700).centroid.to_crs(epsg=4326)

	return data


# TODO: generic on KT?
def dict_get_oneof(
		dictionary: dict[str, Any],
		keys: Iterable[str],  #
		default: str | None = ...,
		err_missing: bool = True,
		) -> str | None:
	"""
	Get one of many possible keys from the given dictionary.

	:param dictionary:
	:param keys:
	:param default: If set, the default value to return if all values are :py:obj:`None`
		(or if no keys exist and ``err_missing`` is :py:obj:`False`)
	:param err_missing: If :py:obj:`True` will error if none of the keys exist in the dictionary.
		If :py:obj:`False` the default value (if set) will be returned instead.
	"""
	possible_keys = list(keys)
	actual_keys = set(possible_keys) & dictionary.keys()

	if not actual_keys:
		if default is not Ellipsis and not err_missing:
			return default

		raise KeyError(possible_keys)

	if len(actual_keys) == 1:
		return dictionary[actual_keys.pop()]

	else:
		for key in actual_keys:
			value = dictionary[value]
			if value is not None:
				return value

	if default is not Ellipsis:
		return default

	raise KeyError(possible_keys)


def get_list_date(list_entry: dict[str, Any]) -> datetime.datetime | None:
	"""
	Returns the listing date, Building Preservation Notice / Certificate of Immunity start date, or similar for the given list entry.

	:param list_entry:
	"""

	possible_keys = [
			"ListDate",
			"DesigDate",
			"COIStart",
			"BPNStart",
			"RegDate",
			"SchedDate",
			"DateRemovedFromList",
			"InscrDate",
			]

	list_date: str | float | None = dict_get_oneof(list_entry, possible_keys, default=None)

	if list_date is None or numpy.isnan(list_date):
		return None

	if isinstance(list_date, (int, float)):
		# Timestamp in milliseconds
		return datetime.datetime.fromtimestamp(
				list_date / 1000,
				tz=datetime.timezone.utc,
				)
	else:
		return datetime.datetime.strptime(list_date, DATE_FORMAT)


def _chunk_sort_fn(list_entry: dict[str, Any]) -> int:
	list_entry_no = _get_list_entry_no(list_entry)

	if list_entry_no == -1:
		dt = get_list_date(list_entry)
		if dt is None:
			return -1

		return int(dt.timestamp())

	return list_entry_no


def _get_list_entry_no(list_entry: dict[str, Any]) -> str | int:
	possible_keys = ["ListEntry", "OriginalListEntryNumber"]
	entry_no = dict_get_oneof(list_entry, possible_keys, default=-1)

	if isinstance(entry_no, str):
		return entry_no

	if entry_no is None or numpy.isnan(entry_no):
		return -1

	return int(entry_no)


def _get_list_entry_name(list_entry: dict[str, Any]) -> str:
	possible_keys = ["Name", "ARTICLEVERSIONNAME"]
	return dict_get_oneof(list_entry, possible_keys)


def _prepare_dataset(
		dataset: Dataset,
		lat_range: Iterable[float],
		lng_range: Iterable[float],
		data_directory: PathPlus,
		) -> Chunks:
	# TODO: handle no English dataset
	gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(data_directory / dataset.geojson_filename)
	if dataset.welsh_geojson_filename:
		welsh_gdf: geopandas.GeoDataFrame = pyogrio.read_dataframe(data_directory / dataset.welsh_geojson_filename)
		gdf = pandas.concat((gdf, welsh_gdf), ignore_index=True)
		gdf = gdf.where(gdf.notnull(), None)

	return get_data_chunks(gdf, lat_range, lng_range)


# TODO: optional tqdm progress bar
def chunk_data(
		data: list[tuple[Dataset, bool]],
		lat_range: Iterable[float],
		lng_range: Iterable[float],
		data_directory: PathLike,
		output_directory: PathLike,
		) -> None:
	"""
	Split the data into chunks for the given latitudes and longitudes.

	:param data:
	:param lat_range: Range of latitude values (southern edge of square)
	:param lng_range: Range of longitude values (western edge of square)
	:param data_directory: Directory containing the input GeoJSON files.
	:param output_directory: Directory to write files to.
	"""

	lat_range = list(lat_range)
	lng_range = list(lng_range)

	data_dir = PathPlus(data_directory)
	output_dir = PathPlus(output_directory)
	output_dir.maybe_make(parents=True)

	datasets: list[tuple[Chunks, Dataset, bool]] = []
	for (dataset, polygon) in data:
		datasets.append((_prepare_dataset(dataset, lat_range, lng_range, data_dir), dataset, polygon))

	id_lookup: dict[float, dict[float, int]] = defaultdict(dict)

	for latitude in lat_range:
		for longitude in lng_range:
			chunk_id = get_id()
			chunk_buffer = []
			data_for_chunk: bool = False

			for chunks, dataset, polygon in datasets:
				subset = chunks.get(latitude, {}).get(longitude)

				if subset is None:
					chunk_js = get_chunk_js(
							[],
							chunk_id=chunk_id,
							variable_prefix=dataset.variable_prefix,
							)
				else:
					data_for_chunk = True
					subset = subset.copy()
					if polygon:
						subset = set_polygon_marker(subset)

					chunk_js = get_chunk_js(
							subset.to_dict("records"),
							chunk_id=chunk_id,
							variable_prefix=dataset.variable_prefix,
							include_polygon=polygon,
							)

				chunk_buffer.append(chunk_js)

			if data_for_chunk:
				id_lookup[latitude][longitude] = chunk_id

				output_dir.joinpath(f"nhle_{chunk_id}.js").write_lines(chunk_buffer)

	id_lookup_js = f"nhleIDLookup = {json.dumps(id_lookup, indent=4)}"
	output_dir.joinpath("nhle_id_lookup.js").write_clean(id_lookup_js)
