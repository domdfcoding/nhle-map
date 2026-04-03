#!/usr/bin/env python3
#
#  __init__.py
"""
Jinja2 templates.
"""
#
#  Copyright © 2025 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import base64

# 3rd party
import jinja2
from domdf_python_tools.paths import PathPlus
from jinja2 import Environment

# from jinja2_workarounds import MultiLineInclude  # type: ignore[import-untyped]

__all__ = ["base64_encode", "render_template"]


def base64_encode(value: str) -> str:
	"""
	Encode the given string as base64.

	:param value:
	"""

	return base64.b64encode(value.encode("utf-8")).decode("utf-8")


templates = Environment(  # nosec: B701
		loader=jinja2.FileSystemLoader(str((PathPlus(__file__).parent).absolute())),
		undefined=jinja2.StrictUndefined,
		# extensions=[MultiLineInclude],
		)

templates.globals["github_url"] = "https://github.com/domdfcoding/nhle-map"
templates.globals["list"] = list
templates.globals["sorted"] = sorted
templates.globals["enumerate"] = enumerate
templates.globals["len"] = len

templates.filters["base64_encode"] = base64_encode


def render_template(template: str, **kwargs) -> str:
	r"""
	Render the template with the given filename with the given parameters.

	:param template:
	:param \*\*kwargs:
	"""

	return templates.get_template(template).render(**kwargs)
