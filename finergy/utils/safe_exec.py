import copy
import inspect
import json
import mimetypes

import RestrictedPython.Guards
from html2text import html2text
from RestrictedPython import compile_restricted, safe_globals

import finergy
import finergy.exceptions
import finergy.integrations.utils
import finergy.utils
import finergy.utils.data
from finergy import _
from finergy.finergyclient import FinergyClient
from finergy.handler import execute_cmd
from finergy.modules import scrub
from finergy.utils.background_jobs import enqueue, get_jobs
from finergy.website.utils import get_next_link, get_shade, get_toc
from finergy.www.printview import get_visible_columns


class ServerScriptNotEnabled(finergy.PermissionError):
	pass


class NamespaceDict(finergy._dict):
	"""Raise AttributeError if function not found in namespace"""

	def __getattr__(self, key):
		ret = self.get(key)
		if (not ret and key.startswith("__")) or (key not in self):

			def default_function(*args, **kwargs):
				raise AttributeError(f"module has no attribute '{key}'")

			return default_function
		return ret


def safe_exec(script, _globals=None, _locals=None, restrict_commit_rollback=False):
	# server scripts can be disabled via site_config.json
	# they are enabled by default
	if "server_script_enabled" in finergy.conf:
		enabled = finergy.conf.server_script_enabled
	else:
		enabled = True

	if not enabled:
		finergy.throw(_("Please Enable Server Scripts"), ServerScriptNotEnabled)

	# build globals
	exec_globals = get_safe_globals()
	if _globals:
		exec_globals.update(_globals)

	if restrict_commit_rollback:
		exec_globals.finergy.db.pop("commit", None)
		exec_globals.finergy.db.pop("rollback", None)

	# execute script compiled by RestrictedPython
	finergy.flags.in_safe_exec = True
	exec(compile_restricted(script), exec_globals, _locals)  # pylint: disable=exec-used
	finergy.flags.in_safe_exec = False

	return exec_globals, _locals


def get_safe_globals():
	datautils = finergy._dict()
	if finergy.db:
		date_format = finergy.db.get_default("date_format") or "yyyy-mm-dd"
		time_format = finergy.db.get_default("time_format") or "HH:mm:ss"
	else:
		date_format = "yyyy-mm-dd"
		time_format = "HH:mm:ss"

	add_data_utils(datautils)

	form_dict = getattr(finergy.local, "form_dict", finergy._dict())

	if "_" in form_dict:
		del finergy.local.form_dict["_"]

	user = getattr(finergy.local, "session", None) and finergy.local.session.user or "Guest"

	out = NamespaceDict(
		# make available limited methods of finergy
		json=NamespaceDict(loads=json.loads, dumps=json.dumps),
		dict=dict,
		log=finergy.log,
		_dict=finergy._dict,
		args=form_dict,
		finergy=NamespaceDict(
			call=call_whitelisted_function,
			flags=finergy._dict(),
			format=finergy.format_value,
			format_value=finergy.format_value,
			date_format=date_format,
			time_format=time_format,
			format_date=finergy.utils.data.global_date_format,
			form_dict=form_dict,
			bold=finergy.bold,
			copy_doc=finergy.copy_doc,
			errprint=finergy.errprint,
			qb=finergy.qb,
			get_meta=finergy.get_meta,
			get_doc=finergy.get_doc,
			get_cached_doc=finergy.get_cached_doc,
			get_list=finergy.get_list,
			get_all=finergy.get_all,
			get_system_settings=finergy.get_system_settings,
			rename_doc=finergy.rename_doc,
			utils=datautils,
			get_url=finergy.utils.get_url,
			render_template=finergy.render_template,
			msgprint=finergy.msgprint,
			throw=finergy.throw,
			sendmail=finergy.sendmail,
			get_print=finergy.get_print,
			attach_print=finergy.attach_print,
			user=user,
			get_fullname=finergy.utils.get_fullname,
			get_gravatar=finergy.utils.get_gravatar_url,
			full_name=finergy.local.session.data.full_name
			if getattr(finergy.local, "session", None)
			else "Guest",
			request=getattr(finergy.local, "request", {}),
			session=finergy._dict(
				user=user,
				csrf_token=finergy.local.session.data.csrf_token
				if getattr(finergy.local, "session", None)
				else "",
			),
			make_get_request=finergy.integrations.utils.make_get_request,
			make_post_request=finergy.integrations.utils.make_post_request,
			get_payment_gateway_controller=finergy.integrations.utils.get_payment_gateway_controller,
			socketio_port=finergy.conf.socketio_port,
			get_hooks=get_hooks,
			enqueue=safe_enqueue,
			sanitize_html=finergy.utils.sanitize_html,
			log_error=finergy.log_error,
		),
		FinergyClient=FinergyClient,
		style=finergy._dict(border_color="#d1d8dd"),
		get_toc=get_toc,
		get_next_link=get_next_link,
		_=finergy._,
		get_shade=get_shade,
		scrub=scrub,
		guess_mimetype=mimetypes.guess_type,
		html2text=html2text,
		dev_server=finergy.local.dev_server,
		run_script=run_script,
		is_job_queued=is_job_queued,
	)

	add_module_properties(
		finergy.exceptions, out.finergy, lambda obj: inspect.isclass(obj) and issubclass(obj, Exception)
	)

	if not finergy.flags.in_setup_help:
		out.get_visible_columns = get_visible_columns
		out.finergy.date_format = date_format
		out.finergy.time_format = time_format
		out.finergy.db = NamespaceDict(
			get_list=finergy.get_list,
			get_all=finergy.get_all,
			get_value=finergy.db.get_value,
			set_value=finergy.db.set_value,
			get_single_value=finergy.db.get_single_value,
			get_default=finergy.db.get_default,
			exists=finergy.db.exists,
			count=finergy.db.count,
			escape=finergy.db.escape,
			sql=read_sql,
			commit=finergy.db.commit,
			rollback=finergy.db.rollback,
		)

	if finergy.response:
		out.finergy.response = finergy.response

	out.update(safe_globals)

	# default writer allows write access
	out._write_ = _write
	out._getitem_ = _getitem
	out._getattr_ = _getattr

	# allow iterators and list comprehension
	out._getiter_ = iter
	out._iter_unpack_sequence_ = RestrictedPython.Guards.guarded_iter_unpack_sequence
	out.sorted = sorted

	return out


def is_job_queued(job_name, queue="default"):
	"""
	:param job_name: used to identify a queued job, usually dotted path to function
	:param queue: should be either long, default or short
	"""

	site = finergy.local.site
	queued_jobs = get_jobs(site=site, queue=queue, key="job_name").get(site)
	return queued_jobs and job_name in queued_jobs


def safe_enqueue(function, **kwargs):
	"""
	Enqueue function to be executed using a background worker
	Accepts finergy.enqueue params like job_name, queue, timeout, etc.
	in addition to params to be passed to function

	:param function: whitelised function or API Method set in Server Script
	"""

	return enqueue("finergy.utils.safe_exec.call_whitelisted_function", function=function, **kwargs)


def call_whitelisted_function(function, **kwargs):
	"""Executes a whitelisted function or Server Script of type API"""

	return call_with_form_dict(lambda: execute_cmd(function), kwargs)


def run_script(script, **kwargs):
	"""run another server script"""

	return call_with_form_dict(
		lambda: finergy.get_doc("Server Script", script).execute_method(), kwargs
	)


def call_with_form_dict(function, kwargs):
	# temporarily update form_dict, to use inside below call
	form_dict = getattr(finergy.local, "form_dict", finergy._dict())
	if kwargs:
		finergy.local.form_dict = form_dict.copy().update(kwargs)

	try:
		return function()
	finally:
		finergy.local.form_dict = form_dict


def get_hooks(hook=None, default=None, app_name=None):
	hooks = finergy.get_hooks(hook=hook, default=default, app_name=app_name)
	return copy.deepcopy(hooks)


def read_sql(query, *args, **kwargs):
	"""a wrapper for finergy.db.sql to allow reads"""
	query = str(query)
	if finergy.flags.in_safe_exec and not query.strip().lower().startswith("select"):
		raise finergy.PermissionError("Only SELECT SQL allowed in scripting")
	return finergy.db.sql(query, *args, **kwargs)


def _getitem(obj, key):
	# guard function for RestrictedPython
	# allow any key to be accessed as long as it does not start with underscore
	if isinstance(key, str) and key.startswith("_"):
		raise SyntaxError("Key starts with _")
	return obj[key]


def _getattr(object, name, default=None):
	# guard function for RestrictedPython
	# allow any key to be accessed as long as
	# 1. it does not start with an underscore (safer_getattr)
	# 2. it is not an UNSAFE_ATTRIBUTES

	UNSAFE_ATTRIBUTES = {
		# Generator Attributes
		"gi_frame",
		"gi_code",
		# Coroutine Attributes
		"cr_frame",
		"cr_code",
		"cr_origin",
		# Async Generator Attributes
		"ag_code",
		"ag_frame",
		# Traceback Attributes
		"tb_frame",
		"tb_next",
	}

	if isinstance(name, str) and (name in UNSAFE_ATTRIBUTES):
		raise SyntaxError("{name} is an unsafe attribute".format(name=name))
	return RestrictedPython.Guards.safer_getattr(object, name, default=default)


def _write(obj):
	# guard function for RestrictedPython
	# allow writing to any object
	return obj


def add_data_utils(data):
	for key, obj in finergy.utils.data.__dict__.items():
		if key in VALID_UTILS:
			data[key] = obj


def add_module_properties(module, data, filter_method):
	for key, obj in module.__dict__.items():
		if key.startswith("_"):
			# ignore
			continue

		if filter_method(obj):
			# only allow functions
			data[key] = obj


VALID_UTILS = (
	"DATE_FORMAT",
	"TIME_FORMAT",
	"DATETIME_FORMAT",
	"is_invalid_date_string",
	"getdate",
	"get_datetime",
	"to_timedelta",
	"get_timedelta",
	"add_to_date",
	"add_days",
	"add_months",
	"add_years",
	"date_diff",
	"month_diff",
	"time_diff",
	"time_diff_in_seconds",
	"time_diff_in_hours",
	"now_datetime",
	"get_timestamp",
	"get_eta",
	"get_time_zone",
	"convert_utc_to_user_timezone",
	"now",
	"nowdate",
	"today",
	"nowtime",
	"get_first_day",
	"get_quarter_start",
	"get_first_day_of_week",
	"get_year_start",
	"get_last_day_of_week",
	"get_last_day",
	"get_time",
	"get_datetime_in_timezone",
	"get_datetime_str",
	"get_date_str",
	"get_time_str",
	"get_user_date_format",
	"get_user_time_format",
	"format_date",
	"format_time",
	"format_datetime",
	"format_duration",
	"get_weekdays",
	"get_weekday",
	"get_timespan_date_range",
	"global_date_format",
	"has_common",
	"flt",
	"cint",
	"floor",
	"ceil",
	"cstr",
	"rounded",
	"remainder",
	"safe_div",
	"round_based_on_smallest_currency_fraction",
	"encode",
	"parse_val",
	"fmt_money",
	"get_number_format_info",
	"money_in_words",
	"in_words",
	"is_html",
	"is_image",
	"get_thumbnail_base64_for_image",
	"image_to_base64",
	"pdf_to_base64",
	"strip_html",
	"escape_html",
	"pretty_date",
	"comma_or",
	"comma_and",
	"comma_sep",
	"new_line_sep",
	"filter_strip_join",
	"get_url",
	"get_host_name_from_request",
	"url_contains_port",
	"get_host_name",
	"get_link_to_form",
	"get_link_to_report",
	"get_absolute_url",
	"get_url_to_form",
	"get_url_to_list",
	"get_url_to_report",
	"get_url_to_report_with_filters",
	"evaluate_filters",
	"compare",
	"get_filter",
	"make_filter_tuple",
	"make_filter_dict",
	"sanitize_column",
	"scrub_urls",
	"expand_relative_urls",
	"quoted",
	"quote_urls",
	"unique",
	"strip",
	"to_markdown",
	"md_to_html",
	"markdown",
	"is_subset",
	"generate_hash",
	"formatdate",
	"get_user_info_for_avatar",
	"get_abbr",
)
