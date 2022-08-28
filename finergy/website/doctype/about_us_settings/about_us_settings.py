# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy.model.document import Document


class AboutUsSettings(Document):
	def on_update(self):
		from finergy.website.render import clear_cache

		clear_cache("about")


def get_args():
	obj = finergy.get_doc("About Us Settings")
	return {"obj": obj}
