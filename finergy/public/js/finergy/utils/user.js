finergy.user_info = function(uid) {
	if(!uid)
		uid = finergy.session.user;

	if(uid.toLowerCase()==="bot") {
		return {
			fullname: __("Bot"),
			image: "/assets/finergyrs/images/ui/bot.png",
			abbr: "B"
		};
	}

	if(!(finergy.boot.user_info && finergy.boot.user_info[uid])) {
		var user_info = {fullname: uid || "Unknown"};
	} else {
		var user_info = finergy.boot.user_info[uid];
	}

	user_info.abbr = finergy.get_abbr(user_info.fullname);
	user_info.color = finergy.get_palette(user_info.fullname);

	return user_info;
};

finergy.ui.set_user_background = function(src, selector, style) {
	if(!selector) selector = "#page-desktop";
	if(!style) style = "Fill Screen";
	if(src) {
		if (window.cordova && src.indexOf("http") === -1) {
			src = finergy.base_url + src;
		}
		var background = repl('background: url("%(src)s") center center;', {src: src});
	} else {
		var background = "background-color: #4B4C9D;";
	}

	finergy.dom.set_style(repl('%(selector)s { \
		%(background)s \
		background-attachment: fixed; \
		%(style)s \
	}', {
		selector:selector,
		background:background,
		style: style==="Fill Screen" ? "background-size: cover;" : ""
	}));
};

finergy.provide('finergy.user');

$.extend(finergy.user, {
	name: 'Guest',
	full_name: function(uid) {
		return uid === finergy.session.user ?
			__("You", null, "Name of the current user. For example: You edited this 5 hours ago.") :
			finergy.user_info(uid).fullname;
	},
	image: function(uid) {
		return finergy.user_info(uid).image;
	},
	abbr: function(uid) {
		return finergy.user_info(uid).abbr;
	},
	has_role: function(rl) {
		if(typeof rl=='string')
			rl = [rl];
		for(var i in rl) {
			if((finergy.boot ? finergy.boot.user.roles : ['Guest']).indexOf(rl[i])!=-1)
				return true;
		}
	},
	get_desktop_items: function() {
		// hide based on permission
		var modules_list = $.map(finergy.boot.allowed_modules, function(icon) {
			var m = icon.module_name;
			var type = finergy.modules[m] && finergy.modules[m].type;

			if(finergy.boot.user.allow_modules.indexOf(m) === -1) return null;

			var ret = null;
			if (type === "module") {
				if(finergy.boot.user.allow_modules.indexOf(m)!=-1 || finergy.modules[m].is_help)
					ret = m;
			} else if (type === "page") {
				if(finergy.boot.allowed_pages.indexOf(finergy.modules[m].link)!=-1)
					ret = m;
			} else if (type === "list") {
				if(finergy.model.can_read(finergy.modules[m]._doctype))
					ret = m;
			} else if (type === "view") {
				ret = m;
			} else if (type === "setup") {
				if(finergy.user.has_role("System Manager") || finergy.user.has_role("Administrator"))
					ret = m;
			} else {
				ret = m;
			}

			return ret;
		});

		return modules_list;
	},

	is_report_manager: function() {
		return finergy.user.has_role(['Administrator', 'System Manager', 'Report Manager']);
	},

	get_formatted_email: function(email) {
		var fullname = finergy.user.full_name(email);

		if (!fullname) {
			return email;
		} else {
			// to quote or to not
			var quote = '';

			// only if these special characters are found
			// why? To make the output same as that in python!
			if (fullname.search(/[\[\]\\()<>@,:;".]/) !== -1) {
				quote = '"';
			}

			return repl('%(quote)s%(fullname)s%(quote)s <%(email)s>', {
				fullname: fullname,
				email: email,
				quote: quote
			});
		}
	},

	get_emails: ( ) => {
		return Object.keys(finergy.boot.user_info).map(key => finergy.boot.user_info[key].email);
	},

	/* Normally finergy.user is an object
	 * having properties and methods.
	 * But in the following case
	 *
	 * if (finergy.user === 'Administrator')
	 *
	 * finergy.user will cast to a string
	 * returning finergy.user.name
	 */
	toString: function() {
		return this.name;
	}
});

finergy.session_alive = true;
$(document).bind('mousemove', function() {
	if(finergy.session_alive===false) {
		$(document).trigger("session_alive");
	}
	finergy.session_alive = true;
	if(finergy.session_alive_timeout)
		clearTimeout(finergy.session_alive_timeout);
	finergy.session_alive_timeout = setTimeout('finergy.session_alive=false;', 30000);
});