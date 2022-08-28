// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt

finergy.provide("finergy.ui.toolbar");
finergy.provide('finergy.search');

finergy.ui.toolbar.Toolbar = class {
	constructor () {
		$('header').replaceWith(finergy.render_template("navbar", {
			avatar: finergy.avatar(finergy.session.user, 'avatar-medium'),
			navbar_settings: finergy.boot.navbar_settings
		}));
		$('.dropdown-toggle').dropdown();

		this.setup_awesomebar();
		this.setup_notifications();
		this.setup_help();
		this.make();
	}

	make () {
		this.bind_events();
		$(document).trigger('toolbar_setup');
	}

	bind_events () {
		// clear all custom menus on page change
		$(document).on("page-change", function() {
			$("header .navbar .custom-menu").remove();
		});

		//focus search-modal on show in mobile view
		$('#search-modal').on('shown.bs.modal', function() {
			var search_modal = $(this);
			setTimeout(function() {
				search_modal.find('#modal-search').focus();
			}, 300);
		});
		$('.navbar-toggle-full-width').click(() => {
			finergy.ui.toolbar.toggle_full_width();
		});
	}


	setup_help () {
		if (!finergy.boot.desk_settings.notifications) {
			// hide the help section
			$('.navbar .vertical-bar').removeClass('d-sm-block');
			$('.dropdown-help').removeClass('d-lg-block');
			return;
		}
		finergy.provide('finergy.help');
		finergy.help.show_results = show_results;

		this.search = new finergy.search.SearchDialog();
		finergy.provide('finergy.searchdialog');
		finergy.searchdialog.search = this.search;

		$(".dropdown-help .dropdown-toggle").on("click", function() {
			$(".dropdown-help input").focus();
		});

		$(".dropdown-help .dropdown-menu").on("click", "input, button", function(e) {
			e.stopPropagation();
		});

		$("#input-help").on("keydown", function(e) {
			if(e.which == 13) {
				$(this).val("");
			}
		});

		$(document).on("page-change", function () {
			var $help_links = $(".dropdown-help #help-links");
			$help_links.html("");

			var route = finergy.get_route_str();
			var breadcrumbs = route.split("/");

			var links = [];
			for (var i = 0; i < breadcrumbs.length; i++) {
				var r = route.split("/", i + 1);
				var key = r.join("/");
				var help_links = finergy.help.help_links[key] || [];
				links = $.merge(links, help_links);
			}

			if(links.length === 0) {
				$help_links.next().hide();
			} else {
				$help_links.next().show();
			}

			for (var i = 0; i < links.length; i++) {
				var link = links[i];
				var url = link.url;
				$("<a>", {
					href: url,
					class: "dropdown-item",
					text: __(link.label),
					target: "_blank"
				}).appendTo($help_links);
			}

			$('.dropdown-help .dropdown-menu').on('click', 'a', show_results);
		});

		var $result_modal = finergy.get_modal("", "");
		$result_modal.addClass("help-modal");

		$(document).on("click", ".help-modal a", show_results);

		function show_results(e) {
			//edit links
			var href = e.target.href;
			if(href.indexOf('blob') > 0) {
				window.open(href, '_blank');
			}
			var path = $(e.target).attr("data-path");
			if(path) {
				e.preventDefault();
			}
		}
	}

	setup_awesomebar() {
		if (finergy.boot.desk_settings.search_bar) {
			let awesome_bar = new finergy.search.AwesomeBar();
			awesome_bar.setup("#navbar-search");

			// TODO: Remove this in v14
			finergy.search.utils.make_function_searchable(function() {
				finergy.set_route("List", "Client Script");
			}, __("Custom Script List"));

		}
	}

	setup_notifications () {
		if (finergy.boot.desk_settings.notifications && finergy.session.user !== 'Guest') {
			this.notifications = new finergy.ui.Notifications();
		}
	}

};

$.extend(finergy.ui.toolbar, {
	add_dropdown_button: function(parent, label, click, icon) {
		var menu = finergy.ui.toolbar.get_menu(parent);
		if(menu.find("li:not(.custom-menu)").length && !menu.find(".divider").length) {
			finergy.ui.toolbar.add_menu_divider(menu);
		}

		return $('<li class="custom-menu"><a><i class="fa-fw '
			+icon+'"></i> '+label+'</a></li>')
			.insertBefore(menu.find(".divider"))
			.find("a")
			.click(function() {
				click.apply(this);
			});
	},
	get_menu: function(label) {
		return $("#navbar-" + label.toLowerCase());
	},
	add_menu_divider: function(menu) {
		menu = typeof menu == "string" ?
			finergy.ui.toolbar.get_menu(menu) : menu;

		$('<li class="divider custom-menu"></li>').prependTo(menu);
	},
	add_icon_link(route, icon, index, class_name) {
		let parent_element = $(".navbar-right").get(0);
		let new_element = $(`<li class="${class_name}">
			<a class="btn" href="${route}" title="${finergy.utils.to_title_case(class_name, true)}" aria-haspopup="true" aria-expanded="true">
				<div>
					<i class="octicon ${icon}"></i>
				</div>
			</a>
		</li>`).get(0);

		parent_element.insertBefore(new_element, parent_element.children[index]);
	},
	toggle_full_width() {
		let fullwidth = JSON.parse(localStorage.container_fullwidth || 'false');
		fullwidth = !fullwidth;
		localStorage.container_fullwidth = fullwidth;
		finergy.ui.toolbar.set_fullwidth_if_enabled();
		$(document.body).trigger('toggleFullWidth');
	},
	set_fullwidth_if_enabled() {
		let fullwidth = JSON.parse(localStorage.container_fullwidth || 'false');
		$(document.body).toggleClass('full-width', fullwidth);
	},
	show_shortcuts (e) {
		e.preventDefault();
		finergy.ui.keys.show_keyboard_shortcut_dialog();
		return false;
	},
});

finergy.ui.toolbar.clear_cache = finergy.utils.throttle(function() {
	finergy.assets.clear_local_storage();
	finergy.xcall('finergy.sessions.clear').then(message => {
		finergy.show_alert({
			message: message,
			indicator: 'info'
		});
		location.reload(true);
	});
}, 10000);

finergy.ui.toolbar.show_about = function() {
	try {
		finergy.ui.misc.about();
	} catch(e) {
		console.log(e);
	}
	return false;
};

finergy.ui.toolbar.route_to_user = function() {
	finergy.set_route('Form', 'User', finergy.session.user);
};

finergy.ui.toolbar.view_website = function() {
	let website_tab = window.open();
	website_tab.opener = null;
	website_tab.location = '/index';
};

finergy.ui.toolbar.setup_session_defaults = function() {
	let fields = [];
	finergy.call({
		method: 'finergy.core.doctype.session_default_settings.session_default_settings.get_session_default_values',
		callback: function (data) {
			fields = JSON.parse(data.message);
			let perms = finergy.perm.get_perm('Session Default Settings');
			//add settings button only if user is a System Manager or has permission on 'Session Default Settings'
			if ((in_list(finergy.user_roles, 'System Manager')) || (perms[0].read == 1))  {
				fields[fields.length] = {
					'fieldname': 'settings',
					'fieldtype': 'Button',
					'label': __('Settings'),
					'click': () => {
						finergy.set_route('Form', 'Session Default Settings', 'Session Default Settings');
					}
				};
			}
			finergy.prompt(fields, function(values) {
				//if default is not set for a particular field in prompt
				fields.forEach(function(d) {
					if (!values[d.fieldname]) {
						values[d.fieldname] = "";
					}
				});
				finergy.call({
					method: 'finergy.core.doctype.session_default_settings.session_default_settings.set_session_default_values',
					args: {
						default_values: values,
					},
					callback: function(data) {
						if (data.message == "success") {
							finergy.show_alert({
								'message': __('Session Defaults Saved'),
								'indicator': 'green'
							});
							finergy.ui.toolbar.clear_cache();
						}	else {
							finergy.show_alert({
								'message': __('An error occurred while setting Session Defaults'),
								'indicator': 'red'
							});
						}
					}
				});
			},
			__('Session Defaults'),
			__('Save'),
			);
		}
	});
};