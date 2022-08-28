import finergy


def execute():
	finergy.db.change_column_type(table="__Auth", column="password", type="TEXT")
