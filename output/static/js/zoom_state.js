/*
Preserve zoom level and map position when reloading or sharing URLs
*/
function updateQueryStringParam (key, value) {
	const url = new URL(window.location.href);
	url.searchParams.set(key, value.toString()); // Add or update the parameter
	// window.history.pushState({}, null, url);
	window.history.replaceState({}, '', url);
}
function setupZoomState (map) {
	map.on('zoomend', function () {
		const zoomLvl = map.getZoom();
		updateQueryStringParam('zoom', zoomLvl);
	});
	map.on('moveend', function () {
		const centre = map.getCenter();
		updateQueryStringParam('lat', centre.lat);
		updateQueryStringParam('lng', centre.lng);
	});
}
function zoomStateFromURL (defaultZoom, defaultCentre) {
	const url = new URL(window.location.href);
	// let zoomLvl = map.getZoom();
	let zoomLvl = defaultZoom;
	if (url.searchParams.has('zoom')) {
		zoomLvl = parseInt(url.searchParams.get('zoom'));
	}
	// const centre = map.getCenter();
	const centre = defaultCentre;
	if (url.searchParams.has('lat')) {
		centre.lat = parseFloat(url.searchParams.get('lat'));
	}
	if (url.searchParams.has('lng')) {
		centre.lng = parseFloat(url.searchParams.get('lng'));
	}
	return { centre, zoomLvl };
}
function basemapFromURL (defaultBasemap, layerControl) {
	let _a;
	const url = new URL(window.location.href);
	const basemapLayers = Object.fromEntries(
		/* @ts-expect-error _layers does exist but is private */
		layerControl._layers.map((element) => [element.name, element.layer]));
	if (url.searchParams.has('basemap')) {
		const basemapName = (_a = url.searchParams.get('basemap')) !== null && _a !== void 0 ? _a : defaultBasemap;
		console.log(basemapName);
		if (basemapName in basemapLayers) {
			return basemapLayers[basemapName];
		}
	}
	return basemapLayers[defaultBasemap];
}
function setupBasemapState (map) {
	map.on('baselayerchange', (e) => updateQueryStringParam('basemap', e.name));
}
