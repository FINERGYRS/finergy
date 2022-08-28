# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

from werkzeug.wrappers import Response

import finergy
import finergy.sessions
import finergy.utils
from finergy import _, is_whitelisted
from finergy.core.doctype.server_script.server_script_utils import get_server_script_map
from finergy.utils import cint
from finergy.utils.csvutils import build_csv_response
from finergy.utils.response import build_response

ALLOWED_MIMETYPES = (
	"image/png",
	"image/jpeg",
	"application/pdf",
	"application/msword",
	"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
	"application/vnd.ms-excel",
	"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	"application/vnd.oasis.opendocument.text",
	"application/vnd.oasis.opendocument.spreadsheet",
	"text/plain",
)


def handle():
	"""handle request"""

	cmd = finergy.local.form_dict.cmd
	data = None

	if cmd != "login":
		data = execute_cmd(cmd)

	# data can be an empty string or list which are valid responses
	if data is not None:
		if isinstance(data, Response):
			# method returns a response object, pass it on
			return data

		# add the response to `message` label
		finergy.response["message"] = data

	return build_response("json")


def execute_cmd(cmd, from_async=False):
	"""execute a request as python module"""
	for hook in finergy.get_hooks("override_whitelisted_methods", {}).get(cmd, []):
		# override using the first hook
		cmd = hook
		break

	# via server script
	server_script = get_server_script_map().get("_api", {}).get(cmd)
	if server_script:
		return run_server_script(server_script)

	try:
		method = get_attr(cmd)
	except Exception as e:
		finergy.throw(_("Failed to get method for command {0} with {1}").format(cmd, e))

	if from_async:
		method = method.queue

	if method != run_doc_method:
		is_whitelisted(method)
		is_valid_http_method(method)

	return finergy.call(method, **finergy.form_dict)


def run_server_script(server_script):
	response = finergy.get_doc("Server Script", server_script).execute_method()

	# some server scripts return output using flags (empty dict by default),
	# while others directly modify finergy.response
	# return flags if not empty dict (this overwrites finergy.response.message)
	if response != {}:
		return response


def is_valid_http_method(method):
	if finergy.flags.in_safe_exec:
		return

	http_method = finergy.local.request.method

	if http_method not in finergy.allowed_http_methods_for_whitelisted_func[method]:
		throw_permission_error()


def throw_permission_error():
	finergy.throw(_("Not permitted"), finergy.PermissionError)


@finergy.whitelist(allow_guest=True)
def version():
	return finergy.__version__


@finergy.whitelist(allow_guest=True)
def logout():
	finergy.local.login_manager.logout()
	finergy.db.commit()


@finergy.whitelist(allow_guest=True)
def web_logout():
	finergy.local.login_manager.logout()
	finergy.db.commit()
	finergy.respond_as_web_page(
		_("Logged Out"), _("You have been successfully logged out"), indicator_color="green"
	)


@finergy.whitelist()
def uploadfile():
	ret = None

	try:
		if finergy.form_dict.get("from_form"):
			try:
				ret = finergy.get_doc(
					{
						"doctype": "File",
						"attached_to_name": finergy.form_dict.docname,
						"attached_to_doctype": finergy.form_dict.doctype,
						"attached_to_field": finergy.form_dict.docfield,
						"file_url": finergy.form_dict.file_url,
						"file_name": finergy.form_dict.filename,
						"is_private": finergy.utils.cint(finergy.form_dict.is_private),
						"content": finergy.form_dict.filedata,
						"decode": True,
					}
				)
				ret.save()
			except finergy.DuplicateEntryError:
				# ignore pass
				ret = None
				finergy.db.rollback()
		else:
			if finergy.form_dict.get("method"):
				method = finergy.get_attr(finergy.form_dict.method)
				is_whitelisted(method)
				ret = method()
	except Exception:
		finergy.errprint(finergy.utils.get_traceback())
		finergy.response["http_status_code"] = 500
		ret = None

	return ret


@finergy.whitelist(allow_guest=True)
def upload_file():
	user = None
	if finergy.session.user == "Guest":
		if finergy.get_system_settings("allow_guests_to_upload_files"):
			ignore_permissions = True
		else:
			return
	else:
		user = finergy.get_doc("User", finergy.session.user)
		ignore_permissions = False

	files = finergy.request.files
	is_private = finergy.form_dict.is_private
	doctype = finergy.form_dict.doctype
	docname = finergy.form_dict.docname
	fieldname = finergy.form_dict.fieldname
	file_url = finergy.form_dict.file_url
	folder = finergy.form_dict.folder or "Home"
	method = finergy.form_dict.method
	filename = finergy.form_dict.file_name
	content = None

	if "file" in files:
		file = files["file"]
		content = file.stream.read()
		filename = file.filename

	finergy.local.uploaded_file = content
	finergy.local.uploaded_filename = filename

	if content is not None and (
		finergy.session.user == "Guest" or (user and not user.has_desk_access())
	):
		import mimetypes

		filetype = mimetypes.guess_type(filename)[0]
		if filetype not in ALLOWED_MIMETYPES:
			finergy.throw(_("You can only upload JPG, PNG, PDF, TXT or Microsoft documents."))

	if method:
		method = finergy.get_attr(method)
		is_whitelisted(method)
		return method()
	else:
		ret = finergy.get_doc(
			{
				"doctype": "File",
				"attached_to_doctype": doctype,
				"attached_to_name": docname,
				"attached_to_field": fieldname,
				"folder": folder,
				"file_name": filename,
				"file_url": file_url,
				"is_private": cint(is_private),
				"content": content,
			}
		)
		ret.save(ignore_permissions=ignore_permissions)
		return ret


def get_attr(cmd):
	"""get method object from cmd"""
	if "." in cmd:
		method = finergy.get_attr(cmd)
	else:
		method = globals()[cmd]
	finergy.log("method:" + cmd)
	return method


@finergy.whitelist(allow_guest=True)
def ping():
	return "pong"


def run_doc_method(method, docs=None, dt=None, dn=None, arg=None, args=None):
	"""run a whitelisted controller method"""
	import inspect
	import json

	if not args:
		args = arg or ""

	if dt:  # not called from a doctype (from a page)
		if not dn:
			dn = dt  # single
		doc = finergy.get_doc(dt, dn)

	else:
		if isinstance(docs, str):
			docs = json.loads(docs)

		doc = finergy.get_doc(docs)
		doc._original_modified = doc.modified
		doc.check_if_latest()

	if not doc or not doc.has_permission("read"):
		throw_permission_error()

	try:
		args = json.loads(args)
	except ValueError:
		args = args

	method_obj = getattr(doc, method)
	fn = getattr(method_obj, "__func__", method_obj)
	is_whitelisted(fn)
	is_valid_http_method(fn)

	fnargs = inspect.getfullargspec(method_obj).args

	if not fnargs or (len(fnargs) == 1 and fnargs[0] == "self"):
		response = doc.run_method(method)

	elif "args" in fnargs or not isinstance(args, dict):
		response = doc.run_method(method, args)

	else:
		response = doc.run_method(method, **args)

	finergy.response.docs.append(doc)
	if not response:
		return

	# build output as csv
	if cint(finergy.form_dict.get("as_csv")):
		build_csv_response(response, _(doc.doctype).replace(" ", ""))
		return

	finergy.response["message"] = response


# for backwards compatibility
runserverobj = run_doc_method
