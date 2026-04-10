function load_new_markers() {
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

	progress.addEventListener('shown.bs.modal', event => {
		loadMarkers(chunkIDs);
	}, { once: true });

	if (chunkIDs.length > 0) {
		console.log('Showing progressbar');
		modal.show();
	}
}

function loadMarkers(chunkIDs) {
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
		script.src = `data/listed_buildings_${id}.js`;
		document.head.appendChild(script);
	});

	Promise.all(scriptPromises).then((values) => {
		console.log('Adding markers for ids', chunkIDs);
		chunkIDs.forEach(function(id) {
			if (loaded_ids.includes(id)) {
				console.log(`Markers already loaded for ID ${id}`);
			} else {
				console.log('Accessing JS variable', 'listedBuildings' + id);
				addMarkers(window['listedBuildings' + id], markerList, listedBuildingsIcon);
				addedChunkIDs.push(id);
			}
		});

		marker_cluster_listed_buildings.addLayers(markerList);
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

function disable_interaction() {
	map.dragging.disable();
	map.touchZoom.disable();
	map.doubleClickZoom.disable();
	map.scrollWheelZoom.disable();
	map.boxZoom.disable();
	map.keyboard.disable();
	if (map.tap) map.tap.disable();
	document.getElementById('map').style.cursor = 'default';
}

function enable_interaction() {
	map.dragging.enable();
	map.touchZoom.enable();
	map.doubleClickZoom.enable();
	map.scrollWheelZoom.enable();
	map.boxZoom.enable();
	map.keyboard.enable();
	if (map.tap) map.tap.enable();
	document.getElementById('map').style.cursor = 'grab';
}
function updateProgressBar(processed, total, elapsed, layersArray) {
	// if (elapsed > 1000) {
	// if it takes more than a second to load, display the progress bar:
	// if (elapsed > 0) {
	// 	disable_interaction();
	// 	modal.show();
	// }
	progressBar.style.width = Math.round(processed / total * 100) + '%';
	// }
	if (processed === total) {
		// all markers processed - hide the progress bar:
		modal.hide();
		// enable_interaction();
	}
}
