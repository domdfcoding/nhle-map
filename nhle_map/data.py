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
import json
from collections import defaultdict

# 3rd party
import geopandas
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from domdf_python_tools.typing import PathLike

# this package
from nhle_map.utils import get_id

__all__ = ["chunk_data", "get_chunk_js"]


def get_chunk_js(features: list, id: int, variable_prefix: str = "listedBuildings") -> str:
	"""
	Returns the javascript array for the given features chunk.

	:param features:
	:param id:
	"""

	output = StringList()

	output.append("// Lat,Lng,Number,Name,Grade,ListDate,Link")
	output.append(f"var {variable_prefix}{id} = [")

	for item in features:
		number = item["ListEntry"]
		name = item["Name"]
		grade = item["Grade"]
		list_date = item["ListDate"]
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
		lat_range: range,
		lng_range: range,
		output_directory: PathLike,
		variable_prefix: str = "listedBuildings",
		filename_prefix: str = "listed_buildings",
		):

	output_dir = PathPlus(output_directory)
	output_dir.maybe_make(parents=True)

	id_lookup = defaultdict(dict)

	for latitude in lat_range:
		for longitide in lng_range:
			id = get_id()
			id_lookup[latitude][longitide] = id
			subset = data.cx[longitide:longitide + 1, latitude:latitude + 1]
			if not len(subset):
				continue

			chunk_js = get_chunk_js(subset.to_dict("records"), id, variable_prefix=variable_prefix)
			output_dir.joinpath(f"{filename_prefix}_{id}.js").write_clean(chunk_js)

	id_lookup_js = f"{variable_prefix}IDLookup = {json.dumps(id_lookup, indent=4)}"
	output_dir.joinpath(f"{filename_prefix}_id_lookup.js").write_clean(id_lookup_js)
