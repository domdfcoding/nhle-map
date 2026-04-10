// Adapted from https://github.com/jieter/leaflet.layerscontrol-minimap
// Copyright (c) 2013, Jan Pieter Waagmeester
// All rights reserved.

// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:

// 1. Redistributions of source code must retain the above copyright notice, this
//    list of conditions and the following disclaimer.
// 2. Redistributions in binary form must reproduce the above copyright notice,
//    this list of conditions and the following disclaimer in the documentation
//    and/or other materials provided with the distribution.

// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
// ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
// ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
// (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
// LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
// ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

CustomLayerControl = L.Control.Layers.MinimapToggle.extend({
	_addItem: function(obj) {
		var container = obj.overlay ? this._overlaysList : this._baseLayersList;

		if (obj.overlay) {
			var labelClass = 'leaflet-lc-overlay-container';
		} else {
			var labelClass = 'leaflet-minimap-container';
		}

		var label = L.DomUtil.create('label', labelClass, container);
		label._layerName = obj.name;
		var checked = this._map.hasLayer(obj.layer);

		if (!obj.overlay) {
			label._minimap = this._createMinimap(
				L.DomUtil.create('div', 'leaflet-minimap', label),
				obj.layer,
				obj.overlay,
			);
		}
		var span = L.DomUtil.create('span', 'leaflet-minimap-label', label);
		var input;
		if (obj.overlay) {
			input = document.createElement('input');
			input.type = 'checkbox';
			input.className = 'leaflet-control-layers-selector';
			input.defaultChecked = checked;
		} else {
			input = this._createRadioElement('leaflet-base-layers', checked);
		}
		this._layerControlInputs.push(input);
		input.layerId = L.stamp(obj.layer);
		span.appendChild(input);

		L.DomEvent.on(label, 'click', this._onInputClick, this);

		var name = L.DomUtil.create('span', '', span);
		name.innerHTML = ' ' + obj.name;

		return label;
	},
});

customlayercontrol = function(baseLayers, overlays, options) {
	return new CustomLayerControl(baseLayers, overlays, options);
};
