# Copyright (c) 2021, Finergy Reporting Solutions SAS and Contributors
# MIT License. See LICENSE

from finergy.exceptions import ValidationError


class NewsletterAlreadySentError(ValidationError):
	pass


class NoRecipientFoundError(ValidationError):
	pass


class NewsletterNotSavedError(ValidationError):
	pass
