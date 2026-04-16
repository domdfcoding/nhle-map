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
			script.onerror = function() {
				reject();
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
	}).catch(function(rej) {
		console.log('Error loading markers: ', rej);
		alert('Error loading markers');
		modal.hide();
	});
}

function addMarkers(points, markerList, icon) {
	for (var i = 0; i < points.length; i++) {
		var a = points[i];
		var title = "<a href='" + a[6] + "' target='_blank'>" + a[3] + '</a>';
		// var title = a[2].toString();
		var marker = new L.PolyMarker(
			L.latLng(a[0], a[1]),
			// (a[7] ? a[7]: null),
			a[7],
			{ title: a[3], icon: icon },
		);
		// TODO: constants for indices rather than magic numbers
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

function loadShipwreckMarkers(ChunkID) {
	return loadSmallDataset(
		ChunkID,
		'protectedWreckSites',
		'protected_wreck_sites',
		protectedWreckSitesIcon,
		marker_cluster_protected_wreck_sites,
	);
}

function loadBPNMarkers(ChunkID) {
	return loadSmallDataset(
		ChunkID,
		'buildingPreservationNotices',
		'building_preservation_notices',
		buildingPreservationNoticesIcon,
		marker_cluster_building_preservation_notices,
	);
}

function loadImmunityMarkers(ChunkID) {
	return loadSmallDataset(
		ChunkID,
		'certificatesOfImmunity',
		'certificates_of_immunity',
		certificatesOfImmunityIcon,
		marker_cluster_certificates_of_immunity,
	);
}
function loadParksGardensMarkers(ChunkID) {
	return loadSmallDataset(
		ChunkID,
		'parksGardens',
		'parks_and_gardens',
		parksGardensIcon,
		marker_cluster_parks_and_gardens,
	);
}

function loadBattlefieldMarkers(ChunkID) {
	return loadSmallDataset(
		ChunkID,
		'battlefields',
		'battlefields',
		battlefieldsIcon,
		marker_cluster_battlefields,
	);
}

function loadScheduledMonumentMarkers(ChunkID) {
	return loadSmallDataset(
		ChunkID,
		'scheduledMonuments',
		'scheduled_monuments',
		scheduledMonumentsIcon,
		marker_cluster_scheduled_monuments,
	);
}

function loadDeDesignatedMarkers(ChunkID) {
	return loadSmallDataset(
		ChunkID,
		'deDesignated',
		'de_designated',
		deDesignatedIcon,
		marker_cluster_de_designated,
	);
}
function loadWorldHeritageMarkers(ChunkID) {
	return loadSmallDataset(
		ChunkID,
		'worldHeritageSites',
		'world_heritage_sites',
		worldHeritageSitesIcon,
		marker_cluster_world_heritage_sites,
	);
}

function loadSmallDataset(chunkID, variable_prefix, filename_prefix, icon, layer) {
	var chunkIDs = [chunkID];

	var promise = new Promise((resolve, reject) => {
		progress.addEventListener('hidden.bs.modal', event => {
			resolve();
		}, { once: true });
	});

	progress.addEventListener('shown.bs.modal', event => {
		// TODO: proper ID for shipwrecks and other "small" layers
		loadMarkers(
			chunkIDs,
			variable_prefix,
			filename_prefix,
			icon,
			layer,
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
		return 20;
	}

	if (zoom > 12) {
		return 40;
	}

	return 80;
}


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


MarkerGroup = L.MarkerGroup.extend({
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

});
