'use strict';
(() => {
	// src/heatmap.ts
	var TDHeatmap = L.TimeDimension.Layer.extend({
		initialize: function(data, options) {
			const heatmapCfg = {
				radius: 15,
				blur: 0.8,
				maxOpacity: 1,
				scaleRadius: false,
				useLocalExtrema: false,
				latField: 'lat',
				lngField: 'lng',
				valueField: 'count',
				defaultWeight: 1,
				...options.heatmapOptions || {},
			};
			const layer = new HeatmapOverlay(heatmapCfg);
			L.TimeDimension.Layer.prototype.initialize.call(this, layer, options);
			this._currentLoadedTime = 0;
			this._currentTimeData = {
				data: [],
			};
			this.data = data;
			this.defaultWeight = heatmapCfg.defaultWeight || 1;
		},
		onAdd: function(map) {
			L.TimeDimension.Layer.prototype.onAdd.call(this, map);
			map.addLayer(this._baseLayer);
			if (this._timeDimension) {
				this._getDataForTime(this._timeDimension.getCurrentTime());
			}
		},
		// @ts-expect-error  // TODO
		_onNewTimeLoading: function(ev) {
			this._getDataForTime(ev.time);
		},
		isReady: function(time) {
			return this._currentLoadedTime === time;
		},
		_update: function() {
			this._baseLayer.setData(this._currentTimeData);
			return true;
		},
		_getDataForTime: function(time) {
			delete this._currentTimeData.data;
			this._currentTimeData.data = [];
			console.log('time=', time);
			const data = Array.prototype.concat(...this.data.slice(0, time));
			for (let i = 0; i < data.length; i++) {
				this._currentTimeData.data.push({
					lat: data[i][0],
					lng: data[i][1],
					count: data[i].length > 2 ? data[i][2] : this.defaultWeight,
				});
			}
			this._currentLoadedTime = time;
			if (this._timeDimension && time === this._timeDimension.getCurrentTime()
				&& !this._timeDimension.isLoading())
			{
				this._update();
			}
			this.fire('timeload', { time });
		},
	});
	var TDHeatLayer = TDHeatmap.extend({
		initialize: function(data, options) {
			const heatmapCfg = {
				minOpacity: 0.05,
				maxZoom: 18,
				radius: 25,
				blur: 15,
				max: 1,
				...options.heatmapOptions || {},
			};
			const layer = new L.HeatLayer([], heatmapCfg);
			L.TimeDimension.Layer.prototype.initialize.call(this, layer, options);
			this._currentLoadedTime = 0;
			this._currentTimeData = {
				data: [],
			};
			this.data = data;
		},
		_update: function() {
			console.log(this._currentTimeData.data);
			this._baseLayer.setLatLngs(this._currentTimeData.data);
			return true;
		},
	});
	var TimeDimensionControl = L.Control.TimeDimension.extend({
		initialize: function(index, options) {
			options.playerOptions = {
				buffer: 1,
				minBufferReady: -1,
				...options.playerOptions || {},
			};
			L.Control.TimeDimension.prototype.initialize.call(this, options);
			this.index = index;
		},
		_getDisplayDateFormat: function(date) {
			return this.index[date.getTime() - 1];
		},
	});

	// src/markergroup.ts
	var MarkerGroup = L.Layer.extend({
		initialize: function(cluster, _options) {
			console.log('Initialize called');
			this._markers = [];
			this._marker_cluster = cluster;
		},
		/**
		 * Add layers (markers) to the group and to the actual marker cluster.
		 *
		 * @param layers The layers/markers to add.
		 * @param addToCluster Whether to add the markers to the marker cluster. Default true.
		 */
		addLayers: function(layers, addToCluster = true) {
			if (this._map) {
				this._marker_cluster.addLayers(this.internLayer(layers, addToCluster));
			}
		},
		/**
		 * Like addLayers, adds to the internal list of markers but doesn't add to map.
		 *
		 * @param layers The layers/markers to add.
		 * @param addToCluster Whether to add the markers to the marker cluster. Default true.
		 *
		 * @returns The list of markers to add to the map (empty if the layer is not visible)
		 */
		/*
    */
		internLayers: function(layers, addToCluster = true) {
			this._markers.push(...layers);
			if (this._map && addToCluster) {
				return layers;
			}
			return [];
		},
		onRemove: function(_map) {
			this._map = null;
			console.log('Removing markers', this._markers);
			this._marker_cluster.removeLayers(this._markers);
			return this;
		},
		onAdd: function(map) {
			this._map = map;
			if (this._markers !== void 0) {
				this._marker_cluster.addLayers(this._markers);
			}
			return this;
		},
	});

	// src/polymarker.ts
	var PolyMarker = L.Marker.extend({
		// TODO: highlight polygon when marker clicked
		initialize: function(latlng, polyPoints, options) {
			L.Marker.prototype.initialize.call(this, latlng, options);
			this._polygons = [];
			if (polyPoints) {
				polyPoints.forEach((p) => {
					let polygonOptions = {};
					if (options.icon) {
						if ('markerColor' in options.icon.options) {
							polygonOptions = { color: options.icon.options.markerColor };
						}
					}
					this._polygons.push(L.polygon(p, polygonOptions));
				});
			}
		},
		onAdd: function(map) {
			console.log('Add polygons', this._polygons);
			L.Marker.prototype.onAdd.call(this, map);
			if (this._polygons) {
				this._polygons.forEach((p) => {
					p.addTo(map);
				});
			}
			return this;
		},
		onRemove: function(map) {
			console.log('Remove polygons', this._polygons);
			L.Marker.prototype.onRemove.call(this, map);
			if (this._polygons) {
				this._polygons.forEach((p) => {
					p.remove();
				});
			}
			return this;
		},
		polygonsBindPopup: function(content, options) {
			this._polygons.forEach((p) => {
				p.bindPopup(content, options);
			});
		},
	});

	// src/utils.ts
	function serial(funcs) {
		return funcs.reduce(
			(promise, func) => promise.then((result) => func().then(Array.prototype.concat.bind(result))),
			Promise.resolve([]),
		);
	}
	function disableInteraction(map, mapElement) {
		map.dragging.disable();
		map.touchZoom.disable();
		map.doubleClickZoom.disable();
		map.scrollWheelZoom.disable();
		map.boxZoom.disable();
		map.keyboard.disable();
		mapElement.style.cursor = 'default';
	}
	function enableInteraction(map, mapElement) {
		map.dragging.enable();
		map.touchZoom.enable();
		map.doubleClickZoom.enable();
		map.scrollWheelZoom.enable();
		map.boxZoom.enable();
		map.keyboard.enable();
		mapElement.style.cursor = 'grab';
	}

	// src/main.ts
	L.PolyMarker = PolyMarker;
	L.MarkerGroup = MarkerGroup;
	L.Util.serial = serial;
	L.Util.disableInteraction = disableInteraction;
	L.Util.enableInteraction = enableInteraction;
	L.TDHeatmap = TDHeatmap;
	L.TDHeatLayer = TDHeatLayer;
	L.Control.TimeDimensionHeatmap = TimeDimensionControl;
})();
