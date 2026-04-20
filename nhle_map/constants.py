#!/usr/bin/env python3
#
#  constants.py
"""
String constants.
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
from typing import NamedTuple

# this package
from nhle_map.icons import FontawesomeLayerIcon, LayerIcon, SVGLayerIcon

__all__ = [
		"BATTLEFIELDS",
		"BUILDING_PRESERVATION_NOTICES",
		"CERTIFICATES_OF_IMMUNITY",
		"Dataset",
		"DE_DESIGNATED",
		"LAYERS",
		"LISTED_BUILDINGS",
		"MAX_LAT",
		"MAX_LNG",
		"MIN_LAT",
		"MIN_LNG",
		"PARKS_AND_GARDENS",
		"PROTECTED_WRECK_SITES",
		"SCHEDULED_MONUMENTS",
		"WELSH_LAYERS",
		"WORLD_HERITAGE_SITES",
		]


class Dataset(NamedTuple):
	"""
	Identifiers for a particular dataset.
	"""

	variable_prefix: str
	identifier: str
	name: str
	icon: "LayerIcon"
	geojson_filename: str  # TODO: Accept None to allow welsh-only layers
	welsh_geojson_filename: str | None = None
	welsh_api_typename: str | None = None

	@property
	def layer_label(self) -> str:
		"""
		The text for the layer control, showing the layer name and icon.
		"""

		return f"{self.name} {self.icon.layercontrol_icon}"


BATTLEFIELDS = Dataset(
		variable_prefix="battlefields",
		identifier="battlefields",
		name="Battlefields",
		icon=SVGLayerIcon(filename="static/img/Challenge_Icon.svg", marker_colour="orange"),
		geojson_filename="Battlefields.geojson",
		)

# Alternative BPN/immunity icon   # fa-sign-hanging
BUILDING_PRESERVATION_NOTICES = Dataset(
		variable_prefix="buildingPreservationNotices",
		identifier="building_preservation_notices",
		name="Building Preservation Notices",
		icon=FontawesomeLayerIcon(icon="building-flag", marker_colour="teal", svg_marker=True),
		geojson_filename="Building Preservation Notice points.geojson",
		)

CERTIFICATES_OF_IMMUNITY = Dataset(
		variable_prefix="certificatesOfImmunity",
		identifier="certificates_of_immunity",
		name="Certificates of Immunity",
		icon=FontawesomeLayerIcon(icon="scroll", marker_colour="tan", svg_marker=True),
		geojson_filename="Certificate of Immunity points.geojson",
		)

LISTED_BUILDINGS = Dataset(
		variable_prefix="listedBuildings",
		identifier="listed_buildings",
		name="Listed Buildings",
		icon=FontawesomeLayerIcon(icon="building", marker_colour="#006fb2", svg_marker=True),
		geojson_filename="Listed Building points.geojson",
		welsh_geojson_filename="Welsh Listed Buildings.geojson",
		welsh_api_typename="inspire-wg:Cadw_ListedBuildings",
		)

PARKS_AND_GARDENS = Dataset(
		variable_prefix="parksGardens",
		identifier="parks_and_gardens",
		name="Parks and Gardens",
		icon=FontawesomeLayerIcon(icon="tree", marker_colour="green"),
		geojson_filename="Parks and Gardens.geojson",
		)

PROTECTED_WRECK_SITES = Dataset(
		variable_prefix="protectedWreckSites",
		identifier="protected_wreck_sites",
		name="Protected Wreck Sites",
		icon=FontawesomeLayerIcon(icon="anchor", marker_colour="purple", svg_marker=True),
		geojson_filename="Protected Wreck Sites.geojson",
		welsh_geojson_filename="Welsh Protected Wreck Sites.geojson",
		welsh_api_typename="inspire-wg:Cadw_DesignatedWrecks",
		)

SCHEDULED_MONUMENTS = Dataset(
		variable_prefix="scheduledMonuments",
		identifier="scheduled_monuments",
		name="Scheduled Monuments",
		icon=FontawesomeLayerIcon(icon="monument", marker_colour="#a32d2f", svg_marker=True),
		geojson_filename="Scheduled Monuments.geojson",
		welsh_geojson_filename="Welsh Scheduled Monuments.geojson",
		welsh_api_typename="inspire-wg:Cadw_SAM",
		)

WORLD_HERITAGE_SITES = Dataset(
		variable_prefix="worldHeritageSites",
		identifier="world_heritage_sites",
		name="World Heritage Sites",
		icon=FontawesomeLayerIcon(icon="certificate", marker_colour="grey", svg_marker=True),
		geojson_filename="World Heritage Sites.geojson",
		# welsh_geojson_filename="Welsh World Heritage Sites.geojson",
		welsh_api_typename="inspire-wg:vGeoServer_WorldHeritageSites_Public",
		)

DE_DESIGNATED = Dataset(
		variable_prefix="deDesignated",
		identifier="de_designated",
		name="De-designated",
		icon=FontawesomeLayerIcon(icon="ban", marker_colour="black"),
		geojson_filename="De-designated sites.geojson",
		)

LAYERS = (
		BATTLEFIELDS,
		BUILDING_PRESERVATION_NOTICES,
		CERTIFICATES_OF_IMMUNITY,
		LISTED_BUILDINGS,
		PARKS_AND_GARDENS,
		PROTECTED_WRECK_SITES,
		SCHEDULED_MONUMENTS,
		WORLD_HERITAGE_SITES,
		DE_DESIGNATED,
		)

MIN_LAT = 49
# MIN_LNG = -12
MIN_LNG = -7
# MAX_LAT = 62
MAX_LAT = 55
MAX_LNG = 3


WELSH_LAYERS = (
		LISTED_BUILDINGS,
		# TODO: WELSH_PARKS_AND_GARDENS,
		PROTECTED_WRECK_SITES,
		# WELSH_REGISTERED_LANDSCAPES,
		SCHEDULED_MONUMENTS,
		# WORLD_HERITAGE_SITES,
		)
