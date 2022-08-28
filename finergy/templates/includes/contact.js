// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt

finergy.ready(function() {

	if(finergy.utils.get_url_arg('subject')) {
	  $('[name="subject"]').val(finergy.utils.get_url_arg('subject'));
	}

	$('.btn-send').off("click").on("click", function() {
		var email = $('[name="email"]').val();
		var message = $('[name="message"]').val();

		if(!(email && message)) {
			finergy.msgprint('{{ _("Please enter both your email and message so that we can get back to you. Thanks!") }}');
			return false;
		}

		if(!validate_email(email)) {
			finergy.msgprint('{{ _("You seem to have written your name instead of your email. Please enter a valid email address so that we can get back.") }}');
			$('[name="email"]').focus();
			return false;
		}

		$("#contact-alert").toggle(false);
		finergy.send_message({
			subject: $('[name="subject"]').val(),
			sender: email,
			message: message,
			callback: function(r) {
				if(r.message==="okay") {
					finergy.msgprint('{{ _("Thank you for your message") }}');
				} else {
					finergy.msgprint('{{ _("There were errors") }}');
					console.log(r.exc);
				}
				$(':input').val('');
			}
		}, this);
		return false;
	});

});

var msgprint = function(txt) {
	if(txt) $("#contact-alert").html(txt).toggle(true);
}
