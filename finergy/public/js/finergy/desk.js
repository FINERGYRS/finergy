// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt
/* eslint-disable no-console */

// __('Modules') __('Domains') __('Places') __('Administration') # for translation, don't remove

finergy.start_app = function() {
	if (!finergy.Application)
		return;
	finergy.assets.check();
	finergy.provide('finergy.app');
	finergy.provide('finergy.desk');
	finergy.app = new finergy.Application();
};

$(document).ready(function() {
	if (!finergy.utils.supportsES6) {
		finergy.msgprint({
			indicator: 'red',
			title: __('Browser not supported'),
			message: __('Some of the features might not work in your browser. Please update your browser to the latest version.')
		});
	}
	finergy.start_app();
});

finergy.Application = Class.extend({
	init: function() {
		this.startup();
	},

	startup: function() {
		finergy.socketio.init();
		finergy.model.init();

		if(finergy.boot.status==='failed') {
			finergy.msgprint({
				message: finergy.boot.error,
				title: __('Session Start Failed'),
				indicator: 'red',
			});
			throw 'boot failed';
		}

		this.setup_finergy_vue();
		this.load_bootinfo();
		this.load_user_permissions();
		this.make_nav_bar();
		this.set_favicon();
		this.setup_analytics();
		this.set_fullwidth_if_enabled();
		this.add_browser_class();
		this.setup_energy_point_listeners();
		this.setup_copy_doc_listener();

		finergy.ui.keys.setup();

		finergy.ui.keys.add_shortcut({
			shortcut: 'shift+ctrl+g',
			description: __('Switch Theme'),
			action: () => {
				finergy.theme_switcher = new finergy.ui.ThemeSwitcher();
				finergy.theme_switcher.show();
			}
		});

		// page container
		this.make_page_container();
		this.set_route();

		// trigger app startup
		$(document).trigger('startup');

		$(document).trigger('app_ready');

		if (finergy.boot.messages) {
			finergy.msgprint(finergy.boot.messages);
		}

		if (finergy.user_roles.includes('System Manager')) {
			// delayed following requests to make boot faster
			setTimeout(() => {
				this.show_change_log();
				this.show_update_available();
			}, 1000);
		}

		if (!finergy.boot.developer_mode) {
			let console_security_message = __("Using this console may allow attackers to impersonate you and steal your information. Do not enter or paste code that you do not understand.");
			console.log(
				`%c${console_security_message}`,
				"font-size: large"
			);
		}

		this.show_notes();

		if (finergy.ui.startup_setup_dialog && !finergy.boot.setup_complete) {
			finergy.ui.startup_setup_dialog.pre_show();
			finergy.ui.startup_setup_dialog.show();
		}

		finergy.realtime.on("version-update", function() {
			var dialog = finergy.msgprint({
				message:__("The application has been updated to a new version, please refresh this page"),
				indicator: 'green',
				title: __('Version Updated')
			});
			dialog.set_primary_action(__("Refresh"), function() {
				location.reload(true);
			});
			dialog.get_close_btn().toggle(false);
		});

		// listen to build errors
		this.setup_build_error_listener();

		if (finergy.sys_defaults.email_user_password) {
			var email_list =  finergy.sys_defaults.email_user_password.split(',');
			for (var u in email_list) {
				if (email_list[u]===finergy.user.name) {
					this.set_password(email_list[u]);
				}
			}
		}

		// REDESIGN-TODO: Fix preview popovers
		this.link_preview = new finergy.ui.LinkPreview();

		if (!finergy.boot.developer_mode) {
			setInterval(function() {
				finergy.call({
					method: 'finergy.core.page.background_jobs.background_jobs.get_scheduler_status',
					callback: function(r) {
						if (r.message[0] == __("Inactive")) {
							finergy.call('finergy.utils.scheduler.activate_scheduler');
						}
					}
				});
			}, 300000); // check every 5 minutes

			if (finergy.user.has_role("System Manager")) {
				setInterval(function() {
					finergy.call({
						method: 'finergy.core.doctype.log_settings.log_settings.has_unseen_error_log',
						args: {
							user: finergy.session.user
						},
						callback: function(r) {
							if (r.message.show_alert) {
								finergy.show_alert({
									indicator: 'red',
									message: r.message.message
								});
							}
						}
					});
				}, 600000); // check every 10 minutes
			}
		}
	},

	set_route() {
		finergy.flags.setting_original_route = true;
		if (finergy.boot && localStorage.getItem("session_last_route")) {
			finergy.set_route(localStorage.getItem("session_last_route"));
			localStorage.removeItem("session_last_route");
		} else {
			// route to home page
			finergy.router.route();
		}
		finergy.after_ajax(() => finergy.flags.setting_original_route = false);
		finergy.router.on('change', () => {
			$(".tooltip").hide();
		});
	},

	setup_finergy_vue() {
		Vue.prototype.__ = window.__;
		Vue.prototype.finergy = window.finergy;
	},

	set_password: function(user) {
		var me=this;
		finergy.call({
			method: 'finergy.core.doctype.user.user.get_email_awaiting',
			args: {
				"user": user
			},
			callback: function(email_account) {
				email_account = email_account["message"];
				if (email_account) {
					var i = 0;
					if (i < email_account.length) {
						me.email_password_prompt( email_account, user, i);
					}
				}
			}
		});
	},

	email_password_prompt: function(email_account,user,i) {
		var me = this;
		const email_id = email_account[i]["email_id"];
		let d = new finergy.ui.Dialog({
			title: __('Password missing in Email Account'),
			fields: [
				{
					'fieldname': 'password',
					'fieldtype': 'Password',
					'label': __('Please enter the password for: <b>{0}</b>', [email_id], "Email Account"),
					'reqd': 1
				},
				{
					"fieldname": "submit",
					"fieldtype": "Button",
					"label": __("Submit", null, "Submit password for Email Account")
				}
			]
		});
		d.get_input("submit").on("click", function() {
			//setup spinner
			d.hide();
			var s = new finergy.ui.Dialog({
				title: __("Checking one moment"),
				fields: [{
					"fieldtype": "HTML",
					"fieldname": "checking"
				}]
			});
			s.fields_dict.checking.$wrapper.html('<i class="fa fa-spinner fa-spin fa-4x"></i>');
			s.show();
			finergy.call({
				method: 'finergy.email.doctype.email_account.email_account.set_email_password',
				args: {
					"email_account": email_account[i]["email_account"],
					"user": user,
					"password": d.get_value("password")
				},
				callback: function(passed) {
					s.hide();
					d.hide();//hide waiting indication
					if (!passed["message"]) {
						finergy.show_alert({message: __("Login Failed please try again"), indicator: 'error'}, 5);
						me.email_password_prompt(email_account, user, i);
					} else {
						if (i + 1 < email_account.length) {
							i = i + 1;
							me.email_password_prompt(email_account, user, i);
						}
					}

				}
			});
		});
		d.show();
	},
	load_bootinfo: function() {
		if(finergy.boot) {
			this.setup_workspaces();
			finergy.model.sync(finergy.boot.docs);
			this.check_metadata_cache_status();
			this.set_globals();
			this.sync_pages();
			finergy.router.setup();
			this.setup_moment();
			if(finergy.boot.print_css) {
				finergy.dom.set_style(finergy.boot.print_css, "print-style");
			}
			finergy.user.name = finergy.boot.user.name;
			finergy.router.setup();
		} else {
			this.set_as_guest();
		}
	},

	setup_workspaces() {
		finergy.modules = {};
		finergy.workspaces = {};
		for (let page of finergy.boot.allowed_workspaces || []) {
			finergy.modules[page.module]=page;
			finergy.workspaces[finergy.router.slug(page.name)] = page;
		}
		if (!finergy.workspaces['home']) {
			// default workspace is settings for Finergy
			finergy.workspaces['home'] = finergy.workspaces[Object.keys(finergy.workspaces)[0]];
		}
	},

	load_user_permissions: function() {
		finergy.defaults.update_user_permissions();

		finergy.realtime.on('update_user_permissions', finergy.utils.debounce(() => {
			finergy.defaults.update_user_permissions();
		}, 500));
	},

	check_metadata_cache_status: function() {
		if(finergy.boot.metadata_version != localStorage.metadata_version) {
			finergy.assets.clear_local_storage();
			finergy.assets.init_local_storage();
		}
	},

	set_globals: function() {
		finergy.session.user = finergy.boot.user.name;
		finergy.session.logged_in_user = finergy.boot.user.name;
		finergy.session.user_email = finergy.boot.user.email;
		finergy.session.user_fullname = finergy.user_info().fullname;

		finergy.user_defaults = finergy.boot.user.defaults;
		finergy.user_roles = finergy.boot.user.roles;
		finergy.sys_defaults = finergy.boot.sysdefaults;

		finergy.ui.py_date_format = finergy.boot.sysdefaults.date_format.replace('dd', '%d').replace('mm', '%m').replace('yyyy', '%Y');
		finergy.boot.user.last_selected_values = {};

		// Proxy for user globals
		Object.defineProperties(window, {
			'user': {
				get: function() {
					console.warn('Please use `finergy.session.user` instead of `user`. It will be deprecated soon.');
					return finergy.session.user;
				}
			},
			'user_fullname': {
				get: function() {
					console.warn('Please use `finergy.session.user_fullname` instead of `user_fullname`. It will be deprecated soon.');
					return finergy.session.user;
				}
			},
			'user_email': {
				get: function() {
					console.warn('Please use `finergy.session.user_email` instead of `user_email`. It will be deprecated soon.');
					return finergy.session.user_email;
				}
			},
			'user_defaults': {
				get: function() {
					console.warn('Please use `finergy.user_defaults` instead of `user_defaults`. It will be deprecated soon.');
					return finergy.user_defaults;
				}
			},
			'roles': {
				get: function() {
					console.warn('Please use `finergy.user_roles` instead of `roles`. It will be deprecated soon.');
					return finergy.user_roles;
				}
			},
			'sys_defaults': {
				get: function() {
					console.warn('Please use `finergy.sys_defaults` instead of `sys_defaults`. It will be deprecated soon.');
					return finergy.user_roles;
				}
			}
		});
	},
	sync_pages: function() {
		// clear cached pages if timestamp is not found
		if(localStorage["page_info"]) {
			finergy.boot.allowed_pages = [];
			var page_info = JSON.parse(localStorage["page_info"]);
			$.each(finergy.boot.page_info, function(name, p) {
				if(!page_info[name] || (page_info[name].modified != p.modified)) {
					delete localStorage["_page:" + name];
				}
				finergy.boot.allowed_pages.push(name);
			});
		} else {
			finergy.boot.allowed_pages = Object.keys(finergy.boot.page_info);
		}
		localStorage["page_info"] = JSON.stringify(finergy.boot.page_info);
	},
	set_as_guest: function() {
		finergy.session.user = 'Guest';
		finergy.session.user_email = '';
		finergy.session.user_fullname = 'Guest';

		finergy.user_defaults = {};
		finergy.user_roles = ['Guest'];
		finergy.sys_defaults = {};
	},
	make_page_container: function() {
		if ($("#body").length) {
			$(".splash").remove();
			finergy.temp_container = $("<div id='temp-container' style='display: none;'>")
				.appendTo("body");
			finergy.container = new finergy.views.Container();
		}
	},
	make_nav_bar: function() {
		// toolbar
		if(finergy.boot && finergy.boot.home_page!=='setup-wizard') {
			finergy.finergy_toolbar = new finergy.ui.toolbar.Toolbar();
		}

	},
	logout: function() {
		var me = this;
		me.logged_out = true;
		return finergy.call({
			method:'logout',
			callback: function(r) {
				if(r.exc) {
					return;
				}
				me.redirect_to_login();
			}
		});
	},
	handle_session_expired: function() {
		if(!finergy.app.session_expired_dialog) {
			var dialog = new finergy.ui.Dialog({
				title: __('Session Expired'),
				keep_open: true,
				fields: [
					{ fieldtype:'Password', fieldname:'password',
						label: __('Please Enter Your Password to Continue') },
				],
				onhide: () => {
					if (!dialog.logged_in) {
						finergy.app.redirect_to_login();
					}
				}
			});
			dialog.set_primary_action(__('Login'), () => {
				dialog.set_message(__('Authenticating...'));
				finergy.call({
					method: 'login',
					args: {
						usr: finergy.session.user,
						pwd: dialog.get_values().password
					},
					callback: (r) => {
						if (r.message==='Logged In') {
							dialog.logged_in = true;

							// revert backdrop
							$('.modal-backdrop').css({
								'opacity': '',
								'background-color': '#334143'
							});
						}
						dialog.hide();
					},
					statusCode: () => {
						dialog.hide();
					}
				});
			});
			finergy.app.session_expired_dialog = dialog;
		}
		if(!finergy.app.session_expired_dialog.display) {
			finergy.app.session_expired_dialog.show();
			// add backdrop
			$('.modal-backdrop').css({
				'opacity': 1,
				'background-color': '#4B4C9D'
			});
		}
	},
	redirect_to_login: function() {
		window.location.href = '/';
	},
	set_favicon: function() {
		var link = $('link[type="image/x-icon"]').remove().attr("href");
		$('<link rel="shortcut icon" href="' + link + '" type="image/x-icon">').appendTo("head");
		$('<link rel="icon" href="' + link + '" type="image/x-icon">').appendTo("head");
	},
	trigger_primary_action: function() {
		// to trigger change event on active input before triggering primary action
		$(document.activeElement).blur();
		// wait for possible JS validations triggered after blur (it might change primary button)
		setTimeout(() => {
			if (window.cur_dialog && cur_dialog.display) {
				// trigger primary
				cur_dialog.get_primary_btn().trigger("click");
			} else if (cur_frm && cur_frm.page.btn_primary.is(':visible')) {
				cur_frm.page.btn_primary.trigger('click');
			} else if (finergy.container.page.save_action) {
				finergy.container.page.save_action();
			}
		}, 100);
	},

	show_change_log: function() {
		var me = this;
		let change_log = finergy.boot.change_log;

		// finergy.boot.change_log = [{
		// 	"change_log": [
		// 		[<version>, <change_log in markdown>],
		// 		[<version>, <change_log in markdown>],
		// 	],
		// 	"description": "ERP made simple",
		// 	"title": "CapKPI",
		// 	"version": "12.2.0"
		// }];

		if (!Array.isArray(change_log) || !change_log.length ||
			window.Cypress || cint(finergy.boot.sysdefaults.disable_change_log_notification)) {
			return;
		}

		// Iterate over changelog
		var change_log_dialog = finergy.msgprint({
			message: finergy.render_template("change_log", {"change_log": change_log}),
			title: __("Updated To A New Version 🎉"),
			wide: true,
		});
		change_log_dialog.keep_open = true;
		change_log_dialog.custom_onhide = function() {
			finergy.call({
				"method": "finergy.utils.change_log.update_last_known_versions"
			});
			me.show_notes();
		};
	},

	show_update_available: () => {
		if (finergy.boot.sysdefaults.disable_system_update_notification) return;

		finergy.call({
			"method": "finergy.utils.change_log.show_update_popup"
		});
	},

	setup_analytics: function() {
		if(window.mixpanel) {
			window.mixpanel.identify(finergy.session.user);
			window.mixpanel.people.set({
				"$first_name": finergy.boot.user.first_name,
				"$last_name": finergy.boot.user.last_name,
				"$created": finergy.boot.user.creation,
				"$email": finergy.session.user
			});
		}
	},

	add_browser_class() {
		$('html').addClass(finergy.utils.get_browser().name.toLowerCase());
	},

	set_fullwidth_if_enabled() {
		finergy.ui.toolbar.set_fullwidth_if_enabled();
	},

	show_notes: function() {
		var me = this;
		if(finergy.boot.notes.length) {
			finergy.boot.notes.forEach(function(note) {
				if(!note.seen || note.notify_on_every_login) {
					var d = finergy.msgprint({message:note.content, title:note.title});
					d.keep_open = true;
					d.custom_onhide = function() {
						note.seen = true;

						// Mark note as read if the Notify On Every Login flag is not set
						if (!note.notify_on_every_login) {
							finergy.call({
								method: "finergy.desk.doctype.note.note.mark_as_seen",
								args: {
									note: note.name
								}
							});
						}

						// next note
						me.show_notes();

					};
				}
			});
		}
	},

	setup_build_error_listener() {
		if (finergy.boot.developer_mode) {
			finergy.realtime.on('build_error', (data) => {
				console.log(data);
			});
		}
	},

	setup_energy_point_listeners() {
		finergy.realtime.on('energy_point_alert', (message) => {
			finergy.show_alert(message);
		});
	},

	setup_copy_doc_listener() {
		$('body').on('paste', (e) => {
			try {
				let pasted_data = finergy.utils.get_clipboard_data(e);
				let doc = JSON.parse(pasted_data);
				if (doc.doctype) {
					e.preventDefault();
					let sleep = (time) => {
						return new Promise((resolve) => setTimeout(resolve, time));
					};

					finergy.dom.freeze(__('Creating {0}', [doc.doctype]) + '...');
					// to avoid abrupt UX
					// wait for activity feedback
					sleep(500).then(() => {
						let res = finergy.model.with_doctype(doc.doctype, () => {
							let newdoc = finergy.model.copy_doc(doc);
							newdoc.__newname = doc.name;
							delete doc.name;
							newdoc.idx = null;
							newdoc.__run_link_triggers = false;
							finergy.set_route('Form', newdoc.doctype, newdoc.name);
							finergy.dom.unfreeze();
						});
						res && res.fail(finergy.dom.unfreeze);
					});
				}
			} catch (e) {
				//
			}
		});
	},

	setup_moment() {
		moment.updateLocale('en', {
			week: {
				dow: finergy.datetime.get_first_day_of_the_week_index(),
			}
		});
		moment.locale("en");
		moment.user_utc_offset = moment().utcOffset();
		if (finergy.boot.timezone_info) {
			moment.tz.add(finergy.boot.timezone_info);
		}
	}
});

finergy.get_module = function(m, default_module) {
	var module = finergy.modules[m] || default_module;
	if (!module) {
		return;
	}

	if(module._setup) {
		return module;
	}

	if(!module.label) {
		module.label = m;
	}

	if(!module._label) {
		module._label = __(module.label);
	}

	module._setup = true;

	return module;
};
