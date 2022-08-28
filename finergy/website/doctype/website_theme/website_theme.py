# Copyright (c) 2015, Finergy Reporting Solutions SAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

from os.path import abspath
from os.path import exists as path_exists
from os.path import join as join_path
from os.path import splitext

import finergy
from finergy import _
from finergy.model.document import Document
from finergy.utils import get_path


class WebsiteTheme(Document):
	def validate(self):
		self.validate_if_customizable()
		self.generate_bootstrap_theme()

	def on_update(self):
		if (
			not self.custom
			and finergy.local.conf.get("developer_mode")
			and not (finergy.flags.in_import or finergy.flags.in_test)
		):

			self.export_doc()

		self.clear_cache_if_current_theme()

	def is_standard_and_not_valid_user(self):
		return (
			not self.custom
			and not finergy.local.conf.get("developer_mode")
			and not (finergy.flags.in_import or finergy.flags.in_test or finergy.flags.in_migrate)
		)

	def on_trash(self):
		if self.is_standard_and_not_valid_user():
			finergy.throw(
				_("You are not allowed to delete a standard Website Theme"), finergy.PermissionError
			)

	def validate_if_customizable(self):
		if self.is_standard_and_not_valid_user():
			finergy.throw(_("Please Duplicate this Website Theme to customize."))

	def export_doc(self):
		"""Export to standard folder `[module]/website_theme/[name]/[name].json`."""
		from finergy.modules.export_file import export_to_files

		export_to_files(record_list=[["Website Theme", self.name]], create_init=True)

	def clear_cache_if_current_theme(self):
		if finergy.flags.in_install == "finergy":
			return
		website_settings = finergy.get_doc("Website Settings", "Website Settings")
		if getattr(website_settings, "website_theme", None) == self.name:
			website_settings.clear_cache()

	def generate_bootstrap_theme(self):
		from subprocess import PIPE, Popen

		self.theme_scss = finergy.render_template(
			"finergy/website/doctype/website_theme/website_theme_template.scss", self.as_dict()
		)

		# create theme file in site public files folder
		folder_path = abspath(finergy.utils.get_files_path("website_theme", is_private=False))
		# create folder if not exist
		finergy.create_folder(folder_path)

		if self.custom:
			self.delete_old_theme_files(folder_path)

		# add a random suffix
		suffix = finergy.generate_hash("Website Theme", 8) if self.custom else "style"
		file_name = finergy.scrub(self.name) + "_" + suffix + ".css"
		output_path = join_path(folder_path, file_name)

		self.theme_scss = content = get_scss(self)
		content = content.replace("\n", "\\n")
		command = ["node", "generate_bootstrap_theme.js", output_path, content]

		process = Popen(command, cwd=finergy.get_app_path("finergy", ".."), stdout=PIPE, stderr=PIPE)

		stderr = process.communicate()[1]

		if stderr:
			stderr = finergy.safe_decode(stderr)
			stderr = stderr.replace("\n", "<br>")
			finergy.throw('<div style="font-family: monospace;">{stderr}</div>'.format(stderr=stderr))
		else:
			self.theme_url = "/files/website_theme/" + file_name

		finergy.msgprint(_("Compiled Successfully"), alert=True)

	def delete_old_theme_files(self, folder_path):
		import os

		for fname in os.listdir(folder_path):
			if fname.startswith(finergy.scrub(self.name) + "_") and fname.endswith(".css"):
				os.remove(os.path.join(folder_path, fname))

	def generate_theme_if_not_exist(self):
		bench_path = finergy.utils.get_bench_path()
		if self.theme_url:
			theme_path = join_path(bench_path, "sites", self.theme_url[1:])
			if not path_exists(theme_path):
				self.generate_bootstrap_theme()
		else:
			self.generate_bootstrap_theme()

	@finergy.whitelist()
	def set_as_default(self):
		self.generate_bootstrap_theme()
		self.save()
		website_settings = finergy.get_doc("Website Settings")
		website_settings.website_theme = self.name
		website_settings.ignore_validate = True
		website_settings.save()

	@finergy.whitelist()
	def get_apps(self):
		from finergy.utils.change_log import get_versions

		apps = get_versions()
		out = []
		for app, values in apps.items():
			out.append({"name": app, "title": values["title"]})
		return out


def add_website_theme(context):
	context.theme = finergy._dict()

	if not context.disable_website_theme:
		website_theme = get_active_theme()
		context.theme = website_theme or finergy._dict()


def get_active_theme():
	website_theme = finergy.db.get_single_value("Website Settings", "website_theme")
	if website_theme:
		try:
			return finergy.get_doc("Website Theme", website_theme)
		except finergy.DoesNotExistError:
			pass


def get_scss(website_theme):
	"""
	Render `website_theme_template.scss` with the values defined in Website Theme.

	params:
	website_theme - instance of a Website Theme
	"""
	apps_to_ignore = tuple((d.app + "/") for d in website_theme.ignored_apps)
	available_imports = get_scss_paths()
	imports_to_include = [d for d in available_imports if not d.startswith(apps_to_ignore)]
	context = website_theme.as_dict()
	context["website_theme_scss"] = imports_to_include
	return finergy.render_template(
		"finergy/website/doctype/website_theme/website_theme_template.scss", context
	)


def get_scss_paths():
	"""
	Return a set of SCSS import paths from all apps that provide `website.scss`.

	If `$BENCH_PATH/apps/finergyrs/finergy/public/scss/website.scss` exists, the
	returned set will contain 'finergy/public/scss/website'.
	"""
	import_path_list = []
	bench_path = finergy.utils.get_bench_path()

	for app in finergy.get_installed_apps():
		relative_path = join_path(app, "public/scss/website.scss")
		full_path = get_path("apps", app, relative_path, base=bench_path)
		if path_exists(full_path):
			import_path = splitext(relative_path)[0]
			import_path_list.append(import_path)

	return import_path_list


def after_migrate():
	"""
	Regenerate Active Theme CSS file after migration.

	Necessary to reflect possible changes in the imported SCSS files. Called at
	the end of every `bench migrate`.
	"""
	website_theme = finergy.db.get_single_value("Website Settings", "website_theme")
	if not website_theme or website_theme == "Standard":
		return

	doc = finergy.get_doc("Website Theme", website_theme)
	doc.generate_bootstrap_theme()
	doc.save()
