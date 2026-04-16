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
		"Dataset",
		"BATTLEFIELDS",
		"BUILDING_PRESERVATION_NOTICES",
		"CERTIFICATES_OF_IMMUNITY",
		"LISTED_BUILDINGS",
		"PARKS_AND_GARDENS",
		"PROTECTED_WRECK_SITES",
		"SCHEDULED_MONUMENTS",
		"WORLD_HERITAGE_SITES",
		"DE_DESIGNATED",
		"LAYERS",
		]


class Dataset(NamedTuple):
	"""
	Identifiers for a particular dataset.
	"""

	variable_prefix: str
	filename_prefix: str
	name: str
	icon: "LayerIcon"
	promise_function: str | None = None

	@property
	def layer_label(self) -> str:
		"""
		The text for the layer control, showing the layer name and icon.
		"""

		return f"{self.name} {self.icon.layercontrol_icon}"


BATTLEFIELDS = Dataset(
		"battlefields",
		"battlefields",
		"Battlefields",
		SVGLayerIcon(filename="static/img/Challenge_Icon.svg", marker_colour="orange"),
		"loadBattlefieldMarkers",
		)

# Alternative BPN/immunity icon   # fa-sign-hanging
BUILDING_PRESERVATION_NOTICES = Dataset(
		"buildingPreservationNotices",
		"building_preservation_notices",
		"Building Preservation Notices",
		FontawesomeLayerIcon(icon="building-flag", marker_colour="teal"),
		"loadBPNMarkers",
		)

CERTIFICATES_OF_IMMUNITY = Dataset(
		"certificatesOfImmunity",
		"certificates_of_immunity",
		"Certificates of Immunity",
		FontawesomeLayerIcon(icon="scroll", marker_colour="tan"),
		"loadImmunityMarkers",
		)

# TODO: adjust shade back to old blue now using SVG
LISTED_BUILDINGS = Dataset(
		"listedBuildings",
		"listed_buildings",
		"Listed Buildings",
		FontawesomeLayerIcon(icon="building", marker_colour="blue"),
		None,
		)

PARKS_AND_GARDENS = Dataset(
		"parksGardens",
		"parks_and_gardens",
		"Parks and Gardens",
		FontawesomeLayerIcon(icon="tree", marker_colour="green"),
		"loadParksGardensMarkers",
		)

PROTECTED_WRECK_SITES = Dataset(
		"protectedWreckSites",
		"protected_wreck_sites",
		"Protected Wreck Sites",
		FontawesomeLayerIcon(icon="anchor", marker_colour="purple"),
		"loadShipwreckMarkers",
		)

SCHEDULED_MONUMENTS = Dataset(
		"scheduledMonuments",
		"scheduled_monuments",
		"Scheduled Monuments",
		FontawesomeLayerIcon(icon="monument", marker_colour="red"),
		"loadScheduledMonumentMarkers",
		)

WORLD_HERITAGE_SITES = Dataset(
		"worldHeritageSites",
		"world_heritage_sites",
		"World Heritage Sites",
		FontawesomeLayerIcon(icon="certificate", marker_colour="grey"),
		"loadWorldHeritageMarkers",
		)

DE_DESIGNATED = Dataset(
		"deDesignated",
		"de_designated",
		"De-designated",
		FontawesomeLayerIcon(icon="ban", marker_colour="black"),
		"loadDeDesignatedMarkers",
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
