// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt

finergy.provide('finergy.pages');
finergy.provide('finergy.views');

finergy.views.Factory = class Factory {
	constructor(opts) {
		$.extend(this, opts);
	}

	show() {
		var page_name = finergy.get_route_str(),
			me = this;

		if (finergy.pages[page_name]) {
			finergy.container.change_to(page_name);
			if(me.on_show) {
				me.on_show();
			}
		} else {
			var route = finergy.get_route();
			if(route[1]) {
				me.make(route);
			} else {
				finergy.show_not_found(route);
			}
		}
	}

	make_page(double_column, page_name) {
		return finergy.make_page(double_column, page_name);
	}
}

finergy.make_page = function(double_column, page_name) {
	if(!page_name) {
		var page_name = finergy.get_route_str();
	}
	var page = finergy.container.add_page(page_name);

	finergy.ui.make_app_page({
		parent: page,
		single_column: !double_column
	});
	finergy.container.change_to(page_name);
	return page;
}
