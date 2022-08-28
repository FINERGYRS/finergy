import click

import finergy


def execute():
	finergy.delete_doc_if_exists("DocType", "Chat Message")
	finergy.delete_doc_if_exists("DocType", "Chat Message Attachment")
	finergy.delete_doc_if_exists("DocType", "Chat Profile")
	finergy.delete_doc_if_exists("DocType", "Chat Token")
	finergy.delete_doc_if_exists("DocType", "Chat Room User")
	finergy.delete_doc_if_exists("DocType", "Chat Room")
	finergy.delete_doc_if_exists("Module Def", "Chat")

	click.secho(
		"Chat Module is moved to a separate app and is removed from Finergy in version-13.\n"
		"Please install the app to continue using the chat feature: https://github.com/finergyrs/chat",
		fg="yellow",
	)
