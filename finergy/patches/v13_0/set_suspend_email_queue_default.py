import finergy
from finergy.cache_manager import clear_defaults_cache


def execute():
	finergy.db.set_default(
		"suspend_email_queue",
		finergy.db.get_default("hold_queue", "Administrator") or 0,
		parent="__default",
	)

	finergy.db.delete("DefaultValue", {"defkey": "hold_queue"})
	clear_defaults_cache()
