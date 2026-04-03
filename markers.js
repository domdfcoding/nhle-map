
function load_new_markers() {
	// const centre = map.getCenter();
	// console.log("lat", Math.floor(centre.lat))
	// console.log("lng", Math.floor(centre.lng))
	const bounds = map.getBounds();
	console.log("bounds", bounds)
	console.log("SW", Math.floor(bounds.getSouth()), Math.floor(bounds.getWest()))
	console.log("NE", Math.floor(bounds.getNorth()), Math.floor(bounds.getEast()))
	var latitudes = range(Math.floor(bounds.getSouth()), Math.floor(bounds.getNorth()) + 1, 1)
	var longitides = range(Math.floor(bounds.getWest()), Math.floor(bounds.getEast()) + 1, 1)
	console.log(latitudes)
	console.log(longitides)
	latitudes.forEach(function (latitude) {
		longitides.forEach(function (longitide) {
			console.log(latitude, longitide)
			loadMarkers(latitude, longitide)
		});
	});
	// loadMarkers(Math.floor(centre.lat),Math.floor(centre.lng))
}



function addMarkers(points, markerList) {
	for (var i = 0; i < points.length; i++) {
		var a = points[i];
		var title = "<a href='" + a[6] + "' target='_blank'>" + a[3] + "</a>";
		// var title = a[2].toString();
		var marker = L.marker(L.latLng(a[0], a[1]), { title: title });
		marker.bindPopup(title);
		markerList.push(marker);
	}
}

function lookup_id(latitude, longitide) {
	var lat_lookup = id_lookup[latitude]
	if (lat_lookup === undefined) {
		return null
	}

	let id = lat_lookup[longitide];

	if (id === undefined) {
		return null
	}

	return id
}

function loadMarkers(latitude, longitide) {
	var id = lookup_id(latitude, longitide);
	if (loaded_ids.includes(id)) {
		console.log(`Markers already loaded for ${latitude}N ${longitide}E`);
		return
	}

	var script = document.createElement('script');

	var markerList = [];

	progress.addEventListener('shown.bs.modal', event => {
		if (loaded_ids.includes(id)) {
			console.log(`Markers already loaded for ${latitude}N ${longitide}E`);
			return
		}
		
		markers.addLayers(markerList);
		console.log('end clustering: ' + window.performance.now());

		loaded_ids.push(id);
	}, { once: true })

	script.onload = function () {
		console.log("Script loaded")
		if (loaded_ids.includes(id)) {
			console.log(`Markers already loaded for ${latitude}N ${longitide}E`);
			return
		}


		console.log('start creating markers: ' + window.performance.now());
		addMarkers(window["addressPoints" + id], markerList);

		console.log('start clustering: ' + window.performance.now());
		// disable_interaction();

		modal.show()

	};

	script.src = `points_${id}.js`;
	document.head.appendChild(script);

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
	if (zoom > 15) {
		return 30
	}
	// TODO: intermediate
	else {
		return 80
	}
}


function updateProgressBar(processed, total, elapsed, layersArray) {
	// if (elapsed > 1000) {
	// if it takes more than a second to load, display the progress bar:
	// 	if (elapsed > 0) {
	// 		disable_interaction();
	// 		modal.show()
	// }
	progressBar.style.width = Math.round(processed / total * 100) + '%';
	// }
	if (processed === total) {
		// all markers processed - hide the progress bar:
		modal.hide()
		// enable_interaction();
	}
}

