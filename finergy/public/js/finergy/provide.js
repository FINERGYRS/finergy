// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt

// provide a namespace
if(!window.finergy)
	window.finergy = {};

finergy.provide = function(namespace) {
	// docs: create a namespace //
	var nsl = namespace.split('.');
	var parent = window;
	for(var i=0; i<nsl.length; i++) {
		var n = nsl[i];
		if(!parent[n]) {
			parent[n] = {}
		}
		parent = parent[n];
	}
	return parent;
}

finergy.provide("locals");
finergy.provide("finergy.flags");
finergy.provide("finergy.settings");
finergy.provide("finergy.utils");
finergy.provide("finergy.ui.form");
finergy.provide("finergy.modules");
finergy.provide("finergy.templates");
finergy.provide("finergy.test_data");
finergy.provide('finergy.utils');
finergy.provide('finergy.model');
finergy.provide('finergy.user');
finergy.provide('finergy.session');
finergy.provide("finergy._messages");
finergy.provide('locals.DocType');

// for listviews
finergy.provide("finergy.listview_settings");
finergy.provide("finergy.tour");
finergy.provide("finergy.listview_parent_route");

// constants
window.NEWLINE = '\n';
window.TAB = 9;
window.UP_ARROW = 38;
window.DOWN_ARROW = 40;

// proxy for user globals defined in desk.js

// API globals
window.cur_frm=null;
