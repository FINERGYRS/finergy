# Copyright (c) 2021, Finergy Technologies and Contributors
# See license.txt

import unittest

import finergy


class TestFeedback(unittest.TestCase):
	def tearDown(self):
		finergy.form_dict.reference_doctype = None
		finergy.form_dict.reference_name = None
		finergy.form_dict.rating = None
		finergy.form_dict.feedback = None
		finergy.local.request_ip = None

	def test_feedback_creation_updation(self):
		from finergy.website.doctype.blog_post.test_blog_post import make_test_blog

		test_blog = make_test_blog()

		finergy.db.sql("delete from `tabFeedback` where reference_doctype = 'Blog Post'")

		from finergy.templates.includes.feedback.feedback import add_feedback, update_feedback

		finergy.form_dict.reference_doctype = "Blog Post"
		finergy.form_dict.reference_name = test_blog.name
		finergy.form_dict.rating = 5
		finergy.form_dict.feedback = "New feedback"
		finergy.local.request_ip = "127.0.0.1"

		feedback = add_feedback()

		self.assertEqual(feedback.feedback, "New feedback")
		self.assertEqual(feedback.rating, 5)

		updated_feedback = update_feedback("Blog Post", test_blog.name, 6, "Updated feedback")

		self.assertEqual(updated_feedback.feedback, "Updated feedback")
		self.assertEqual(updated_feedback.rating, 6)

		finergy.db.sql("delete from `tabFeedback` where reference_doctype = 'Blog Post'")

		test_blog.delete()
