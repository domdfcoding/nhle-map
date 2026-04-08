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
import random

# 3rd party
import domdf_folium_tools.static_files
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import PathPlus

# this package
from nhle_map.icons import write_icons_js

__all__ = ["copy_static_files", "get_id"]

rng = random.Random("NHLE")


def get_id() -> int:
	"""
	Returns a unique ID, but with the RNG same seed for every program execution.
	"""

	return rng.getrandbits(32)


def _copy_file(module: str, filename: str, target_dir: PathPlus) -> None:
	(target_dir / filename).write_text(importlib_resources.read_text(module, filename))


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

	write_icons_js(static_dir / "js")
