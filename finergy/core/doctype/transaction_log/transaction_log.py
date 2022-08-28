# -*- coding: utf-8 -*-
# Copyright (c) 2018, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import hashlib

import finergy
from finergy import _
from finergy.model.document import Document
from finergy.utils import cint, now_datetime


class TransactionLog(Document):
	def before_insert(self):
		index = get_current_index()
		self.row_index = index
		self.timestamp = now_datetime()
		if index != 1:
			prev_hash = finergy.db.sql(
				"SELECT `chaining_hash` FROM `tabTransaction Log` WHERE `row_index` = '{0}'".format(index - 1)
			)
			if prev_hash:
				self.previous_hash = prev_hash[0][0]
			else:
				self.previous_hash = "Indexing broken"
		else:
			self.previous_hash = self.hash_line()
		self.transaction_hash = self.hash_line()
		self.chaining_hash = self.hash_chain()
		self.checksum_version = "v1.0.1"

	def hash_line(self):
		sha = hashlib.sha256()
		sha.update(
			finergy.safe_encode(str(self.row_index))
			+ finergy.safe_encode(str(self.timestamp))
			+ finergy.safe_encode(str(self.data))
		)
		return sha.hexdigest()

	def hash_chain(self):
		sha = hashlib.sha256()
		sha.update(
			finergy.safe_encode(str(self.transaction_hash)) + finergy.safe_encode(str(self.previous_hash))
		)
		return sha.hexdigest()


def get_current_index():
	current = finergy.db.sql(
		"""SELECT `current`
		FROM `tabSeries`
		WHERE `name` = 'TRANSACTLOG'
		FOR UPDATE"""
	)
	if current and current[0][0] is not None:
		current = current[0][0]

		finergy.db.sql(
			"""UPDATE `tabSeries`
			SET `current` = `current` + 1
			where `name` = 'TRANSACTLOG'"""
		)
		current = cint(current) + 1
	else:
		finergy.db.sql("INSERT INTO `tabSeries` (name, current) VALUES ('TRANSACTLOG', 1)")
		current = 1
	return current
