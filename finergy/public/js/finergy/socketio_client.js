finergy.socketio = {
	open_tasks: {},
	open_docs: [],
	emit_queue: [],
	init: function(port = 3000) {
		if (!window.io) {
			return;
		}

		if (finergy.boot.disable_async) {
			return;
		}

		if (finergy.socketio.socket) {
			return;
		}

		//Enable secure option when using HTTPS
		if (window.location.protocol == "https:") {
			finergy.socketio.socket = io.connect(finergy.socketio.get_host(port), {secure: true});
		}
		else if (window.location.protocol == "http:") {
			finergy.socketio.socket = io.connect(finergy.socketio.get_host(port));
		}
		else if (window.location.protocol == "file:") {
			finergy.socketio.socket = io.connect(window.localStorage.server);
		}

		if (!finergy.socketio.socket) {
			console.log("Unable to connect to " + finergy.socketio.get_host(port));
			return;
		}

		finergy.socketio.socket.on('msgprint', function(message) {
			finergy.msgprint(message);
		});

		finergy.socketio.socket.on('eval_js', function(message) {
			eval(message);
		});

		finergy.socketio.socket.on('progress', function(data) {
			if(data.progress) {
				data.percent = flt(data.progress[0]) / data.progress[1] * 100;
			}
			if(data.percent) {
				if(data.percent==100) {
					finergy.hide_progress();
				} else {
					finergy.show_progress(data.title || __("Progress"), data.percent, 100, data.description);
				}
			}
		});

		finergy.socketio.setup_listeners();
		finergy.socketio.setup_reconnect();

		$(document).on('form-load form-rename', function(e, frm) {
			if (frm.is_new()) {
				return;
			}

			for (var i=0, l=finergy.socketio.open_docs.length; i<l; i++) {
				var d = finergy.socketio.open_docs[i];
				if (frm.doctype==d.doctype && frm.docname==d.name) {
					// already subscribed
					return false;
				}
			}

			finergy.socketio.doc_subscribe(frm.doctype, frm.docname);
		});

		$(document).on("form-refresh", function(e, frm) {
			if (frm.is_new()) {
				return;
			}

			finergy.socketio.doc_open(frm.doctype, frm.docname);
		});

		$(document).on('form-unload', function(e, frm) {
			if (frm.is_new()) {
				return;
			}

			// finergy.socketio.doc_unsubscribe(frm.doctype, frm.docname);
			finergy.socketio.doc_close(frm.doctype, frm.docname);
		});

		$(document).on('form-typing', function(e, frm) {
			finergy.socketio.form_typing(frm.doctype, frm.docname);
		});

		$(document).on('form-stopped-typing', function(e, frm) {
			finergy.socketio.form_stopped_typing(frm.doctype, frm.docname);
		});

		window.addEventListener('beforeunload', () => {
			if (!cur_frm || cur_frm.is_new()) {
				return;
			}

			// if tab/window is closed, notify other users
			if (cur_frm.doc) {
				finergy.socketio.doc_close(cur_frm.doctype, cur_frm.docname);
			}
		});
	},
	get_host: function(port = 3000) {
		var host = window.location.origin;
		if(window.dev_server) {
			var parts = host.split(":");
			port = finergy.boot.socketio_port || port.toString() || '3000';
			if(parts.length > 2) {
				host = parts[0] + ":" + parts[1];
			}
			host = host + ":" + port;
		}
		return host;
	},
	subscribe: function(task_id, opts) {
		// TODO DEPRECATE

		finergy.socketio.socket.emit('task_subscribe', task_id);
		finergy.socketio.socket.emit('progress_subscribe', task_id);

		finergy.socketio.open_tasks[task_id] = opts;
	},
	task_subscribe: function(task_id) {
		finergy.socketio.socket.emit('task_subscribe', task_id);
	},
	task_unsubscribe: function(task_id) {
		finergy.socketio.socket.emit('task_unsubscribe', task_id);
	},
	doc_subscribe: function(doctype, docname) {
		if (finergy.flags.doc_subscribe) {
			console.log('throttled');
			return;
		}

		finergy.flags.doc_subscribe = true;

		// throttle to 1 per sec
		setTimeout(function() { finergy.flags.doc_subscribe = false }, 1000);

		finergy.socketio.socket.emit('doc_subscribe', doctype, docname);
		finergy.socketio.open_docs.push({doctype: doctype, docname: docname});
	},
	doc_unsubscribe: function(doctype, docname) {
		finergy.socketio.socket.emit('doc_unsubscribe', doctype, docname);
		finergy.socketio.open_docs = $.filter(finergy.socketio.open_docs, function(d) {
			if(d.doctype===doctype && d.name===docname) {
				return null;
			} else {
				return d;
			}
		})
	},
	doc_open: function(doctype, docname) {
		// notify that the user has opened this doc, if not already notified
		if (!finergy.socketio.last_doc
			|| (finergy.socketio.last_doc[0] != doctype || finergy.socketio.last_doc[1] != docname)) {
			finergy.socketio.socket.emit('doc_open', doctype, docname);

			finergy.socketio.last_doc &&
				finergy.socketio.doc_close(finergy.socketio.last_doc[0], finergy.socketio.last_doc[1]);
		}
		finergy.socketio.last_doc = [doctype, docname];
	},
	doc_close: function(doctype, docname) {
		// notify that the user has closed this doc
		finergy.socketio.socket.emit('doc_close', doctype, docname);

		// if the doc is closed the user has also stopped typing
		finergy.socketio.socket.emit('doc_typing_stopped', doctype, docname);
	},
	form_typing: function(doctype, docname) {
		// notifiy that the user is typing on the doc
		finergy.socketio.socket.emit('doc_typing', doctype, docname);
	},
	form_stopped_typing: function(doctype, docname) {
		// notifiy that the user has stopped typing
		finergy.socketio.socket.emit('doc_typing_stopped', doctype, docname);
	},
	setup_listeners: function() {
		finergy.socketio.socket.on('task_status_change', function(data) {
			finergy.socketio.process_response(data, data.status.toLowerCase());
		});
		finergy.socketio.socket.on('task_progress', function(data) {
			finergy.socketio.process_response(data, "progress");
		});
	},
	setup_reconnect: function() {
		// subscribe again to open_tasks
		finergy.socketio.socket.on("connect", function() {
			// wait for 5 seconds before subscribing again
			// because it takes more time to start python server than nodejs server
			// and we use validation requests to python server for subscribing
			setTimeout(function() {
				$.each(finergy.socketio.open_tasks, function(task_id, opts) {
					finergy.socketio.subscribe(task_id, opts);
				});

				// re-connect open docs
				$.each(finergy.socketio.open_docs, function(d) {
					if(locals[d.doctype] && locals[d.doctype][d.name]) {
						finergy.socketio.doc_subscribe(d.doctype, d.name);
					}
				});

				if (cur_frm && cur_frm.doc) {
					finergy.socketio.doc_open(cur_frm.doc.doctype, cur_frm.doc.name);
				}
			}, 5000);
		});
	},
	process_response: function(data, method) {
		if(!data) {
			return;
		}

		// success
		var opts = finergy.socketio.open_tasks[data.task_id];
		if(opts[method]) {
			opts[method](data);
		}

		// "callback" is std finergy term
		if(method==="success") {
			if(opts.callback) opts.callback(data);
		}

		// always
		finergy.request.cleanup(opts, data);
		if(opts.always) {
			opts.always(data);
		}

		// error
		if(data.status_code && data.status_code > 400 && opts.error) {
			opts.error(data);
		}
	}
}

finergy.provide("finergy.realtime");
finergy.realtime.on = function(event, callback) {
	finergy.socketio.socket && finergy.socketio.socket.on(event, callback);
};

finergy.realtime.off = function(event, callback) {
	finergy.socketio.socket && finergy.socketio.socket.off(event, callback);
}

finergy.realtime.publish = function(event, message) {
	if(finergy.socketio.socket) {
		finergy.socketio.socket.emit(event, message);
	}
}

