import finergy


def execute():
	finergy.delete_doc_if_exists("DocType", "Tag Category")
	finergy.delete_doc_if_exists("DocType", "Tag Doc Category")

	finergy.reload_doc("desk", "doctype", "tag")
	finergy.reload_doc("desk", "doctype", "tag_link")

	tag_list = []
	tag_links = []
	time = finergy.utils.get_datetime()

	for doctype in finergy.get_list("DocType", filters={"istable": 0, "issingle": 0}):
		if not finergy.db.count(doctype.name) or not finergy.db.has_column(doctype.name, "_user_tags"):
			continue

		for _user_tags in finergy.db.sql(
			"select `name`, `_user_tags` from `tab{0}`".format(doctype.name), as_dict=True
		):
			if not _user_tags.get("_user_tags"):
				continue

			for tag in _user_tags.get("_user_tags").split(",") if _user_tags.get("_user_tags") else []:
				if not tag:
					continue

				tag_list.append((tag.strip(), time, time, "Administrator"))

				tag_link_name = finergy.generate_hash(_user_tags.name + tag.strip() + doctype.name, 10)
				tag_links.append(
					(tag_link_name, doctype.name, _user_tags.name, tag.strip(), time, time, "Administrator")
				)

	finergy.db.bulk_insert(
		"Tag",
		fields=["name", "creation", "modified", "modified_by"],
		values=set(tag_list),
		ignore_duplicates=True,
	)
	finergy.db.bulk_insert(
		"Tag Link",
		fields=["name", "document_type", "document_name", "tag", "creation", "modified", "modified_by"],
		values=set(tag_links),
		ignore_duplicates=True,
	)
