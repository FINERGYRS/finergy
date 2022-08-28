# imports - standard imports
import sys

# imports - module imports
from finergy.integrations.finergy_providers.finergycloud import finergycloud_migrator


def migrate_to(local_site, finergy_provider):
	if finergy_provider in ("finergy.cloud", "finergycloud.com"):
		return finergycloud_migrator(local_site)
	else:
		print("{} is not supported yet".format(finergy_provider))
		sys.exit(1)
