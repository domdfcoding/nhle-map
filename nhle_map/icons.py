#!/usr/bin/env python3
#
#  icons.py
"""
Layer icons.
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
import abc
import json
from typing import Any

# 3rd party
import attrs
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from domdf_python_tools.typing import PathLike

__all__ = ["FontawesomeLayerIcon", "LayerIcon", "SVGLayerIcon", "get_layer_label_text", "write_icons_js"]


@attrs.define
class LayerIcon(abc.ABC):
	"""
	Base class for icons used for markers in layers.
	"""

	#: The marker background colour.
	marker_colour: str

	def to_dict(self) -> dict[str, Any]:
		"""
		Returns a dictionary representation suitable for Leaflet.ExtraMarkers.
		"""

		return attrs.asdict(self)

	@property
	@abc.abstractmethod
	def layercontrol_icon(self) -> str:
		"""
		Returns the icon suitable for use in the layer control.
		"""

		raise NotImplementedError


@attrs.define
class FontawesomeLayerIcon(LayerIcon):
	"""
	An icon from fontawesome.
	"""

	icon: str

	@property
	def layercontrol_icon(self) -> str:  # noqa: D102
		return f"<i class='fa-solid fa-{self.icon}'></i>"

	def to_dict(self) -> dict[str, Any]:  # noqa: D102
		return {
				"icon": f"fa-{self.icon}",
				"markerColor": self.marker_colour,
				"prefix": "fa",
				}


@attrs.define
class SVGLayerIcon(LayerIcon):
	"""
	An icon from an SVG file.
	"""

	filename: str

	@property
	def layercontrol_icon(self) -> str:  # noqa: D102
		return f"<img src='{self.filename}' width='20px'>"

	def to_dict(self) -> dict[str, Any]:  # noqa: D102
		return {
				"innerHTML": f"<img src='{self.filename}' style='margin: 8px'>",
				"markerColor": self.marker_colour,
				}


layer_icons: dict[str, LayerIcon] = {
		"Battlefields": SVGLayerIcon(filename="static/img/Challenge_Icon.svg", marker_colour="orange"),  #
		# Alternative BPN/immunity icon   # fa-sign-hanging
		"Building Preservation Notices": FontawesomeLayerIcon(icon="building-flag", marker_colour="teal"),
		"Certificates of Immunity": FontawesomeLayerIcon(icon="scroll", marker_colour="tan"),
		"Listed Buildings": FontawesomeLayerIcon(icon="building", marker_colour="blue"),
		"Parks and Gardens": FontawesomeLayerIcon(icon="tree", marker_colour="green"),
		"Protected Wreck Sites": FontawesomeLayerIcon(icon="anchor", marker_colour="purple"),
		"Scheduled Monuments": FontawesomeLayerIcon(icon="monument", marker_colour="red"),
		"World Heritage Sites": FontawesomeLayerIcon(icon="certificate", marker_colour="grey"),
		"De-designated": FontawesomeLayerIcon(icon="ban", marker_colour="black"),
		}


def get_layer_label_text(name: str) -> str:
	"""
	Returns the text for the layer control, showing the layer name and icon.

	:param name:
	"""

	return f"{name} {layer_icons[name].layercontrol_icon}"


def write_icons_js(output_directory: PathLike) -> None:
	"""
	Write the javascript file containing the icons for Leaflet.

	:param output_directory: Directory to write the ``icons.js`` file to.
	"""

	output_dir = PathPlus(output_directory)
	output_dir.maybe_make(parents=True)

	output = StringList()
	for layer_name, var_name in [
		("Battlefields", "battlefieldsIcon"),
		("Building Preservation Notices", "buildingPreservationNoticesIcon"),
		("Certificates of Immunity", "certificatesOfImmunityIcon"),
		("Listed Buildings", "listedBuildingsIcon"),
		("Parks and Gardens", "parksAndGardensIcon"),
		("Protected Wreck Sites", "protectedWreckSitesIcon"),
		("Scheduled Monuments", "scheduledMonumentsIcon"),
		("World Heritage Sites", "worldHeritageSitesIcon"),
		("De-designated", "deDesignatedIcon"),
	]:

		output.append(f"var {var_name} = L.ExtraMarkers.icon(")
		output.append('\t' + json.dumps(layer_icons[layer_name].to_dict()))
		output.append(");")
		output.blankline()

	output_dir.joinpath("icons.js").write_clean(str(output))
