/* Based on https://github.com/python-visualization/folium/blob/main/folium/plugins/heat_map_withtime.py
*  Copyright (C) 2013-, Folium developers
*  MIT Licenced
*/

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
		if (scale < 0.7) scale = 0.7;
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

var TDHeatmapCustom = L.TDHeatmap.extend({
	initialize: function(data, options) {
		const heatmapCfg = {
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
		const layer = new HMO(heatmapCfg);
		L.TimeDimension.Layer.prototype.initialize.call(this, layer, options);
		this._currentLoadedTime = 0;
		this._currentTimeData = {
			data: [],
		};
		this.data = data;
		this.defaultWeight = heatmapCfg.defaultWeight || 1;
	},
});
