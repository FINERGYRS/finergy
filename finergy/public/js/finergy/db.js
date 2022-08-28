// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt

finergy.db = {
	get_list: function(doctype, args) {
		if (!args) {
			args = {};
		}
		args.doctype = doctype;
		if (!args.fields) {
			args.fields = ['name'];
		}
		if (!('limit' in args)) {
			args.limit = 20;
		}
		return new Promise ((resolve) => {
			finergy.call({
				method: 'finergy.desk.reportview.get_list',
				args: args,
				type: 'GET',
				callback: function(r) {
					resolve(r.message);
				}
			});
		});
	},
	exists: function(doctype, name) {
		return new Promise ((resolve) => {
			finergy.db.get_value(doctype, {name: name}, 'name').then((r) => {
				(r.message && r.message.name) ? resolve(true) : resolve(false);
			});
		});
	},
	get_value: function(doctype, filters, fieldname, callback, parent_doc) {
		return finergy.call({
			method: "finergy.client.get_value",
			type: 'GET',
			args: {
				doctype: doctype,
				fieldname: fieldname,
				filters: filters,
				parent: parent_doc
			},
			callback: function(r) {
				callback && callback(r.message);
			}
		});
	},
	get_single_value: (doctype, field) => {
		return new Promise(resolve => {
			finergy.call({
				method: 'finergy.client.get_single_value',
				args: { doctype, field },
				type: 'GET',
			}).then(r => resolve(r ? r.message : null));
		});
	},
	set_value: function(doctype, docname, fieldname, value, callback) {
		return finergy.call({
			method: "finergy.client.set_value",
			args: {
				doctype: doctype,
				name: docname,
				fieldname: fieldname,
				value: value
			},
			callback: function(r) {
				callback && callback(r.message);
			}
		});
	},
	get_doc: function (doctype, name, filters) {
		return new Promise((resolve, reject) => {
			finergy.call({
				method: "finergy.client.get",
				type: 'GET',
				args: { doctype, name, filters },
				callback: r => {
					finergy.model.sync(r.message);
					resolve(r.message);
				}
			}).fail(reject);
		});
	},
	insert: function(doc) {
		return finergy.xcall('finergy.client.insert', { doc });
	},
	delete_doc: function(doctype, name) {
		return new Promise(resolve => {
			finergy.call('finergy.client.delete', { doctype, name }, r => resolve(r.message));
		});
	},
	count: function(doctype, args={}) {
		let filters = args.filters || {};

		// has a filter with childtable?
		const distinct = Array.isArray(filters) && filters.some(filter => {
			return filter[0] !== doctype;
		});

		const fields = [];

		return finergy.xcall('finergy.desk.reportview.get_count', {
			doctype,
			filters,
			fields,
			distinct,
		});
	},
	get_link_options(doctype, txt = '', filters={}) {
		return new Promise(resolve => {
			finergy.call({
				type: 'GET',
				method: 'finergy.desk.search.search_link',
				args: {
					doctype,
					txt,
					filters
				},
				callback(r) {
					resolve(r.results);
				}
			});
		});
	}
};
