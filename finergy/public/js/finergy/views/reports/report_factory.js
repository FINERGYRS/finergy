// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt

finergy.views.ReportFactory = class ReportFactory extends finergy.views.Factory {
	make(route) {
		const _route = ['List', route[1], 'Report'];

		if (route[2]) {
			// custom report
			_route.push(route[2]);
		}

		finergy.set_route(_route);
	}
}
