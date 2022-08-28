# -*- coding: utf-8 -*-
# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import logging
import os

from six import iteritems
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.local import LocalManager
from werkzeug.middleware.profiler import ProfilerMiddleware
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.wrappers import Request, Response

import finergy
import finergy.api
import finergy.auth
import finergy.handler
import finergy.monitor
import finergy.rate_limiter
import finergy.recorder
import finergy.utils.response
import finergy.website.render
from finergy import _
from finergy.core.doctype.comment.comment import update_comments_in_parent_after_request
from finergy.middlewares import StaticDataMiddleware
from finergy.utils import get_site_name, sanitize_html
from finergy.utils.error import make_error_snapshot

local_manager = LocalManager([finergy.local])

_site = None
_sites_path = os.environ.get("SITES_PATH", ".")


class RequestContext(object):
	def __init__(self, environ):
		self.request = Request(environ)

	def __enter__(self):
		init_request(self.request)

	def __exit__(self, type, value, traceback):
		finergy.destroy()


@Request.application
def application(request):
	response = None

	try:
		rollback = True

		init_request(request)

		finergy.recorder.record()
		finergy.monitor.start()
		finergy.rate_limiter.apply()
		finergy.api.validate_auth()

		if request.method == "OPTIONS":
			response = Response()

		elif finergy.form_dict.cmd:
			response = finergy.handler.handle()

		elif request.path.startswith("/api/"):
			response = finergy.api.handle()

		elif request.path.startswith("/backups"):
			response = finergy.utils.response.download_backup(request.path)

		elif request.path.startswith("/private/files/"):
			response = finergy.utils.response.download_private_file(request.path)

		elif request.method in ("GET", "HEAD", "POST"):
			response = finergy.website.render.render()

		else:
			raise NotFound

	except HTTPException as e:
		return e

	except finergy.SessionStopped as e:
		response = finergy.utils.response.handle_session_stopped()

	except Exception as e:
		response = handle_exception(e)

	else:
		rollback = after_request(rollback)

	finally:
		if request.method in ("POST", "PUT") and finergy.db and rollback:
			finergy.db.rollback()

		finergy.rate_limiter.update()
		finergy.monitor.stop(response)
		finergy.recorder.dump()

		log_request(request, response)
		process_response(response)
		finergy.destroy()

	return response


def init_request(request):
	finergy.local.request = request
	finergy.local.is_ajax = finergy.get_request_header("X-Requested-With") == "XMLHttpRequest"

	site = _site or request.headers.get("X-Finergy-Site-Name") or get_site_name(request.host)
	finergy.init(site=site, sites_path=_sites_path)

	if not (finergy.local.conf and finergy.local.conf.db_name):
		# site does not exist
		raise NotFound

	if finergy.local.conf.get("maintenance_mode"):
		finergy.connect()
		raise finergy.SessionStopped("Session Stopped")
	else:
		finergy.connect(set_admin_as_user=False)

	make_form_dict(request)

	if request.method != "OPTIONS":
		finergy.local.http_request = finergy.auth.HTTPRequest()


def log_request(request, response):
	if hasattr(finergy.local, "conf") and finergy.local.conf.enable_finergy_logger:
		finergy.logger("finergy.web", allow_site=finergy.local.site).info(
			{
				"site": get_site_name(request.host),
				"remote_addr": getattr(request, "remote_addr", "NOTFOUND"),
				"base_url": getattr(request, "base_url", "NOTFOUND"),
				"full_path": getattr(request, "full_path", "NOTFOUND"),
				"method": getattr(request, "method", "NOTFOUND"),
				"scheme": getattr(request, "scheme", "NOTFOUND"),
				"http_status_code": getattr(response, "status_code", "NOTFOUND"),
			}
		)


def process_response(response):
	if not response:
		return

	# set cookies
	if hasattr(finergy.local, "cookie_manager"):
		finergy.local.cookie_manager.flush_cookies(response=response)

	# rate limiter headers
	if hasattr(finergy.local, "rate_limiter"):
		response.headers.extend(finergy.local.rate_limiter.headers())

	# CORS headers
	if hasattr(finergy.local, "conf") and finergy.conf.allow_cors:
		set_cors_headers(response)


def set_cors_headers(response):
	origin = finergy.request.headers.get("Origin")
	allow_cors = finergy.conf.allow_cors
	if not (origin and allow_cors):
		return

	if allow_cors != "*":
		if not isinstance(allow_cors, list):
			allow_cors = [allow_cors]

		if origin not in allow_cors:
			return

	response.headers.extend(
		{
			"Access-Control-Allow-Origin": origin,
			"Access-Control-Allow-Credentials": "true",
			"Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
			"Access-Control-Allow-Headers": (
				"Authorization,DNT,X-Mx-ReqToken,"
				"Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,"
				"Cache-Control,Content-Type"
			),
		}
	)


def make_form_dict(request):
	import json

	request_data = request.get_data(as_text=True)
	if "application/json" in (request.content_type or "") and request_data:
		args = json.loads(request_data)
	else:
		args = {}
		args.update(request.args or {})
		args.update(request.form or {})

	if not isinstance(args, dict):
		finergy.throw("Invalid request arguments")

	try:
		finergy.local.form_dict = finergy._dict(
			{k: v[0] if isinstance(v, (list, tuple)) else v for k, v in iteritems(args)}
		)
	except IndexError:
		finergy.local.form_dict = finergy._dict(args)

	if "_" in finergy.local.form_dict:
		# _ is passed by $.ajax so that the request is not cached by the browser. So, remove _ from form_dict
		finergy.local.form_dict.pop("_")


def handle_exception(e):
	response = None
	http_status_code = getattr(e, "http_status_code", 500)
	return_as_message = False
	accept_header = finergy.get_request_header("Accept") or ""
	respond_as_json = (
		finergy.get_request_header("Accept")
		and (finergy.local.is_ajax or "application/json" in accept_header)
		or (finergy.local.request.path.startswith("/api/") and not accept_header.startswith("text"))
	)

	if respond_as_json:
		# handle ajax responses first
		# if the request is ajax, send back the trace or error message
		response = finergy.utils.response.report_error(http_status_code)

	elif (
		http_status_code == 500
		and (finergy.db and isinstance(e, finergy.db.InternalError))
		and (finergy.db and (finergy.db.is_deadlocked(e) or finergy.db.is_timedout(e)))
	):
		http_status_code = 508

	elif http_status_code == 401:
		finergy.respond_as_web_page(
			_("Session Expired"),
			_("Your session has expired, please login again to continue."),
			http_status_code=http_status_code,
			indicator_color="red",
		)
		return_as_message = True

	elif http_status_code == 403:
		finergy.respond_as_web_page(
			_("Not Permitted"),
			_("You do not have enough permissions to complete the action"),
			http_status_code=http_status_code,
			indicator_color="red",
		)
		return_as_message = True

	elif http_status_code == 404:
		finergy.respond_as_web_page(
			_("Not Found"),
			_("The resource you are looking for is not available"),
			http_status_code=http_status_code,
			indicator_color="red",
		)
		return_as_message = True

	elif http_status_code == 429:
		response = finergy.rate_limiter.respond()

	else:
		traceback = "<pre>" + sanitize_html(finergy.get_traceback()) + "</pre>"
		# disable traceback in production if flag is set
		if finergy.local.flags.disable_traceback and not finergy.local.dev_server:
			traceback = ""

		finergy.respond_as_web_page(
			"Server Error", traceback, http_status_code=http_status_code, indicator_color="red", width=640
		)
		return_as_message = True

	if e.__class__ == finergy.AuthenticationError:
		if hasattr(finergy.local, "login_manager"):
			finergy.local.login_manager.clear_cookies()

	if http_status_code >= 500:
		make_error_snapshot(e)

	if return_as_message:
		response = finergy.website.render.render("message", http_status_code=http_status_code)

	if finergy.conf.get("developer_mode") and not respond_as_json:
		# don't fail silently for non-json response errors
		print(finergy.get_traceback())

	return response


def after_request(rollback):
	if (finergy.local.request.method in ("POST", "PUT") or finergy.local.flags.commit) and finergy.db:
		if finergy.db.transaction_writes:
			finergy.db.commit()
			rollback = False

	# update session
	if getattr(finergy.local, "session_obj", None):
		updated_in_db = finergy.local.session_obj.update()
		if updated_in_db:
			finergy.db.commit()
			rollback = False

	update_comments_in_parent_after_request()

	return rollback


application = local_manager.make_middleware(application)


def serve(
	port=8000, profile=False, no_reload=False, no_threading=False, site=None, sites_path="."
):
	global application, _site, _sites_path
	_site = site
	_sites_path = sites_path

	from werkzeug.serving import run_simple

	patch_werkzeug_reloader()

	if profile:
		application = ProfilerMiddleware(application, sort_by=("cumtime", "calls"))

	if not os.environ.get("NO_STATICS"):
		application = SharedDataMiddleware(
			application, {str("/assets"): str(os.path.join(sites_path, "assets"))}
		)

		application = StaticDataMiddleware(
			application, {str("/files"): str(os.path.abspath(sites_path))}
		)

	application.debug = True
	application.config = {"SERVER_NAME": "localhost:8000"}

	log = logging.getLogger("werkzeug")
	log.propagate = False

	in_test_env = os.environ.get("CI")
	if in_test_env:
		log.setLevel(logging.ERROR)

	run_simple(
		"0.0.0.0",
		int(port),
		application,
		use_reloader=False if in_test_env else not no_reload,
		use_debugger=not in_test_env,
		use_evalex=not in_test_env,
		threaded=not no_threading,
	)


def patch_werkzeug_reloader():
	"""
	This function monkey patches Werkzeug reloader to ignore reloading files in
	the __pycache__ directory.

	To be deprecated when upgrading to Werkzeug 2.
	"""

	from werkzeug._reloader import WatchdogReloaderLoop

	trigger_reload = WatchdogReloaderLoop.trigger_reload

	def custom_trigger_reload(self, filename):
		if os.path.basename(os.path.dirname(filename)) == "__pycache__":
			return

		return trigger_reload(self, filename)

	WatchdogReloaderLoop.trigger_reload = custom_trigger_reload
