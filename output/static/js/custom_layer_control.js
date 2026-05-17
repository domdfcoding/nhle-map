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
	initialize(baseLayers, overlays, options) {
		L.Control.Layers.MinimapToggle.prototype.initialize.call(this, baseLayers, overlays, options);
		this._toggleAllButtons = new ToggleAllButtons(this);
	},

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

	_update: function() {
		L.Control.Layers.MinimapToggle.prototype._update.call(this);

		var div = L.DomUtil.create('div', 'leaflet-lc-overlay-container', this._overlaysList);
		var span = L.DomUtil.create('span', 'leaflet-all-layers-buttons pt-1', div);
		// TODO: Show All triggers the double loading bar
		// TODO: tri-state checkbox
		// this._toggleAllButtons.createButton(span, 'Show All', (e) => {
		// 	console.log('Show all overlays');
		// 	this._toggleAllButtons.showAll();
		// 	e.preventDefault();
		// 	e.stopPropagation();
		// });
		this._toggleAllButtons.createButton(span, 'Show None', (e) => {
			console.log('Hide all overlays');
			this._toggleAllButtons.showNone();
			e.preventDefault();
			e.stopPropagation();
		});
	},
});

// TODO: better path for markerGroups; need to batch the addLayers call again to avoid multiple progress bars (which for some reason don't have the blurred background)
class ToggleAllButtons {
	constructor(layerControl) {
		this._layerControl = layerControl;
	}

	createButton(parent, label, callback) {
		var input = L.DomUtil.create(
			'input',
			'leaflet-control-layers-selector btn btn-outline-secondary px-2 py-0 me-1 mt-0 rounded-0',
			parent,
		);
		input.type = 'button';
		input.value = label;
		input.addEventListener('click', callback);
	}

	showAll() {
		const lc = this._layerControl;
		for (var i in lc._layers) {
			if (lc._layers[i].overlay) {
				if (!lc._map.hasLayer(lc._layers[i].layer)) {
					lc._map.addLayer(lc._layers[i].layer);
				}
			}
		}
	}
	showNone() {
		const lc = this._layerControl;
		for (var i in lc._layers) {
			if (lc._layers[i].overlay) {
				if (lc._map.hasLayer(lc._layers[i].layer)) {
					lc._map.removeLayer(lc._layers[i].layer);
				}
			}
		}
	}
}

customlayercontrol = function(baseLayers, overlays, options) {
	return new CustomLayerControl(baseLayers, overlays, options);
};
