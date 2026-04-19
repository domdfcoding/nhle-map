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
			// TODO: generate with jinja2 and populate from LAYERS
			chunkIDs,
			[
				{
					'variable_prefix': 'battlefields',
					'layer': marker_cluster_battlefields,
					'icon': battlefieldsIcon,
					'noun': 'Battlefield',
				},
				{
					'variable_prefix': 'buildingPreservationNotices',
					'layer': marker_cluster_building_preservation_notices,
					'icon': buildingPreservationNoticesIcon,
					'noun': 'Building Preservation Notice',
				},
				{
					'variable_prefix': 'certificatesOfImmunity',
					'layer': marker_cluster_certificates_of_immunity,
					'icon': certificatesOfImmunityIcon,
					'noun': 'Certificate of Immunity',
				},
				{
					'variable_prefix': 'listedBuildings',
					'layer': marker_cluster_listed_buildings,
					'icon': listedBuildingsIcon,
					'noun': 'Listed Building',
				},
				{
					'variable_prefix': 'parksGardens',
					'layer': marker_cluster_parks_and_gardens,
					'icon': parksGardensIcon,
					'noun': 'Park and Garden',
				},
				{
					'variable_prefix': 'protectedWreckSites',
					'layer': marker_cluster_protected_wreck_sites,
					'icon': protectedWreckSitesIcon,
					'noun': 'Protected Wreck',
				},
				{
					'variable_prefix': 'scheduledMonuments',
					'layer': marker_cluster_scheduled_monuments,
					'icon': scheduledMonumentsIcon,
					'noun': 'Scheduled Monument',
				},
				{
					'variable_prefix': 'worldHeritageSites',
					'layer': marker_cluster_world_heritage_sites,
					'icon': worldHeritageSitesIcon,
					'noun': 'World Heritage Site',
				},
				{
					'variable_prefix': 'deDesignated',
					'layer': marker_cluster_de_designated,
					'icon': deDesignatedIcon,
					'noun': 'De-designated Site',
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
					addMarkers(window[var_name], layerMarkerList, layer_data.icon, layer_data.noun);
					markerList.push(...layer_data.layer.internLayers(layerMarkerList));
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

function addMarkers(points, markerList, icon, noun) {
	for (var i = 0; i < points.length; i++) {
		var a = points[i];
		// var popupText = "<a href='" + a[6] + "' target='_blank'>" + a[3] + '</a>';
		var listingGrade = a[4] ? `Grade: <strong>${a[4]}</strong><br>` : '';
		var listingLink = a[6] ? `<a href="${a[6]}" class="card-link" target='_blank'>View list entry</a>` : '';
		var date = a[5] ? `Date: <strong>${a[5]}</strong>` : '';
		var notes = a[7] ? `<p>${a[7]}</p>` : '';
		var popupText = `
<div class="card border-0">
  <div class="card-body p-0">
    <h5 class="card-title">${a[3]}</h5>
    <h6 class="card-subtitle mb-2 text-muted">${noun}</h6>
    <p class="card-text">
		${listingGrade}
	    List Entry Number: <strong>${a[2]}</strong>
		<br>
	    ${date}
	</p>
    ${notes}
    ${listingLink}
  </div>
</div>
		`;
		var marker = new L.PolyMarker(
			L.latLng(a[0], a[1]),
			a[8],
			{ title: a[3], icon: icon },
		);
		// TODO: constants for indices rather than magic numbers
		marker.bindPopup(popupText);
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
