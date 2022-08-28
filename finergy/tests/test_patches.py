from __future__ import unicode_literals

import unittest

import finergy
from finergy.modules import patch_handler


class TestPatches(unittest.TestCase):
	def test_patch_module_names(self):
		finergy.flags.final_patches = []
		finergy.flags.in_install = True
		for patchmodule in patch_handler.get_all_patches():
			if patchmodule.startswith("execute:"):
				pass
			else:
				if patchmodule.startswith("finally:"):
					patchmodule = patchmodule.split("finally:")[-1]
				self.assertTrue(finergy.get_attr(patchmodule.split()[0] + ".execute"))

		finergy.flags.in_install = False
