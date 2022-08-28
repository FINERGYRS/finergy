from __future__ import absolute_import, print_function, unicode_literals

import click

from finergy.commands import get_site, pass_context
from finergy.exceptions import SiteNotSpecifiedError


# translation
@click.command("build-message-files")
@pass_context
def build_message_files(context):
	"Build message files for translation"
	import finergy.translate

	for site in context.sites:
		try:
			finergy.init(site=site)
			finergy.connect()
			finergy.translate.rebuild_all_translation_files()
		finally:
			finergy.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


@click.command("new-language")  # , help="Create lang-code.csv for given app")
@pass_context
@click.argument("lang_code")  # , help="Language code eg. en")
@click.argument("app")  # , help="App name eg. finergy")
def new_language(context, lang_code, app):
	"""Create lang-code.csv for given app"""
	import finergy.translate

	if not context["sites"]:
		raise Exception("--site is required")

	# init site
	finergy.connect(site=context["sites"][0])
	finergy.translate.write_translations_file(app, lang_code)

	print(
		"File created at ./apps/{app}/{app}/translations/{lang_code}.csv".format(
			app=app, lang_code=lang_code
		)
	)
	print(
		"You will need to add the language in finergy/geo/languages.json, if you haven't done it already."
	)


@click.command("get-untranslated")
@click.argument("lang")
@click.argument("untranslated_file")
@click.option("--all", default=False, is_flag=True, help="Get all message strings")
@pass_context
def get_untranslated(context, lang, untranslated_file, all=None):
	"Get untranslated strings for language"
	import finergy.translate

	site = get_site(context)
	try:
		finergy.init(site=site)
		finergy.connect()
		finergy.translate.get_untranslated(lang, untranslated_file, get_all=all)
	finally:
		finergy.destroy()


@click.command("update-translations")
@click.argument("lang")
@click.argument("untranslated_file")
@click.argument("translated-file")
@pass_context
def update_translations(context, lang, untranslated_file, translated_file):
	"Update translated strings"
	import finergy.translate

	site = get_site(context)
	try:
		finergy.init(site=site)
		finergy.connect()
		finergy.translate.update_translations(lang, untranslated_file, translated_file)
	finally:
		finergy.destroy()


@click.command("import-translations")
@click.argument("lang")
@click.argument("path")
@pass_context
def import_translations(context, lang, path):
	"Update translated strings"
	import finergy.translate

	site = get_site(context)
	try:
		finergy.init(site=site)
		finergy.connect()
		finergy.translate.import_translations(lang, path)
	finally:
		finergy.destroy()


commands = [
	build_message_files,
	get_untranslated,
	import_translations,
	new_language,
	update_translations,
]
