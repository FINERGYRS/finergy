// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt

// route urls to their virtual pages

// re-route map (for rename)
finergy.provide('finergy.views');
finergy.re_route = {"#login": ""};
finergy.route_titles = {};
finergy.route_flags = {};
finergy.route_history = [];
finergy.view_factory = {};
finergy.view_factories = [];
finergy.route_options = null;
finergy.route_hooks = {};

$(window).on('hashchange', function(e) {
	// v1 style routing, route is in hash
	if (window.location.hash && !finergy.router.is_app_route(e.currentTarget.pathname)) {
		let sub_path = finergy.router.get_sub_path(window.location.hash);
		finergy.router.push_state(sub_path);
		return false;
	}
});

window.addEventListener('popstate', (e) => {
	// forward-back button, just re-render based on current route
	finergy.router.route();
	e.preventDefault();
	return false;
});

// routing v2, capture all clicks so that the target is managed with push-state
$('body').on('click', 'a', function(e) {
	let override = (route) => {
		e.preventDefault();
		finergy.set_route(route);
		return false;
	};

	const href = e.currentTarget.getAttribute('href');

	// click handled, but not by href
	if (e.currentTarget.getAttribute('onclick') // has a handler
		|| (e.ctrlKey || e.metaKey) // open in a new tab
		|| href==='#') { // hash is home
		return;
	}

	if (href === '') {
		return override('/app');
	}

	if (href && href.startsWith('#')) {
		// target startswith "#", this is a v1 style route, so remake it.
		return override(e.currentTarget.hash);
	}

	if (finergy.router.is_app_route(e.currentTarget.pathname)) {
		// target has "/app, this is a v2 style route.
		return override(e.currentTarget.pathname + e.currentTarget.hash);
	}

});

finergy.router = {
	current_route: null,
	routes: {},
	factory_views: ['form', 'list', 'report', 'tree', 'print', 'dashboard'],
	list_views: ['list', 'kanban', 'report', 'calendar', 'tree', 'gantt', 'dashboard', 'image', 'inbox'],
	layout_mapped: {},

	is_app_route(path) {
		// desk paths must begin with /app or doctype route
		if (path.substr(0, 1) === '/') path = path.substr(1);
		path = path.split('/');
		if (path[0]) {
			return path[0]==='app';
		}
	},

	setup() {
		// setup the route names by forming slugs of the given doctypes
		for (let doctype of finergy.boot.user.can_read) {
			this.routes[this.slug(doctype)] = {doctype: doctype};
		}
		if (finergy.boot.doctype_layouts) {
			for (let doctype_layout of finergy.boot.doctype_layouts) {
				this.routes[this.slug(doctype_layout.name)] = {doctype: doctype_layout.document_type, doctype_layout: doctype_layout.name };
			}
		}
	},

	route() {
		// resolve the route from the URL or hash
		// translate it so the objects are well defined
		// and render the page as required

		if (!finergy.app) return;

		let sub_path = this.get_sub_path();
		if (this.re_route(sub_path)) return;

		this.current_sub_path = sub_path;
		this.current_route = this.parse();
		this.set_history(sub_path);
		this.render();
		this.set_title(sub_path);
		this.trigger('change');
	},

	parse(route) {
		route = this.get_sub_path_string(route).split('/');
		if (!route) return [];
		route = $.map(route, this.decode_component);
		this.set_route_options_from_url(route);
		return this.convert_to_standard_route(route);
	},

	convert_to_standard_route(route) {
		// /app/settings = ["Workspaces", "Settings"]
		// /app/user = ["List", "User"]
		// /app/user/view/report = ["List", "User", "Report"]
		// /app/user/view/tree = ["Tree", "User"]
		// /app/user/user-001 = ["Form", "User", "user-001"]
		// /app/user/user-001 = ["Form", "User", "user-001"]
		// /app/event/view/calendar/default = ["List", "Event", "Calendar", "Default"]

		if (finergy.workspaces[route[0]]) {
			// workspace
			route = ['Workspaces', finergy.workspaces[route[0]].name];
		} else if (this.routes[route[0]]) {
			// route
			route = this.set_doctype_route(route);
		}

		return route;
	},

	set_doctype_route(route) {
		let doctype_route = this.routes[route[0]];
		// doctype route
		if (route[1]) {
			if (route[2] && route[1]==='view') {
				route = this.get_standard_route_for_list(route, doctype_route);
			} else {
				let docname = route[1];
				if (route.length > 2) {
					docname = route.slice(1).join('/');
				}
				route = ['Form', doctype_route.doctype, docname];
			}
		} else if (finergy.model.is_single(doctype_route.doctype)) {
			route = ['Form', doctype_route.doctype, doctype_route.doctype];
		} else {
			route = ['List', doctype_route.doctype, 'List'];
		}

		if (doctype_route.doctype_layout) {
			// set the layout
			this.doctype_layout = doctype_route.doctype_layout;
		}

		return route;
	},

	get_standard_route_for_list(route, doctype_route) {
		let standard_route;
		if (route[2].toLowerCase()==='tree') {
			standard_route = ['Tree', doctype_route.doctype];
		} else {
			standard_route = ['List', doctype_route.doctype, finergy.utils.to_title_case(route[2])];
			// calendar / kanban / dashboard / folder
			if (route[3]) standard_route.push(...route.slice(3, route.length));
		}
		return standard_route;
	},

	set_history() {
		finergy.route_history.push(this.current_route);
		finergy.ui.hide_open_dialog();
	},

	render() {
		if (this.current_route[0]) {
			this.render_page();
		} else {
			// Show home
			finergy.views.pageview.show('');
		}
	},

	render_page() {
		// create the page generator (factory) object and call `show`
		// if there is no generator, render the `Page` object

		const route = this.current_route;
		const factory = finergy.utils.to_title_case(route[0]);

		if (route[1] && finergy.views[factory + "Factory"]) {
			route[0] = factory;
			// has a view generator, generate!
			if (!finergy.view_factory[factory]) {
				finergy.view_factory[factory] = new finergy.views[factory + "Factory"]();
			}

			finergy.view_factory[factory].show();
		} else {
			// show page
			const route_name = finergy.utils.xss_sanitise(route[0]);
			if (finergy.views.pageview) {
				finergy.views.pageview.show(route_name);
			}
		}
	},

	re_route(sub_path) {
		if (finergy.re_route[sub_path] !== undefined) {
			// after saving a doc, for example,
			// "new-doctype-1" and the renamed "TestDocType", both exist in history
			// now if we try to go back,
			// it doesn't allow us to go back to the one prior to "new-doctype-1"
			// Hence if this check is true, instead of changing location hash,
			// we just do a back to go to the doc previous to the "new-doctype-1"
			const re_route_val = this.get_sub_path(finergy.re_route[sub_path]);
			if (re_route_val === this.current_sub_path) {
				window.history.back();
			} else {
				finergy.set_route(re_route_val);
			}

			return true;
		}
	},

	set_title(sub_path) {
		if (finergy.route_titles[sub_path]) {
			finergy.utils.set_title(finergy.route_titles[sub_path]);
		}
	},

	set_route() {
		// set the route (push state) with given arguments
		// example 1: finergy.set_route('a', 'b', 'c');
		// example 2: finergy.set_route(['a', 'b', 'c']);
		// example 3: finergy.set_route('a/b/c');
		let route = Array.from(arguments);

		return new Promise(resolve => {
			route = this.get_route_from_arguments(route);
			route = this.convert_from_standard_route(route);
			let sub_path = this.make_url(route);
			// replace each # occurrences in the URL with encoded character except for last
			// sub_path = sub_path.replace(/[#](?=.*[#])/g, "%23");
			this.push_state(sub_path);

			setTimeout(() => {
				finergy.after_ajax && finergy.after_ajax(() => {
					resolve();
				});
			}, 100);
		}).finally(() => finergy.route_flags = {});
	},

	get_route_from_arguments(route) {
		if (route.length===1 && $.isArray(route[0])) {
			// called as finergy.set_route(['a', 'b', 'c']);
			route = route[0];
		}

		if (route.length===1 && route[0] && route[0].includes('/')) {
			// called as finergy.set_route('a/b/c')
			route = $.map(route[0].split('/'), this.decode_component);
		}

		if (route && route[0] == '') {
			route.shift();
		}

		if (route && ['desk', 'app'].includes(route[0])) {
			// we only need subpath, remove "app" (or "desk")
			route.shift();
		}

		return route;

	},

	convert_from_standard_route(route) {
		// ["List", "Sales Order"] => /sales-order
		// ["Form", "Sales Order", "SO-0001"] => /sales-order/SO-0001
		// ["Tree", "Account"] = /account/view/tree

		const view = route[0] ? route[0].toLowerCase() : '';
		let new_route = route;
		if (view === 'list') {
			if (route[2] && route[2] !== 'list' && !$.isPlainObject(route[2])) {
				new_route = [this.slug(route[1]), 'view', route[2].toLowerCase()];

				// calendar / inbox / file folder
				if (route[3]) new_route.push(...route.slice(3, route.length));
			} else {
				if ($.isPlainObject(route[2])) {
					finergy.route_options = route[2];
				}
				new_route = [this.slug(route[1])];
			}
		} else if (view === 'form') {
			new_route = [this.slug(route[1])];
			if (route[2]) {
				// if not single
				new_route.push(route[2]);
			}
		} else if (view === 'tree') {
			new_route = [this.slug(route[1]), 'view', 'tree'];
		}
		return new_route;
	},

	slug_parts(route) {
		// slug doctype

		// if app is part of the route, then first 2 elements are "" and "app"
		if (route[0] && this.factory_views.includes(route[0].toLowerCase())) {
			route[0] = route[0].toLowerCase();
			route[1] = this.slug(route[1]);
		}
		return route;
	},

	make_url(params) {
		let path_string = $.map(params, function(a) {
			if ($.isPlainObject(a)) {
				finergy.route_options = a;
				return null;
			} else {
				a = encodeURIComponent(String(a));
				return a;
			}
		}).join('/');

		return '/app/' + (path_string || 'home');
	},

	push_state(url) {
		// change the URL and call the router
		if (window.location.pathname !== url) {

			// push/replace state so the browser looks fine
			const method = finergy.route_flags.replace_route ? "replaceState" : "pushState";
			history[method](null, null, url);

			// now process the route
			this.route();
		}
	},

	get_sub_path_string(route) {
		// return clean sub_path from hash or url
		// supports both v1 and v2 routing
		if (!route) {
			route = window.location.pathname;
			if (route.includes('app#')) {
				// to support v1
				route = window.location.hash;
			}
		}

		return this.strip_prefix(route);
	},

	strip_prefix(route) {
		if (route.substr(0, 1)=='/') route = route.substr(1); // for /app/sub
		if (route.startsWith('app/')) route = route.substr(4); // for desk/sub
		if (route == 'app') route = route.substr(4); // for /app
		if (route.substr(0, 1)=='/') route = route.substr(1);
		if (route.substr(0, 1)=='#') route = route.substr(1);
		if (route.substr(0, 1)=='!') route = route.substr(1);
		return route;
	},

	get_sub_path(route) {
		var sub_path = this.get_sub_path_string(route);
		route = $.map(sub_path.split('/'), this.decode_component).join('/');

		return route;
	},

	set_route_options_from_url(route) {
		// set query parameters as finergy.route_options
		var last_part = route[route.length - 1];
		if (last_part.indexOf("?") < last_part.indexOf("=")) {
			// has ? followed by =
			let parts = last_part.split("?");

			// route should not contain string after ?
			route[route.length - 1] = parts[0];

			let query_params = finergy.utils.get_query_params(parts[1]);
			finergy.route_options = $.extend(finergy.route_options || {}, query_params);
		}
	},

	decode_component(r) {
		try {
			return decodeURIComponent(r);
		} catch (e) {
			if (e instanceof URIError) {
				// legacy: not sure why URIError is ignored.
				return r;
			} else {
				throw e;
			}
		}
	},

	slug(name) {
		return name.toLowerCase().replace(/ /g, '-');
	}
};

// global functions for backward compatibility
finergy.get_route = () => finergy.router.current_route;
finergy.get_route_str = () => finergy.router.current_route.join('/');
finergy.set_route = function() {
	return finergy.router.set_route.apply(finergy.router, arguments);
};

finergy.get_prev_route = function() {
	if (finergy.route_history && finergy.route_history.length > 1) {
		return finergy.route_history[finergy.route_history.length - 2];
	} else {
		return [];
	}
};

finergy.set_re_route = function() {
	var tmp = finergy.router.get_sub_path();
	finergy.set_route.apply(null, arguments);
	finergy.re_route[tmp] = finergy.router.get_sub_path();
};

finergy.has_route_options = function() {
	return Boolean(Object.keys(finergy.route_options || {}).length);
};

finergy.utils.make_event_emitter(finergy.router);
