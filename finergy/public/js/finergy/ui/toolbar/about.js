finergy.provide('finergy.ui.misc');
finergy.ui.misc.about = function() {
	if(!finergy.ui.misc.about_dialog) {
		var d = new finergy.ui.Dialog({title: __('Finergy Framework')});

		$(d.body).html(repl("<div>\
		<p>"+__("Open Source Applications for the Web")+"</p>  \
		<p><i class='fa fa-globe fa-fw'></i>\
			Website: <a href='https://finergy-rs.fr' target='_blank'>https://finergy-rs.fr</a></p>\
		<p><i class='fa fa-github fa-fw'></i>\
			Source: <a href='https://github.com/finergy' target='_blank'>https://github.com/finergy</a></p>\
		<p><i class='fa fa-linkedin fa-fw'></i>\
			Linkedin: <a href='https://linkedin.com/company/finergy-tech' target='_blank'>https://linkedin.com/company/finergy-tech</a></p>\
		<p><i class='fa fa-facebook fa-fw'></i>\
			Facebook: <a href='https://facebook.com/capkpi' target='_blank'>https://facebook.com/capkpi</a></p>\
		<p><i class='fa fa-twitter fa-fw'></i>\
			Twitter: <a href='https://twitter.com/capkpi' target='_blank'>https://twitter.com/capkpi</a></p>\
		<hr>\
		<h4>Installed Apps</h4>\
		<div id='about-app-versions'>Loading versions...</div>\
		<hr>\
		<p class='text-muted'>&copy; Finergy Technologies Pvt. Ltd and contributors </p> \
		</div>", finergy.app));

		finergy.ui.misc.about_dialog = d;

		finergy.ui.misc.about_dialog.on_page_show = function() {
			if(!finergy.versions) {
				finergy.call({
					method: "finergy.utils.change_log.get_versions",
					callback: function(r) {
						show_versions(r.message);
					}
				})
			} else {
				show_versions(finergy.versions);
			}
		};

		var show_versions = function(versions) {
			var $wrap = $("#about-app-versions").empty();
			$.each(Object.keys(versions).sort(), function(i, key) {
				var v = versions[key];
				if(v.branch) {
					var text = $.format('<p><b>{0}:</b> v{1} ({2})<br></p>',
						[v.title, v.branch_version || v.version, v.branch])
				} else {
					var text = $.format('<p><b>{0}:</b> v{1}<br></p>',
						[v.title, v.version])
				}
				$(text).appendTo($wrap);
			});

			finergy.versions = versions;
		}

	}

	finergy.ui.misc.about_dialog.show();

}
