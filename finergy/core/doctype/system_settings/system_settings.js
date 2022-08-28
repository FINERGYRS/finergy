finergy.ui.form.on("System Settings", {
	refresh: function(frm) {
		finergy.call({
			method: "finergy.core.doctype.system_settings.system_settings.load",
			callback: function(data) {
				finergy.all_timezones = data.message.timezones;
				frm.set_df_property("time_zone", "options", finergy.all_timezones);

				$.each(data.message.defaults, function(key, val) {
					frm.set_value(key, val);
					finergy.sys_defaults[key] = val;
				});
				if (frm.re_setup_moment) {
					finergy.app.setup_moment();
					delete frm.re_setup_moment;
				}
			}
		});
	},
	enable_password_policy: function(frm) {
		if (frm.doc.enable_password_policy == 0) {
			frm.set_value("minimum_password_score", "");
		} else {
			frm.set_value("minimum_password_score", "2");
		}
	},
	enable_two_factor_auth: function(frm) {
		if (frm.doc.enable_two_factor_auth == 0) {
			frm.set_value("bypass_2fa_for_retricted_ip_users", 0);
			frm.set_value("bypass_restrict_ip_check_if_2fa_enabled", 0);
		}
	},
	enable_prepared_report_auto_deletion: function(frm) {
		if (frm.doc.enable_prepared_report_auto_deletion) {
			if (!frm.doc.prepared_report_expiry_period) {
				frm.set_value('prepared_report_expiry_period', 7);
			}
		}
	},
	on_update: function(frm) {
		if (finergy.boot.time_zone && finergy.boot.time_zone.system !== frm.doc.time_zone) {
			// Clear cache after saving to refresh the values of boot.
			finergy.ui.toolbar.clear_cache();
		}
	},
	first_day_of_the_week(frm) {
		frm.re_setup_moment = true;
	},
});
