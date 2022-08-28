# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# License: See license.txt

from __future__ import unicode_literals

import finergy
from finergy import _, throw
from finergy.model.document import Document


class Currency(Document):
	def validate(self):
		if not finergy.flags.in_install_app:
			finergy.clear_cache()
