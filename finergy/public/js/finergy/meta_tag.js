finergy.provide('finergy.model');
finergy.provide('finergy.utils');

/**
 * Opens the Website Meta Tag form if it exists for {route}
 * or creates a new doc and opens the form
 */
finergy.utils.set_meta_tag = function(route) {
	finergy.db.exists('Website Route Meta', route)
		.then(exists => {
			if (exists) {
				finergy.set_route('Form', 'Website Route Meta', route);
			} else {
				// new doc
				const doc = finergy.model.get_new_doc('Website Route Meta');
				doc.__newname = route;
				finergy.set_route('Form', doc.doctype, doc.name);
			}
		});
};
