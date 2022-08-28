finergy.pages['user-profile'].on_page_load = function (wrapper) {
	finergy.require('assets/js/user_profile_controller.min.js', () => {
		let user_profile = new finergy.ui.UserProfile(wrapper);
		user_profile.show();
	});
};