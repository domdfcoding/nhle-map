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
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

# 3rd party
import attrs
from domdf_python_tools.stringlist import StringList

if TYPE_CHECKING:
	# this package
	from nhle_map.constants import Dataset

__all__ = ["FontawesomeLayerIcon", "LayerIcon", "SVGLayerIcon", "make_icons_js"]


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
	svg_marker: bool = False

	@property
	def layercontrol_icon(self) -> str:  # noqa: D102
		return f"<i class='fa-solid fa-{self.icon}'></i>"

	def to_dict(self) -> dict[str, Any]:  # noqa: D102
		return {
				"icon": f"fa-{self.icon}",
				"markerColor": self.marker_colour,
				"prefix": "fa",
				"svg": self.svg_marker,
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
				# "svg": self.svg_marker,  # TODO: causes marker pin not to display, but icon and shadow do
				}


def make_icons_js(layers: Iterable["Dataset"]) -> str:
	"""
	Generate the javascript file containing the icons for Leaflet.

	:param layers:
	"""

	output = StringList()
	for layer in layers:
		var_name = layer.variable_prefix + "Icon"

		output.append(f"var {var_name} = L.ExtraMarkers.icon(")
		output.append('\t' + json.dumps(layer.icon.to_dict()))
		output.append(");")
		output.blankline()

	return str(output)
