// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt

finergy.provide('finergy.views.list_view');

window.cur_list = null;
finergy.views.ListFactory = class ListFactory extends finergy.views.Factory {
	make(route) {
		var me = this;
		var doctype = route[1];

		finergy.model.with_doctype(doctype, function () {
			if (locals['DocType'][doctype].issingle) {
				finergy.set_re_route('Form', doctype);
			} else {
				// List / Gantt / Kanban / etc
				let view_name = finergy.utils.to_title_case(route[2] || 'List');

				// File is a special view
				if (doctype == "File" && !["Report", "Dashboard"].includes(view_name)) {
					view_name = "File";
				}

				let view_class = finergy.views[view_name + 'View'];
				if (!view_class) view_class = finergy.views.ListView;

				if (view_class && view_class.load_last_view && view_class.load_last_view()) {
					// view can have custom routing logic
					return;
				}

				finergy.provide('finergy.views.list_view.' + doctype);
				const page_name = finergy.get_route_str();

				if (!finergy.views.list_view[page_name]) {
					finergy.views.list_view[page_name] = new view_class({
						doctype: doctype,
						parent: me.make_page(true, page_name)
					});
				} else {
					finergy.container.change_to(page_name);
				}
				me.set_cur_list();
			}
		});
	}

	show() {
		if (this.re_route_to_view()) {
			return;
		}
		this.set_module_breadcrumb();
		super.show();
		this.set_cur_list();
		cur_list && cur_list.show();
	}

	re_route_to_view() {
		var route = finergy.get_route();
		var doctype = route[1];
		var last_route = finergy.route_history.slice(-2)[0];
		if (route[0] === 'List' && route.length === 2 && finergy.views.list_view[doctype]) {
			if(last_route && last_route[0]==='List' && last_route[1]===doctype) {
				// last route same as this route, so going back.
				// this happens because /app/List/Item will redirect to /app/List/Item/List
				// while coming from back button, the last 2 routes will be same, so
				// we know user is coming in the reverse direction (via back button)

				// example:
				// Step 1: /app/List/Item redirects to /app/List/Item/List
				// Step 2: User hits "back" comes back to /app/List/Item
				// Step 3: Now we cannot send the user back to /app/List/Item/List so go back one more step
				window.history.go(-1);
				return true;
			} else {
				return false;
			}
		}
	}

	set_module_breadcrumb() {
		if (finergy.route_history.length > 1) {
			var prev_route = finergy.route_history[finergy.route_history.length - 2];
			if (prev_route[0] === 'modules') {
				var doctype = finergy.get_route()[1],
					module = prev_route[1];
				if (finergy.module_links[module] && finergy.module_links[module].includes(doctype)) {
					// save the last page from the breadcrumb was accessed
					finergy.breadcrumbs.set_doctype_module(doctype, module);
				}
			}
		}
	}

	set_cur_list() {
		var route = finergy.get_route();
		var page_name = finergy.get_route_str();
		cur_list = finergy.views.list_view[page_name];
		if (cur_list && cur_list.doctype !== route[1]) {
			// changing...
			window.cur_list = null;
		}
	}
}
