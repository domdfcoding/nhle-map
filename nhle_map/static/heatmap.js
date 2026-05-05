/* Based on https://github.com/python-visualization/folium/blob/main/folium/plugins/heat_map_withtime.py
*  Copyright (C) 2013-, Folium developers
*  MIT Licenced
*/

if (typeof HeatmapOverlay !== 'undefined') {
	var HMO = HeatmapOverlay.extend({
		_update: function() {
			var bounds, zoom, scale;
			var generatedData = { max: this._max, min: this._min, data: [] };

			bounds = this._map.getBounds();
			zoom = this._map.getZoom();
			// scale = Math.pow(2, zoom);
			//   scale = (1/zoom) * 7  // 7 is default zoom; get from map settings
			// scale = zoom / 7  // 7 is default zoom; get from map settings
			scale = Math.pow(zoom / 7, 2); // 7 is default zoom; get from map settings
			console.log('Zoom:', zoom, '  Scale:', scale);

			if (this._data.length == 0) {
				if (this._heatmap) {
					this._heatmap.setData(generatedData);
				}
				return;
			}

			var latLngPoints = [];
			var radiusMultiplier = this.cfg.scaleRadius ? scale : 1;
			var localMax = 0;
			var localMin = 0;
			var valueField = this.cfg.valueField;
			var len = this._data.length;

			while (len--) {
				var entry = this._data[len];
				var value = entry[valueField];
				var latlng = entry.latlng;

				// we don't wanna render points that are not even on the map ;-)
				if (!bounds.contains(latlng)) {
					continue;
				}
				// local max is the maximum within current bounds
				localMax = Math.max(value, localMax);
				localMin = Math.min(value, localMin);

				var point = this._map.latLngToContainerPoint(latlng);
				var latlngPoint = { x: Math.round(point.x), y: Math.round(point.y) };
				latlngPoint[valueField] = value;

				var radius;

				if (entry.radius) {
					radius = entry.radius * radiusMultiplier;
				} else {
					radius = (this.cfg.radius || 2) * radiusMultiplier;
				}
				latlngPoint.radius = radius;
				latLngPoints.push(latlngPoint);
			}
			if (this.cfg.useLocalExtrema) {
				generatedData.max = localMax;
				generatedData.min = localMin;
			}

			generatedData.data = latLngPoints;

			this._heatmap.setData(generatedData);
		},
	});
}

var TDHeatmap = L.TimeDimension.Layer.extend({
	initialize: function(data, options) {
		var heatmapCfg = {
			radius: 15,
			blur: 0.8,
			maxOpacity: 1.,
			scaleRadius: false,
			useLocalExtrema: false,
			latField: 'lat',
			lngField: 'lng',
			valueField: 'count',
			defaultWeight: 1,
			...options.heatmapOptions || {},
		};
		var layer = new HMO(heatmapCfg);
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
	_onNewTimeLoading: function(ev) {
		this._getDataForTime(ev.time);
		return;
	},
	isReady: function(time) {
		return (this._currentLoadedTime == time);
	},
	_update: function() {
		this._baseLayer.setData(this._currentTimeData);
		return true;
	},
	_getDataForTime: function(time) {
		delete this._currentTimeData.data;
		this._currentTimeData.data = [];
		console.log('time=', time);
		// var data = this.data[time-1];
		var data = Array.prototype.concat(...this.data.slice(0, time));
		for (var i = 0; i < data.length; i++) {
			this._currentTimeData.data.push({
				lat: data[i][0],
				lng: data[i][1],
				count: data[i].length > 2 ? data[i][2] : this.defaultWeight,
			});
		}
		this._currentLoadedTime = time;
		if (this._timeDimension && time == this._timeDimension.getCurrentTime() && !this._timeDimension.isLoading()) {
			this._update();
		}
		this.fire('timeload', {
			time: time,
		});
	},
});

var TDHeatLayer = TDHeatmap.extend({
	initialize: function(data, options) {
		var heatmapCfg = {
			minOpacity: 0.05,
			maxZoom: 18,
			radius: 25,
			blur: 15,
			max: 1.0,
			...options.heatmapOptions || {},
		};
		var layer = new L.HeatLayer([], heatmapCfg);
		L.TimeDimension.Layer.prototype.initialize.call(this, layer, options);
		this._currentLoadedTime = 0;
		this._currentTimeData = {
			data: [],
		};
		this.data = data;
		// this.defaultWeight = heatmapCfg.defaultWeight || 1;
	},
	_update: function() {
		console.log(this._currentTimeData.data);
		this._baseLayer.setLatLngs(this._currentTimeData.data);
		return true;
	},
});

L.Control.TimeDimensionCustom = L.Control.TimeDimension.extend({
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
