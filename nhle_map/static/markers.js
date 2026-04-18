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

	var promise = new Promise((resolve, reject) => {
		progress.addEventListener('hidden.bs.modal', event => {
			resolve();
		}, { once: true });
	});

	progress.addEventListener('shown.bs.modal', event => {
		loadMarkersAllLayers(
			chunkIDs,
			[
				{
					'variable_prefix': 'battlefields',
					'layer': marker_cluster_battlefields,
					'icon': battlefieldsIcon,
				},
				{
					'variable_prefix': 'buildingPreservationNotices',
					'layer': marker_cluster_building_preservation_notices,
					'icon': buildingPreservationNoticesIcon,
				},
				{
					'variable_prefix': 'certificatesOfImmunity',
					'layer': marker_cluster_certificates_of_immunity,
					'icon': certificatesOfImmunityIcon,
				},
				{
					'variable_prefix': 'listedBuildings',
					'layer': marker_cluster_listed_buildings,
					'icon': listedBuildingsIcon,
				},
				{
					'variable_prefix': 'parksGardens',
					'layer': marker_cluster_parks_and_gardens,
					'icon': parksGardensIcon,
				},
				{
					'variable_prefix': 'protectedWreckSites',
					'layer': marker_cluster_protected_wreck_sites,
					'icon': protectedWreckSitesIcon,
				},
				{
					'variable_prefix': 'scheduledMonuments',
					'layer': marker_cluster_scheduled_monuments,
					'icon': scheduledMonumentsIcon,
				},
				{
					'variable_prefix': 'worldHeritageSites',
					'layer': marker_cluster_world_heritage_sites,
					'icon': worldHeritageSitesIcon,
				},
				{
					'variable_prefix': 'deDesignated',
					'layer': marker_cluster_de_designated,
					'icon': deDesignatedIcon,
				},
			],
		);
	}, { once: true });

	if (chunkIDs.length > 0) {
		console.log('Showing progressbar');
		modal.show();
	}

	return promise;
}

function loadMarkersAllLayers(chunkIDs, layers) {
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
		script.src = `data/nhle_${id}.js`;
		document.head.appendChild(script);
	});

	Promise.all(scriptPromises).then((values) => {
		console.log('Adding markers for ids', chunkIDs);

		chunkIDs.forEach(function(id) {
			if (loaded_ids.includes(id)) {
				console.log(`Markers already loaded for ID ${id}`);
			} else {
				layers.forEach((layer_data) => {
					let var_name = layer_data.variable_prefix + id;
					console.log('Accessing JS variable', var_name);
					var layerMarkerList = [];
					addMarkers(window[var_name], layerMarkerList, layer_data.icon);
					markerList.push(...layer_data.layer.internLayers(layerMarkerList))
				});
				addedChunkIDs.push(id);
			}
		});

		marker_cluster_nhle.addLayers(markerList);
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
	var lat_lookup = nhleIDLookup[latitude];
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
	console.log(`Update progressbar to ${processed} out of ${total}`);
	if (total > 0 && processed === total) {
		// all markers processed - hide the progress bar:
		setTimeout(e => {
			progressBar.style.width = '0';
			modal.hide();
			console.log(`Progressbar finished (${processed} out of ${total})`);
		}, 500);
	} else if (total > 0 && elapsed > 0) {
		modal.show();
	}
}

MarkerGroup = L.MarkerGroup.extend({
	/* Like addLayers, adds to the internal list of markers but doesn't add to map.
	Returns the list of markers to add to the map (none if the layer is not visible)
	*/
	internLayers: function(layers, addToCluster = true) {
		// TODO: move this function to domdf-folium-tools
		this._markers.push(...layers);

		if (this._map && addToCluster) {
			return layers;
		}

		return [];
	},

	addLayers: function(layers, addToCluster = true) {
		console.log('addLayers called; addToCluster=', addToCluster);

		marker_cluster_nhle.addLayers(this.internLayers(layers));

		if (!this._map) {
			// Pretend chunkedLoading happened
			modal.hide();
		}
	},
});
