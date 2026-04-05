# 3rd party
import branca.element
from domdf_python_tools.paths import PathPlus

# this package
from nhle_map.map import make_map, render_figure
from nhle_map.templates import render_template

map = make_map()

root: branca.element.Figure = map.get_root()  # type: ignore[assignment]

PathPlus("index.html").write_clean(render_template(
		"map.jinja2",
		**render_figure(root)._asdict(),
		))
