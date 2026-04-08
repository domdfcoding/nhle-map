"""
Fixes problem with arcgis's own ``to_geojson`` function.
"""

# stdlib
import json
from typing import Any

# 3rd party
from arcgis._impl.common._utils import _date_handler  # type: ignore[import-untyped]
from arcgis.features import FeatureSet  # type: ignore[import-untyped]

__all__ = ["extract", "get_coordinates", "get_geom_type", "to_geojson"]


def extract(feature: dict, esri_geom_type: str) -> dict[str, Any]:
	"""
	Creates a single feature.
	"""

	item: dict[str, Any] = {}
	item["type"] = "Feature"
	geom = feature["geometry"]
	geometry: dict[str, Any] = {}
	geometry["type"] = get_geom_type(esri_geom_type)
	geometry["coordinates"] = get_coordinates(geom, geometry["type"])
	# add check for MultiPolygon
	if geometry["type"] == "Polygon" and len(geometry["coordinates"]) > 1:
		geometry["type"] = "MultiPolygon"
		# for multipolygons, each set of rings should be nested an extra level
		new_coords = [[poly] for poly in geometry["coordinates"]]
		geometry["coordinates"] = new_coords
	item["geometry"] = geometry
	item["properties"] = feature["attributes"]

	return item


def get_geom_type(esri_type: str) -> str:
	"""
	Converts esri geometry types to GeoJSON geometry types.
	"""

	if esri_type == "esriGeometryPoint":
		return "Point"
	elif esri_type.lower() == "esrigeometrymultipoint":
		return "MultiPoint"
	elif esri_type == "esriGeometryPolyline":
		return "MultiLineString"
	elif esri_type == "esriGeometryPolygon":
		return "Polygon"
	else:
		return "Point"


def get_coordinates(geom: dict, geom_type: str) -> list:
	"""
	Converts the Esri Geometry Structure to GeoJSON structure.
	"""

	if geom_type == "Polygon":
		return geom["rings"]
	elif geom_type == "MultiLineString":
		return geom["paths"]
	elif geom_type == "Point":
		return [geom['x'], geom['y']]
	else:
		return geom["points"]


def to_geojson(feature_set: FeatureSet) -> str:
	"""
	Gets the Feature Set object as a GeoJSON.

	:returns: A GeoJSON object.
	"""

	def esri_to_geo(esrijson: dict) -> dict:
		"""
		Converts Esri Format JSON to GeoJSON.
		"""

		geojson: dict[str, Any] = {}
		features = esrijson["features"]
		esri_geom_type = esrijson["geometryType"]
		geojson["type"] = "FeatureCollection"
		feats = []
		for feat in features:
			feats.append(extract(feat, esri_geom_type))

		# assign to the geojson object
		geojson["features"] = feats
		return geojson

	return json.dumps(esri_to_geo(feature_set.value), default=_date_handler)
