let loadLock = false;

/* global loadedIDs,progress,layerData,map */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function loadNewMarkers() {
	if (loadLock === true) {
		return null;
	}

	loadLock = true;
	console.log('loadNewMarkers() called');

	const bounds = map.getBounds();
	const latitudes = range(Math.floor(bounds.getSouth()), Math.floor(bounds.getNorth()) + 1, 1);
	const longitides = range(Math.floor(bounds.getWest()), Math.floor(bounds.getEast()) + 1, 1);
	const chunkIDs = [];

	latitudes.forEach(function(latitude) {
		longitides.forEach(function(longitide) {
			const id = lookupID(latitude, longitide);
			if (id !== null) {
				console.log(`ID for ${latitude}N ${longitide}E is ${id}`);
				if (loadedIDs.includes(id)) {
					console.log(`Markers already loaded for ${latitude}N ${longitide}E`);
				} else {
					chunkIDs.push(id);
				}
			}
		});
	});

	const promise = new Promise((resolve) => {
		progress.addEventListener('hidden.bs.modal', _e => {
			resolve();
		}, { once: true });
	});

	if (chunkIDs.length > 0) {
		progress.addEventListener('shown.bs.modal', _e => {
			loadMarkersAllLayers(
				chunkIDs,
				layerData,
			);
		}, { once: true });

		console.log('Showing progressbar');
		modal.show();
	} else {
		loadLock = false;
	}

	return promise;
}

/* global marker_cluster_nhle */
function loadMarkersAllLayers(chunkIDs, layers) {
	const scriptPromises = [];
	const markerList = [];
	const addedChunkIDs = [];

	console.log('Loading scripts', chunkIDs);
	chunkIDs.forEach(function(id) {
		const script = document.createElement('script');
		scriptPromises.push(new Promise((resolve, reject) => {
			script.onload = function() {
				console.log('Script', id, 'loaded');
				resolve();
			};
			script.onerror = function(oError) {
				reject(oError);
			};
		}));
		script.src = `data/nhle_${id}.js`;
		document.head.appendChild(script);
	});

	Promise.all(scriptPromises).then((_values) => {
		console.log('Adding markers for ids', chunkIDs);

		chunkIDs.forEach(function(id) {
			if (loadedIDs.includes(id)) {
				console.log(`Markers already loaded for ID ${id}`);
			} else {
				layers.forEach((thisLayerData) => {
					const varName = thisLayerData.variable_prefix + id;
					console.log('Accessing JS variable', varName);
					const layerMarkerList = [];
					addMarkers(window[varName], layerMarkerList, thisLayerData.icon, thisLayerData.noun);
					markerList.push(...window[thisLayerData.layer].internLayers(layerMarkerList));
				});
				addedChunkIDs.push(id);
			}
		});

		marker_cluster_nhle.addLayers(markerList);
		loadedIDs.push(...addedChunkIDs);

		if (markerList.length === 0) {
			// No clustering will take place if we're not adding any new markers
			modal.hide();
			console.log('Hiding modal; nothing to add');
			loadLock = false;
		}
	}).catch(function(rej) {
		console.log('Error loading markers: ', rej);
		alert('Error loading markers');
		modal.hide();
		loadLock = false;
	});
}

function _polygonPlural(polygons) {
	return polygons.length > 1 ? 'Polygons' : 'Polygon'; // TODO: handle single poly with gaps
}

class MarkerData {
	constructor(lat, lng, num, name, grade, listDate, link, notes = null, polyPoints = null, showPoly = true) {
		this.lat = lat;
		this.lng = lng;
		this.num = num;
		this.name = name;
		this.grade = grade;
		this.listDate = listDate;
		this.link = link;
		this.notes = notes;
		this.showPoly = showPoly;

		if (polyPoints === null || polyPoints === undefined) {
			this.polyPoints = [];
		} else {
			this.polyPoints = polyPoints;
		}
	}

	formatPopup(noun) {
		// const popupText = "<a href='" + this.link + "' target='_blank'>" + a.name + '</a>';

		const listingGrade = this.grade ? `Grade: <strong>${this.grade}</strong><br>` : '';
		const listingLink = this.link
			? `<a href="${this.link}" class="card-link" target='_blank'>View list entry</a>`
			: '';
		const date = this.listDate ? `Date: <strong>${this.listDate}</strong>` : '';
		const notes = this.notes ? `<p>${this.notes}</p>` : '';
		const polygonsText = _polygonPlural(this.polyPoints);
		const highlightText = this.showPoly ? 'Highlight' : 'Show';
		const highlightButton = this.polyPoints.length
			? `<a role="button" class="card-link" id="highlightButton">${highlightText} ${polygonsText}</a>`
			: '';

		const popupText = `
<div class="nhle-popup card border-0">
  <div class="card-body p-0">
    <h5 class="card-title">${this.name}</h5>
    <h6 class="card-subtitle mb-2 text-muted">${noun}</h6>
    <p class="card-text">
		${listingGrade}
	    List Entry Number: <strong>${this.num}</strong>
		<br>
	    ${date}
	</p>
    ${notes}
    ${listingLink}
    ${highlightButton}
  </div>
</div>`;
		return popupText;
	}
}

function _popupOnClick(e) {
	if (!this._popup || !this._map) {
		return;
	}
	L.DomEvent.stop(e);

	if (this._map.hasLayer(this._popup)) {
		this.closePopup();
	} else {
		this.openPopup(e.latlng);
	}
}

function resetMarkerPolygons(marker) {
	marker.polygonsSetStyle({ dashArray: null });
	marker.polygonsHighlighted = false;
}

function _setupPopupOnClick(layer) {
	layer.off('click', layer._openPopup);
	layer.on('click', _popupOnClick, layer);
	map.on('click', (_e) => {
		layer.closePopup();
	});
}

function _setupPopupButtonHandlers(marker, popup, defaultShowPoly) {
	console.log('Popup added', window.performance);
	const button = popup.getElement().querySelector('#highlightButton');

	if (!defaultShowPoly && marker.showPolygons) {
		button.innerHTML = `Hide ${_polygonPlural(marker._polygons)}`;
	}

	if (!button.dataset.setup) {
		button.addEventListener('click', (_e) => {
			if (defaultShowPoly) {
				if (marker.polygonsHighlighted) {
					resetMarkerPolygons(marker);
				} else {
					marker.polygonsSetStyle({ dashArray: '10, 10' });
					map.fire('polygonhighlight', marker);
					marker.polygonsHighlighted = true;
				}
			} else {
				if (marker.showPolygons) {
					marker.removePolygons();
					marker.showPolygons = false;
					marker.closePopup(); // If the popup is associated with the polygon it will go with the polygon. This ensures consistent behaviour.
				} else {
					marker.addPolygons();
					marker.showPolygons = true;
					marker.closePopup(); // To match behaviour when clicking Hide Polygon
				}
			}
		});
		button.dataset.setup = true;
	}
}

const Popup = L.Popup.extend({
	_initLayout() {
		L.Popup.prototype._initLayout.call(this);
		this._wrapper.style = `outline-color: ${this.options.borderColor}`;
	},

	openOn: function(map) {
		const ret = L.Popup.prototype.openOn.call(this, map);
		this.fire('shewn');
		return ret;
	},
});

function addMarkers(points, markerList, icon, noun) {
	const markerClickClosePopup = false;
	// const markerClickClosePopup = true;

	for (let i = 0; i < points.length; i++) {
		const a = new MarkerData(...points[i]);

		// TODO: large polygons disappear after zooming or panning if marker way off screen
		const marker = new L.PolyMarker(
			L.latLng(a.lat, a.lng),
			a.polyPoints,
			{ title: a.name, icon },
			{},
			a.showPoly,
		);

		let closeOnClick = false;
		if (!markerClickClosePopup) {
			closeOnClick = a.polyPoints.length === 0;
		}

		const popup = new Popup({
			keepInView: false,
			autoPanPaddingTopLeft: [45, 0],
			autoPanPaddingBottomRight: [65, 0],
			closeOnClick,
			borderColor: icon.options.markerColor,
		});

		popup.setContent(a.formatPopup(noun));
		marker.bindPopup(popup);
		marker.polygonsBindPopup(popup);
		marker._polygons.forEach((p) => {
			_setupPopupOnClick(p);
		});

		if (markerClickClosePopup) {
			_setupPopupOnClick(marker);
		}
		markerList.push(marker);

		if (a.polyPoints.length) {
			popup.on('shewn', (_e) => {
				_setupPopupButtonHandlers(marker, popup, a.showPoly);
			});
			map.on('polygonhighlight', (e) => {
				// TODO: why can't markers be compared directly (not equal)
				if (e._leaflet_id !== marker._leaflet_id) {
					resetMarkerPolygons(marker);
				}
			});
		}
	}
}

/* global nhleIDLookup */
function lookupID(latitude, longitide) {
	const latLookup = nhleIDLookup[latitude];
	if (latLookup === undefined) {
		return null;
	}

	const id = latLookup[longitide];

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

	const length = Math.max(Math.ceil((stop - start) / step), 0);
	const range = Array(length);

	for (let idx = 0; idx < length; idx++, start += step) {
		range[idx] = start;
	}

	return range;
}

/* global MAX_ZOOM */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function getClusterRadius(zoom) {
	if (zoom === MAX_ZOOM) {
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

/* global modal,progressBar */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function updateProgressBar(processed, total, elapsed, _layersArray) {
	// if it takes more than a second to load, display the progress bar:
	progressBar.style.width = Math.round(processed / total * 100) + '%';
	console.log(`Update progressbar to ${processed} out of ${total}`);
	if (total > 0 && processed === total) {
		// all markers processed - hide the progress bar:
		setTimeout(_e => {
			progressBar.style.width = '0';
			modal.hide();
			console.log(`Progressbar finished (${processed} out of ${total})`);
			loadLock = false;
		}, 500);
	} else if (total > 0 && elapsed > 0) {
		modal.show();
	}
}
