from __future__ import print_function, unicode_literals

"""
Check for unused CSS Classes

sUpdate source and target apps below and run from CLI

	bench --site [sitename] execute finergy.website.purifycss.purify.css

"""

import os
import re

import finergy

source = finergy.get_app_path("finergy_theme", "public", "less", "finergy_theme.less")
target_apps = [
	"capkpi_com",
	"finergy_io",
	"translator",
	"chart_of_accounts_builder",
	"finergy_theme",
]


def purifycss():
	with open(source, "r") as f:
		src = f.read()

	classes = []
	for line in src.splitlines():
		line = line.strip()
		if not line:
			continue
		if line[0] == "@":
			continue
		classes.extend(re.findall("\.([^0-9][^ :&.{,(]*)", line))

	classes = list(set(classes))

	for app in target_apps:
		for basepath, folders, files in os.walk(finergy.get_app_path(app)):
			for fname in files:
				if fname.endswith(".html") or fname.endswith(".md"):
					# print 'checking {0}...'.format(fname)
					with open(os.path.join(basepath, fname), "r") as f:
						src = f.read()
					for c in classes:
						if c in src:
							classes.remove(c)

	for c in sorted(classes):
		print(c)
