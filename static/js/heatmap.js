/* Based on https://github.com/python-visualization/folium/blob/main/folium/plugins/heat_map_withtime.py
*  Copyright (C) 2013-, Folium developers
*  MIT Licenced
*/

/* global HeatmapOverlay */
const HMO = HeatmapOverlay.extend({
	_update: function() {
		const generatedData = { max: this._max, min: this._min, data: [] };
		const bounds = this._map.getBounds();
		const zoom = this._map.getZoom();

		// let scale = Math.pow(2, zoom);
		// let scale = (1/zoom) * 7  // 7 is default zoom; get from map settings
		// let scale = zoom / 7  // 7 is default zoom; get from map settings
		let scale = Math.pow(zoom / 7, 2); // 7 is default zoom; get from map settings
		if (scale < 0.7) scale = 0.7;
		console.log('Zoom:', zoom, '  Scale:', scale);

		if (this._data.length === 0) {
			if (this._heatmap) {
				this._heatmap.setData(generatedData);
			}
			return;
		}

		const latLngPoints = [];
		const radiusMultiplier = this.cfg.scaleRadius ? scale : 1;
		let localMax = 0;
		let localMin = 0;
		const valueField = this.cfg.valueField;
		let len = this._data.length;

		while (len--) {
			const entry = this._data[len];
			const value = entry[valueField];
			const latlng = entry.latlng;

			// we don't wanna render points that are not even on the map ;-)
			if (!bounds.contains(latlng)) {
				continue;
			}
			// local max is the maximum within current bounds
			localMax = Math.max(value, localMax);
			localMin = Math.min(value, localMin);

			const point = this._map.latLngToContainerPoint(latlng);
			const latlngPoint = { x: Math.round(point.x), y: Math.round(point.y) };
			latlngPoint[valueField] = value;

			let radius;
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

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const TDHeatmapCustom = L.TDHeatmap.extend({
	initialize: function(data, options) {
		const heatmapCfg = {
			radius: 15,
			blur: 0.8,
			maxOpacity: 1.0,
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

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const HeatmapControl = L.Control.TimeDimensionHeatmap.extend({
	onAdd: function(map) {
		const container = L.Control.TimeDimensionHeatmap.prototype.onAdd.call(this, map);

		this._buttonBackward.title = 'Previous';
		this._buttonForward.title = 'Next';

		// this._displayDate = L.DomUtil.create('div', this.options.styleNS + ' timecontrol-date', container);
		const newDisplayDate = L.DomUtil.create('div', this.options.styleNS + ' timecontrol-date', container);
		this._displayDate.replaceWith(newDisplayDate);
		this._displayDate = newDisplayDate;

		return container;
	},

	_buttonDateClicked: function() {
	},
});
