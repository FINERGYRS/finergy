# Copyright (c) 2021, Finergy Reporting Solutions SAS and Contributors
# MIT License. See LICENSE
"""
	finergy.coverage
	~~~~~~~~~~~~~~~~

	Coverage settings for finergy
"""

STANDARD_INCLUSIONS = ["*.py"]

STANDARD_EXCLUSIONS = [
	"*.js",
	"*.xml",
	"*.pyc",
	"*.css",
	"*.less",
	"*.scss",
	"*.vue",
	"*.html",
	"*/test_*",
	"*/node_modules/*",
	"*/doctype/*/*_dashboard.py",
	"*/patches/*",
]

FINERGY_EXCLUSIONS = [
	"*/tests/*",
	"*/commands/*",
	"*/finergyrs/change_log/*",
	"*/finergyrs/exceptions*",
	"*finergy/setup.py",
	"*/doctype/*/*_dashboard.py",
	"*/patches/*",
]
