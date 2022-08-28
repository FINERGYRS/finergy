finergy.route_history_queue = [];
const routes_to_skip = ['Form', 'social', 'setup-wizard', 'recorder'];

const save_routes = finergy.utils.debounce(() => {
	if (finergy.session.user === 'Guest') return;
	const routes = finergy.route_history_queue;
	if (!routes.length) return;

	finergy.route_history_queue = [];

	finergy.xcall('finergy.desk.doctype.route_history.route_history.deferred_insert', {
		'routes': routes
	}).catch(() => {
		finergy.route_history_queue.concat(routes);
	});

}, 10000);

finergy.router.on('change', () => {
	const route = finergy.get_route();
	if (is_route_useful(route)) {
		finergy.route_history_queue.push({
			'creation': finergy.datetime.now_datetime(),
			'route': finergy.get_route_str()
		});

		save_routes();
	}
});

function is_route_useful(route) {
	if (!route[1]) {
		return false;
	} else if ((route[0] === 'List' && !route[2]) || routes_to_skip.includes(route[0])) {
		return false;
	} else {
		return true;
	}
}