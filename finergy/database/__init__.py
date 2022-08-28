# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

# Database Module
# --------------------

from __future__ import unicode_literals


def setup_database(force, source_sql=None, verbose=None, no_mariadb_socket=False):
	import finergy

	if finergy.conf.db_type == "postgres":
		import finergy.database.postgres.setup_db

		return finergy.database.postgres.setup_db.setup_database(force, source_sql, verbose)
	else:
		import finergy.database.mariadb.setup_db

		return finergy.database.mariadb.setup_db.setup_database(
			force, source_sql, verbose, no_mariadb_socket=no_mariadb_socket
		)


def drop_user_and_database(db_name, root_login=None, root_password=None):
	import finergy

	if finergy.conf.db_type == "postgres":
		pass
	else:
		import finergy.database.mariadb.setup_db

		return finergy.database.mariadb.setup_db.drop_user_and_database(
			db_name, root_login, root_password
		)


def get_db(host=None, user=None, password=None, port=None):
	import finergy

	if finergy.conf.db_type == "postgres":
		import finergy.database.postgres.database

		return finergy.database.postgres.database.PostgresDatabase(host, user, password, port=port)
	else:
		import finergy.database.mariadb.database

		return finergy.database.mariadb.database.MariaDBDatabase(host, user, password, port=port)


def setup_help_database(help_db_name):
	import finergy

	if finergy.conf.db_type == "postgres":
		import finergy.database.postgres.setup_db

		return finergy.database.postgres.setup_db.setup_help_database(help_db_name)
	else:
		import finergy.database.mariadb.setup_db

		return finergy.database.mariadb.setup_db.setup_help_database(help_db_name)
