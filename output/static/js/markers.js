function load_new_markers() {
	// TODO: new markers are loaded even when layer hidden. Need to hook into show/hide to suppress when hidden and then call when shown (as if panned/zoomed)
	const bounds = map.getBounds();
	var latitudes = range(Math.floor(bounds.getSouth()), Math.floor(bounds.getNorth()) + 1, 1);
	var longitides = range(Math.floor(bounds.getWest()), Math.floor(bounds.getEast()) + 1, 1);
	var chunkIDs = [];

	latitudes.forEach(function(latitude) {
		longitides.forEach(function(longitide) {
			var id = lookup_id(latitude, longitide);
			if (id !== null) {
				console.log(`ID for ${latitude}N ${longitide}E is ${id}`);
				if (loaded_ids.includes(id)) {
					console.log(`Markers already loaded for ${latitude}N ${longitide}E`);
				} else {
					chunkIDs.push(id);
				}
			}
		});
	});

	var promise = new Promise((resolve, reject) => {
		progress.addEventListener('hidden.bs.modal', event => {
			resolve();
		}, { once: true });
	});

	progress.addEventListener('shown.bs.modal', event => {
		loadMarkers(
			chunkIDs,
			'listedBuildings',
			'listed_buildings',
			listedBuildingsIcon,
			marker_cluster_listed_buildings,
		);
	}, { once: true });

	if (chunkIDs.length > 0) {
		console.log('Showing progressbar');
		modal.show();
	}

	return promise;
}

function loadMarkers(chunkIDs, variable_prefix, filename_prefix, icon, layer) {
	var scriptPromises = [];
	var markerList = [];
	var addedChunkIDs = [];

	console.log('Loading scripts', chunkIDs);
	chunkIDs.forEach(function(id) {
		var script = document.createElement('script');
		scriptPromises.push(new Promise((resolve, reject) => {
			script.onload = function() {
				console.log('Script', id, 'loaded');
				resolve();
			};
		}));
		script.src = `data/${filename_prefix}_${id}.js`;
		document.head.appendChild(script);
	});

	Promise.all(scriptPromises).then((values) => {
		console.log('Adding markers for ids', chunkIDs);
		chunkIDs.forEach(function(id) {
			if (loaded_ids.includes(id)) {
				console.log(`Markers already loaded for ID ${id}`);
			} else {
				let var_name = variable_prefix + id;
				console.log('Accessing JS variable', var_name);
				addMarkers(window[var_name], markerList, icon);
				addedChunkIDs.push(id);
			}
		});

		layer.addLayers(markerList);
		loaded_ids.push(...addedChunkIDs);
	});
}

function addMarkers(points, markerList, icon) {
	for (var i = 0; i < points.length; i++) {
		var a = points[i];
		var title = "<a href='" + a[6] + "' target='_blank'>" + a[3] + '</a>';
		// var title = a[2].toString();
		var marker = L.marker(L.latLng(a[0], a[1]), { title: a[3], icon: icon });
		marker.bindPopup(title);
		markerList.push(marker);
	}
}

function lookup_id(latitude, longitide) {
	var lat_lookup = listedBuildingsIDLookup[latitude];
	if (lat_lookup === undefined) {
		return null;
	}

	let id = lat_lookup[longitide];

	if (id === undefined) {
		return null;
	}

	return id;
}

function loadShipwreckMarkers() {
	var chunkIDs = [0];

	var promise = new Promise((resolve, reject) => {
		progress.addEventListener('hidden.bs.modal', event => {
			resolve();
		}, { once: true });
	});

	progress.addEventListener('shown.bs.modal', event => {
		// TODO: proper ID for shipwrecks and other "small" layers
		loadMarkers(
			chunkIDs,
			'protectedWreckSites',
			'protected_wreck_sites',
			protectedWreckSitesIcon,
			marker_cluster_protected_wreck_sites,
		);
	}, { once: true });

	if (chunkIDs.length > 0) {
		console.log('Showing progressbar');
		modal.show();
	}

	return promise;
}

// https://github.com/jashkenas/underscore/blob/master/underscore.js
// MIT

// Generate an integer Array containing an arithmetic progression. A port of
// the native Python `range()` function. See
// [the Python documentation](https://docs.python.org/library/functions.html#range).
function range(start, stop, step) {
	if (stop == null) {
		stop = start || 0;
		start = 0;
	}
	if (!step) {
		step = stop < start ? -1 : 1;
	}

	var length = Math.max(Math.ceil((stop - start) / step), 0);
	var range = Array(length);

	for (var idx = 0; idx < length; idx++, start += step) {
		range[idx] = start;
	}

	return range;
}

function getClusterRadius(zoom) {
	if (zoom == MAX_ZOOM) {
		return 5;
	}

	if (zoom > 15) {
		return 40;
	}

	return 80;
}

// function disable_interaction() {
// 	map.dragging.disable();
// 	map.touchZoom.disable();
// 	map.doubleClickZoom.disable();
// 	map.scrollWheelZoom.disable();
// 	map.boxZoom.disable();
// 	map.keyboard.disable();
// 	if (map.tap) map.tap.disable();
// 	document.getElementById('map').style.cursor = 'default';
// }

// function enable_interaction() {
// 	map.dragging.enable();
// 	map.touchZoom.enable();
// 	map.doubleClickZoom.enable();
// 	map.scrollWheelZoom.enable();
// 	map.boxZoom.enable();
// 	map.keyboard.enable();
// 	if (map.tap) map.tap.enable();
// 	document.getElementById('map').style.cursor = 'grab';
// }

function updateProgressBar(processed, total, elapsed, layersArray) {
	// if it takes more than a second to load, display the progress bar:
	progressBar.style.width = Math.round(processed / total * 100) + '%';
	// }
	if (total > 0 && processed === total) {
		// all markers processed - hide the progress bar:
		modal.hide();
		// enable_interaction();
	} else if (total > 0 && elapsed > 0) {
		modal.show();
	}
}

// Function to execute promises in serial
function serial(funcs) {
	return funcs.reduce((promise, func) => promise.then(result => func().then(Array.prototype.concat.bind(result))),
		Promise.resolve([]));
}

MarkerGroup = L.Layer.extend({
	initialize: function(options) {
		console.log('Initialize called');
		// L.Layer.prototype.initialize.call(this, options);
		this._markers = [];
	},

	addLayers: function(layers) {
		this._markers.push(...layers);

		if (this._map) {
			// Don't add if the layer isn't visible
			marker_cluster_nhle.addLayers(layers);
		} else {
			// Pretend chunkedLoading happened
			modal.hide();
		}
	},

	onRemove: function(map) {
		this._map = null;
		console.log('Removing markers', this._markers);
		// TODO: chunkedLoading not triggered. Is it supposed to?
		marker_cluster_nhle.removeLayers(this._markers);
	},

	onAdd: function(map) {
		this._map = map;
		if (this._markers !== undefined) {
			marker_cluster_nhle.addLayers(this._markers);
		}
	},
});
