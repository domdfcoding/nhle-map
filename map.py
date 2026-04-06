# 3rd party
import branca.element
from domdf_folium_tools.elements import render_figure
from domdf_python_tools.paths import PathPlus

# this package
from nhle_map.map import make_map
from nhle_map.templates import render_template
from nhle_map.utils import copy_static_files

map = make_map()
copy_static_files(PathPlus("output/static"))

root: branca.element.Figure = map.get_root()  # type: ignore[assignment]

PathPlus("index.html").write_clean(render_template(
		"map.jinja2",
		**render_figure(root)._asdict(),
		))
