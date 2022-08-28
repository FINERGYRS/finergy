// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt

finergy.provide('finergy.views.pageview');
finergy.provide("finergy.standard_pages");

finergy.views.pageview = {
	with_page: function(name, callback) {
		if (finergy.standard_pages[name]) {
			if (!finergy.pages[name]) {
				finergy.standard_pages[name]();
			}
			callback();
			return;
		}

		if ((locals.Page && locals.Page[name] && locals.Page[name].script) || name==window.page_name) {
			// already loaded
			callback();
		} else if (localStorage["_page:" + name] && finergy.boot.developer_mode!=1) {
			// cached in local storage
			finergy.model.sync(JSON.parse(localStorage["_page:" + name]));
			callback();
		} else if (name) {
			// get fresh
			return finergy.call({
				method: 'finergy.desk.desk_page.getpage',
				args: {'name':name },
				callback: function(r) {
					if (!r.docs._dynamic_page) {
						localStorage["_page:" + name] = JSON.stringify(r.docs);
					}
					callback();
				},
				freeze: true,
			});
		}
	},

	show: function(name) {
		if (!name) {
			name = (finergy.boot ? finergy.boot.home_page : window.page_name);
		}
		finergy.model.with_doctype("Page", function() {
			finergy.views.pageview.with_page(name, function(r) {
				if (r && r.exc) {
					if (!r['403'])
						finergy.show_not_found(name);
				} else if (!finergy.pages[name]) {
					new finergy.views.Page(name);
				}
				finergy.container.change_to(name);
			});
		});
	}
};

finergy.views.Page = class Page {
	constructor(name) {
		this.name = name;
		var me = this;

		// web home page
		if (name==window.page_name) {
			this.wrapper = document.getElementById('page-' + name);
			this.wrapper.label = document.title || window.page_name;
			this.wrapper.page_name = window.page_name;
			finergy.pages[window.page_name] = this.wrapper;
		} else {
			this.pagedoc = locals.Page[this.name];
			if (!this.pagedoc) {
				finergy.show_not_found(name);
				return;
			}
			this.wrapper = finergy.container.add_page(this.name);
			this.wrapper.page_name = this.pagedoc.name;

			// set content, script and style
			if (this.pagedoc.content)
				this.wrapper.innerHTML = this.pagedoc.content;
			finergy.dom.eval(this.pagedoc.__script || this.pagedoc.script || '');
			finergy.dom.set_style(this.pagedoc.style || '');

			// set breadcrumbs
			finergy.breadcrumbs.add(this.pagedoc.module || null);
		}

		this.trigger_page_event('on_page_load');

		// set events
		$(this.wrapper).on('show', function() {
			window.cur_frm = null;
			me.trigger_page_event('on_page_show');
			me.trigger_page_event('refresh');
		});
	}

	trigger_page_event(eventname) {
		var me = this;
		if (me.wrapper[eventname]) {
			me.wrapper[eventname](me.wrapper);
		}
	}
};

finergy.show_not_found = function(page_name) {
	finergy.show_message_page({
		page_name: page_name,
		message: __("Sorry! I could not find what you were looking for."),
		img: "/assets/finergyrs/images/ui/bubble-tea-sorry.svg"
	});
};

finergy.show_not_permitted = function(page_name) {
	finergy.show_message_page({
		page_name: page_name,
		message: __("Sorry! You are not permitted to view this page."),
		img: "/assets/finergyrs/images/ui/bubble-tea-sorry.svg",
		// icon: "octicon octicon-circle-slash"
	});
};

finergy.show_message_page = function(opts) {
	// opts can include `page_name`, `message`, `icon` or `img`
	if (!opts.page_name) {
		opts.page_name = finergy.get_route_str();
	}

	if (opts.icon) {
		opts.img = repl('<span class="%(icon)s message-page-icon"></span> ', opts);
	} else if (opts.img) {
		opts.img = repl('<img src="%(img)s" class="message-page-image">', opts);
	}

	var page = finergy.pages[opts.page_name] || finergy.container.add_page(opts.page_name);
	$(page).html(
		repl('<div class="page message-page">\
			<div class="text-center message-page-content">\
				%(img)s\
				<p class="lead">%(message)s</p>\
				<a class="btn btn-default btn-sm btn-home" href="#">%(home)s</a>\
			</div>\
		</div>', {
				img: opts.img || "",
				message: opts.message || "",
				home: __("Home")
			})
	);

	finergy.container.change_to(opts.page_name);
};
