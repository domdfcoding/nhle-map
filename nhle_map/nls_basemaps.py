#!/usr/bin/env python3
#
#  nls_basemaps.py
"""
Leaflet basemap tile layers using historic OS mapping from the National Library of Scotland.
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

# 3rd party
from domdf_folium_tools.elements import NLSTileLayer

# TODO: fallback URLs so the whole country is covered when tiles are unavailable with primary URL.

__all__ = ["os10k", "os1250", "os2500", "os25inch"]

os10k = NLSTileLayer(
		"OS 1:10,000 1949-1972",
		"https://geo.nls.uk/mapdata3/os/britain10knationalgridnew/{z}/{x}/{y}.png",
		max_native_zoom=16,
		show=False,
		)

os1250 = NLSTileLayer(
		"OS 1:1,250 1949-1975",
		"https://geo.nls.uk/maps/os/1250_B_2eng/{z}/{x}/{y}.png",
		max_native_zoom=20,
		show=False,
		)

os2500 = NLSTileLayer(
		"OS 1:2,500 1948-1975",
		"https://geo.nls.uk/maps/os/2500_A_1S/{z}/{x}/{y}.png",
		max_native_zoom=18,
		show=False,
		)

os25inch = NLSTileLayer(
		"OS 25 Inch, 1892-1914",
		"https://mapseries-tilesets.s3.amazonaws.com/25_inch/stafford/{z}/{x}/{y}.png",
		max_native_zoom=18,
		show=False,
		)
