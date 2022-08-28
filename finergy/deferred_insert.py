import json

import finergy
from finergy.utils import cstr

queue_prefix = "insert_queue_for_"


def deferred_insert(doctype, records):
	finergy.cache().rpush(queue_prefix + doctype, records)


def save_to_db():
	queue_keys = finergy.cache().get_keys(queue_prefix)
	for key in queue_keys:
		record_count = 0
		queue_key = get_key_name(key)
		doctype = get_doctype_name(key)
		while finergy.cache().llen(queue_key) > 0 and record_count <= 500:
			records = finergy.cache().lpop(queue_key)
			records = json.loads(records.decode("utf-8"))
			if isinstance(records, dict):
				record_count += 1
				insert_record(records, doctype)
				continue
			for record in records:
				record_count += 1
				insert_record(record, doctype)

	finergy.db.commit()


def insert_record(record, doctype):
	if not record.get("doctype"):
		record["doctype"] = doctype
	try:
		doc = finergy.get_doc(record)
		doc.insert()
	except Exception as e:
		print(e, doctype)


def get_key_name(key):
	return cstr(key).split("|")[1]


def get_doctype_name(key):
	return cstr(key).split(queue_prefix)[1]
