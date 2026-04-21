#!/usr/bin/env python3
#
#  utils.py
"""
General utilities.
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
import random
from collections.abc import Iterable
from typing import Any

# 3rd party
import domdf_folium_tools.static_files
import ujson5
from domdf_python_tools.paths import PathPlus

# this package
from nhle_map import constants
from nhle_map.icons import make_icons_js

__all__ = ["copy_static_files", "format_datetime", "format_description", "from_iso_zulu", "get_id"]

rng = random.Random("NHLE")
DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
DATE_ONLY_FORMAT = "%a, %d %b %Y"


def get_id() -> int:
	"""
	Returns a unique ID, but with the RNG same seed for every program execution.
	"""

	return rng.getrandbits(32)


def copy_static_files(static_dir: PathPlus) -> None:
	"""
	Copy CSS and JS files into the given directory.

	:param static_dir:
	"""

	# TODO: add img to domdf_folium_tools
	domdf_folium_tools.static_files.copy_static_files(
			static_dir=static_dir,
			js_files=[
					domdf_folium_tools.static_files.PythonResource("nhle_map.static", "markers.js"),
					domdf_folium_tools.static_files.PythonResource("nhle_map.static", "custom_layer_control.js"),
					],
			css_files=[domdf_folium_tools.static_files.PythonResource("nhle_map.static", "style.css")],
			)

	img_dir = static_dir / "img"

	img_dir.maybe_make(parents=True)

	domdf_folium_tools.static_files._copy_files(
			[
					domdf_folium_tools.static_files.PythonResource("nhle_map.static", "Challenge_Icon.svg"),
					],
			img_dir,
			)

	layers = constants.LAYERS
	icons_js = make_icons_js(layers)
	layer_data = []

	for layer in layers:
		layer_data.append({
				"variable_prefix": layer.variable_prefix,
				"layer": f"marker_cluster_{layer.identifier}",
				"icon": Identifier(layer.variable_prefix + "Icon"),
				"noun": layer.noun,
				})

	layer_data_js = f"const layerData = {ujson5.dumps(layer_data, indent=4, cls=JSEncoder)}"

	static_dir.joinpath("js", "layer_data.js").write_lines([
			icons_js,
			'',
			layer_data_js,
			])


class Identifier:

	def __init__(self, identifier: str):
		self._identifier = identifier


class JSEncoder(ujson5.JSON5Encoder):

	def encode(self, obj: Any, typed_dict_cls: Any | None = None) -> str:
		if isinstance(obj, Identifier):
			return obj._identifier

		return super().encode(obj, typed_dict_cls)

	def _iterencode(self, obj: Any, indent_level: int, key_path: str) -> Iterable[str]:
		if isinstance(obj, Identifier):
			yield obj._identifier
		else:
			yield from super()._iterencode(obj, indent_level, key_path)

	def default(self, obj: Any) -> ujson5.Serializable:
		if isinstance(obj, Identifier):
			return obj

		super().default(obj)


def format_description(description: str) -> str:
	"""
	Format a layer description for the about dialog.

	:param description:
	"""

	description = description.replace('\n', "\n<br>\n")
	# description = description.replace('•', "<br>•")
	description = description.replace('¬', '').replace("see below", "see above")
	return description


def format_datetime(dt: datetime.datetime | None, date_format: str = DATE_FORMAT) -> str | None:
	"""
	Format the given datetime to string.

	:param dt:
	:param date_format:
	"""

	if dt:
		return dt.strftime(date_format)

	return None


def from_iso_zulu(the_datetime: str) -> datetime.datetime:
	"""
	Constructs a :class:`datetime.datetime` object from an
	`ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`_ format string.

	This function understands the character ``Z`` as meaning Zulu time (GMT/UTC).

	:param the_datetime:
	"""  # noqa: D400

	return datetime.datetime.fromisoformat(the_datetime.replace('Z', "+00:00"))
