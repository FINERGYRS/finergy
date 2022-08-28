// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt

finergy.provide("finergy.messages");

import './dialog';

finergy.messages.waiting = function(parent, msg) {
	return $(finergy.messages.get_waiting_message(msg))
		.appendTo(parent);
};

finergy.messages.get_waiting_message = function(msg) {
	return repl('<div class="msg-box" style="width: 63%; margin: 30px auto;">\
		<p class="text-center">%(msg)s</p></div>', { msg: msg });
}

finergy.throw = function(msg) {
	if(typeof msg==='string') {
		msg = {message: msg, title: __('Error')};
	}
	if(!msg.indicator) msg.indicator = 'red';
	finergy.msgprint(msg);
	throw new Error(msg.message);
}

finergy.confirm = function(message, confirm_action, reject_action) {
	var d = new finergy.ui.Dialog({
		title: __("Confirm"),
		primary_action_label: __("Yes"),
		primary_action: () => {
			confirm_action && confirm_action();
			d.hide();
		},
		secondary_action_label: __("No"),
		secondary_action: () => d.hide(),
	});

	d.$body.append(`<p class="finergy-confirm-message">${message}</p>`);
	d.show();

	// flag, used to bind "okay" on enter
	d.confirm_dialog = true;

	// no if closed without primary action
	if (reject_action) {
		d.onhide = () => {
			if (!d.primary_action_fulfilled) {
				reject_action();
			}
		};
	}

	return d;
};

finergy.warn = function(title, message_html, proceed_action, primary_label, is_minimizable) {
	const d = new finergy.ui.Dialog({
		title: title,
		indicator: 'red',
		primary_action_label: primary_label,
		primary_action: () => {
			if (proceed_action) proceed_action();
			d.hide();
		},
		secondary_action_label: __("Cancel", null, "Secondary button in warning dialog"),
		secondary_action: () => d.hide(),
		minimizable: is_minimizable
	});

	d.$body.append(`<div class="finergy-confirm-message">${message_html}</div>`);
	d.standard_actions.find('.btn-primary').removeClass('btn-primary').addClass('btn-danger');
	d.standard_actions.find('.btn-primary').removeClass('btn-primary').addClass('btn-danger');

	d.show();
	return d;
};

finergy.prompt = function(fields, callback, title, primary_label) {
	if (typeof fields === "string") {
		fields = [{
			label: fields,
			fieldname: "value",
			fieldtype: "Data",
			reqd: 1
		}];
	}
	if(!$.isArray(fields)) fields = [fields];
	var d = new finergy.ui.Dialog({
		fields: fields,
		title: title || __("Enter Value"),
	});
	d.set_primary_action(primary_label || __("Submit"), function() {
		var values = d.get_values();
		if(!values) {
			return;
		}
		d.hide();
		callback(values);
	});
	d.show();
	return d;
}

finergy.msgprint = function(msg, title, is_minimizable) {
	if(!msg) return;

	if($.isPlainObject(msg)) {
		var data = msg;
	} else {
		// passed as JSON
		if(typeof msg==='string' && msg.substr(0,1)==='{') {
			var data = JSON.parse(msg);
		} else {
			var data = {'message': msg, 'title': title};
		}
	}

	if(!data.indicator) {
		data.indicator = 'blue';
	}

	if (data.as_list) {
		const list_rows = data.message.map(m => `<li>${m}</li>`).join('');
		data.message = `<ul style="padding-left: 20px">${list_rows}</ul>`;
	}

	if (data.as_table) {
		const rows = data.message.map(row => {
			const cols = row.map(col => `<td>${col}</td>`).join('');
			return `<tr>${cols}</tr>`;
		}).join('');
		data.message = `<table class="table table-bordered" style="margin: 0;">${rows}</table>`;
	}

	if(data.message instanceof Array) {
		data.message.forEach(function(m) {
			finergy.msgprint(m);
		});
		return;
	}

	if(data.alert) {
		finergy.show_alert(data);
		return;
	}

	if(!finergy.msg_dialog) {
		finergy.msg_dialog = new finergy.ui.Dialog({
			title: __("Message"),
			onhide: function() {
				if(finergy.msg_dialog.custom_onhide) {
					finergy.msg_dialog.custom_onhide();
				}
				finergy.msg_dialog.msg_area.empty();
			},
			minimizable: data.is_minimizable || is_minimizable
		});

		// class "msgprint" is used in tests
		finergy.msg_dialog.msg_area = $('<div class="msgprint">')
			.appendTo(finergy.msg_dialog.body);

		finergy.msg_dialog.clear = function() {
			finergy.msg_dialog.msg_area.empty();
		}

		finergy.msg_dialog.indicator = finergy.msg_dialog.header.find('.indicator');
	}

	// setup and bind an action to the primary button
	if (data.primary_action) {
		if (data.primary_action.server_action && typeof data.primary_action.server_action === 'string') {
			data.primary_action.action = () => {
				finergy.call({
					method: data.primary_action.server_action,
					args: {
						args: data.primary_action.args
					},
					callback() {
						if (data.primary_action.hide_on_success) {
							finergy.hide_msgprint();
						}
					}
				});
			}
		}

		if (data.primary_action.client_action && typeof data.primary_action.client_action === 'string') {
			let parts = data.primary_action.client_action.split('.');
			let obj = window;
			for (let part of parts) {
				obj = obj[part];
			}
			data.primary_action.action = () => {
				if (typeof obj === 'function') {
					obj(data.primary_action.args);
				}
			}
		}

		finergy.msg_dialog.set_primary_action(
			__(data.primary_action.label || data.primary_action_label || "Done"),
			data.primary_action.action
		);
	} else {
		if (finergy.msg_dialog.has_primary_action) {
			finergy.msg_dialog.get_primary_btn().addClass('hide');
			finergy.msg_dialog.has_primary_action = false;
		}
	}

	if (data.secondary_action) {
		finergy.msg_dialog.set_secondary_action(data.secondary_action.action);
		finergy.msg_dialog.set_secondary_action_label(__(data.secondary_action.label || "Close"));
	}

	if(data.message==null) {
		data.message = '';
	}

	if(data.message.search(/<br>|<p>|<li>/)==-1) {
		msg = finergy.utils.replace_newlines(data.message);
	}

	var msg_exists = false;
	if(data.clear) {
		finergy.msg_dialog.msg_area.empty();
	} else {
		msg_exists = finergy.msg_dialog.msg_area.html();
	}

	if(data.title || !msg_exists) {
		// set title only if it is explicitly given
		// and no existing title exists
		finergy.msg_dialog.set_title(data.title || __('Message', null, 'Default title of the message dialog'));
	}

	// show / hide indicator
	if(data.indicator) {
		finergy.msg_dialog.indicator.removeClass().addClass('indicator ' + data.indicator);
	} else {
		finergy.msg_dialog.indicator.removeClass().addClass('hidden');
	}

	// width
	if (data.wide) {
		// msgprint should be narrower than the usual dialog
		if (finergy.msg_dialog.wrapper.classList.contains('msgprint-dialog')) {
			finergy.msg_dialog.wrapper.classList.remove('msgprint-dialog');
		}
	} else {
		// msgprint should be narrower than the usual dialog
		finergy.msg_dialog.wrapper.classList.add('msgprint-dialog');
	}

	if(msg_exists) {
		finergy.msg_dialog.msg_area.append("<hr>");
	// append a <hr> if another msg already exists
	}

	finergy.msg_dialog.msg_area.append(data.message);

	// make msgprint always appear on top
	finergy.msg_dialog.$wrapper.css("z-index", 2000);
	finergy.msg_dialog.show();

	return finergy.msg_dialog;
}

window.msgprint = finergy.msgprint;

finergy.hide_msgprint = function(instant) {
	// clear msgprint
	if(finergy.msg_dialog && finergy.msg_dialog.msg_area) {
		finergy.msg_dialog.msg_area.empty();
	}
	if(finergy.msg_dialog && finergy.msg_dialog.$wrapper.is(":visible")) {
		if(instant) {
			finergy.msg_dialog.$wrapper.removeClass("fade");
		}
		finergy.msg_dialog.hide();
		if(instant) {
			finergy.msg_dialog.$wrapper.addClass("fade");
		}
	}
}

// update html in existing msgprint
finergy.update_msgprint = function(html) {
	if(!finergy.msg_dialog || (finergy.msg_dialog && !finergy.msg_dialog.$wrapper.is(":visible"))) {
		finergy.msgprint(html);
	} else {
		finergy.msg_dialog.msg_area.html(html);
	}
}

finergy.verify_password = function(callback) {
	finergy.prompt({
		fieldname: "password",
		label: __("Enter your password"),
		fieldtype: "Password",
		reqd: 1
	}, function(data) {
		finergy.call({
			method: "finergy.core.doctype.user.user.verify_password",
			args: {
				password: data.password
			},
			callback: function(r) {
				if(!r.exc) {
					callback();
				}
			}
		});
	}, __("Verify Password"), __("Verify"))
}

finergy.show_progress = (title, count, total = 100, description, hide_on_completion = false) => {
	let dialog;
	if (
		finergy.cur_progress &&
		finergy.cur_progress.title === title &&
		finergy.cur_progress.is_visible
	) {
		dialog = finergy.cur_progress;
	} else {
		dialog = new finergy.ui.Dialog({
			title: title
		});
		dialog.progress = $(`<div>
			<div class="progress">
				<div class="progress-bar"></div>
			</div>
			<p class="description text-muted small"></p>
		</div`).appendTo(dialog.body);
		dialog.progress_bar = dialog.progress
			.css({ 'margin-top': '10px' })
			.find('.progress-bar');
		dialog.$wrapper.removeClass('fade');
		dialog.show();
		finergy.cur_progress = dialog;
	}
	if (description) {
		dialog.progress.find('.description').text(description);
	}
	dialog.percent = cint((flt(count) * 100) / total);
	dialog.progress_bar.css({ width: dialog.percent + '%' });
	if (hide_on_completion && dialog.percent === 100) {
		// timeout to avoid abrupt hide
		setTimeout(finergy.hide_progress, 500);
	}
	return dialog;
};

finergy.hide_progress = function() {
	if(finergy.cur_progress) {
		finergy.cur_progress.hide();
		finergy.cur_progress = null;
	}
}

// Floating Message
finergy.show_alert = function(message, seconds=7, actions={}) {
	let indicator_icon_map = {
		'orange': "solid-warning",
		'yellow': "solid-warning",
		'blue': "solid-info",
		'green': "solid-success",
		'red': "solid-error"
	};

	if (typeof message==='string') {
		message = {
			message: message
		};
	}

	if (!$('#dialog-container').length) {
		$('<div id="dialog-container"><div id="alert-container"></div></div>').appendTo('body');
	}

	let icon;
	if (message.indicator) {
		icon = indicator_icon_map[message.indicator.toLowerCase()] || 'solid-' + message.indicator;
	} else {
		icon = 'solid-info';
	}

	const indicator = message.indicator || 'blue';

	const div = $(`
		<div class="alert desk-alert ${indicator}" role="alert">
			<div class="alert-message-container">
				<div class="alert-title-container">
					<div>${finergy.utils.icon(icon, 'lg')}</div>
					<div class="alert-message">${message.message}</div>
				</div>
				<div class="alert-subtitle">${message.subtitle || '' }</div>
			</div>
			<div class="alert-body" style="display: none"></div>
			<a class="close">${finergy.utils.icon('close-alt')}</a>
		</div>
	`);

	div.hide().appendTo("#alert-container").show();

	if (message.body) {
		div.find('.alert-body').show().html(message.body);
	}

	div.find('.close, button').click(function() {
		div.addClass('out');
		setTimeout(() => div.remove(), 800);
		return false;
	});

	Object.keys(actions).map(key => {
		div.find(`[data-action=${key}]`).on('click', actions[key]);
	});

	if (seconds > 2) {
		// Delay for animation
		seconds = seconds - 0.8;
	}

	setTimeout(() => {
		div.addClass('out');
		setTimeout(() => div.remove(), 800);
		return false;
	}, seconds * 1000);

	return div;
}

// Proxy for finergy.show_alert
Object.defineProperty(window, 'show_alert', {
	get: function() {
		console.warn('Please use `finergy.show_alert` instead of `show_alert`. It will be deprecated soon.');
		return finergy.show_alert;
	}
});
