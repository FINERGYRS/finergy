// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt

finergy.provide("finergy.help");

finergy.help.youtube_id = {};

finergy.help.has_help = function (doctype) {
	return finergy.help.youtube_id[doctype];
}

finergy.help.show = function (doctype) {
	if (finergy.help.youtube_id[doctype]) {
		finergy.help.show_video(finergy.help.youtube_id[doctype]);
	}
}

finergy.help.show_video = function (youtube_id, title) {
	if (finergy.utils.is_url(youtube_id)) {
		const expression = '(?:youtube.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu.be/)([^"&?\\s]{11})';
		youtube_id = youtube_id.match(expression)[1];
	}

	// (finergy.help_feedback_link || "")
	let dialog = new finergy.ui.Dialog({
		title: title || __("Help"),
		size: 'large'
	});

	let video = $(`<div class="video-player" data-plyr-provider="youtube" data-plyr-embed-id="${youtube_id}"></div>`);
	video.appendTo(dialog.body);

	dialog.show();
	dialog.$wrapper.addClass("video-modal");

	let plyr = new finergy.Plyr(video[0], {
		hideControls: true,
		resetOnEnd: true,
	});

	dialog.onhide = () => {
		plyr.destroy();
	};
}

$("body").on("click", "a.help-link", function () {
	var doctype = $(this).attr("data-doctype");
	doctype && finergy.help.show(doctype);
});
