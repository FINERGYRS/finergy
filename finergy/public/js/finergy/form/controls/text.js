finergy.ui.form.ControlText = finergy.ui.form.ControlData.extend({
	html_element: "textarea",
	horizontal: false,
	make_wrapper: function() {
		this._super();
		this.$wrapper.find(".like-disabled-input").addClass("for-description");
	},
	make_input: function() {
		this._super();
		this.$input.css({'height': '300px'});
	}
});

finergy.ui.form.ControlLongText = finergy.ui.form.ControlText;
finergy.ui.form.ControlSmallText = finergy.ui.form.ControlText.extend({
	make_input: function() {
		this._super();
		this.$input.css({'height': '150px'});
	}
});
