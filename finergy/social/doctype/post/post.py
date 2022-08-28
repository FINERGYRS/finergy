# -*- coding: utf-8 -*-
# Copyright (c) 2018, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import requests
from bs4 import BeautifulSoup

import finergy
from finergy.model.document import Document


class Post(Document):
	def on_update(self):
		if self.is_globally_pinned:
			finergy.publish_realtime("global_pin", after_commit=True)

	def after_insert(self):
		finergy.publish_realtime("new_post", self.owner, after_commit=True)


@finergy.whitelist()
def toggle_like(post_name, user=None):
	liked_by = finergy.db.get_value("Post", post_name, "liked_by")
	liked_by = liked_by.split("\n") if liked_by else []
	user = user or finergy.session.user

	if user in liked_by:
		liked_by.remove(user)
	else:
		liked_by.append(user)

	liked_by = "\n".join(liked_by)
	finergy.db.set_value("Post", post_name, "liked_by", liked_by)
	finergy.publish_realtime("update_liked_by" + post_name, liked_by, after_commit=True)


@finergy.whitelist()
def frequently_visited_links():
	return finergy.get_all(
		"Route History",
		fields=["route", "count(name) as count"],
		filters={"user": finergy.session.user},
		group_by="route",
		order_by="count desc",
		limit=5,
	)


@finergy.whitelist()
def get_link_info(url):
	cached_link_info = finergy.cache().hget("link_info", url)
	if cached_link_info:
		return cached_link_info

	try:
		page = requests.get(url)
	except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
		finergy.cache().hset("link_info", url, {})
		return {}

	soup = BeautifulSoup(page.text)

	meta_obj = {}
	for meta in soup.findAll("meta"):
		meta_name = meta.get("property") or meta.get("name", "").lower()
		if meta_name:
			meta_obj[meta_name] = meta.get("content")

	finergy.cache().hset("link_info", url, meta_obj)

	return meta_obj


@finergy.whitelist()
def delete_post(post_name):
	post = finergy.get_doc("Post", post_name)
	post.delete()
	finergy.publish_realtime("delete_post" + post_name, after_commit=True)


def get_unseen_post_count():
	post_count = finergy.db.count("Post")
	view_post_count = get_viewed_posts(True)

	return post_count - view_post_count


@finergy.whitelist()
def get_posts(filters=None, limit_start=0):
	filters = finergy.utils.get_safe_filters(filters)
	posts = finergy.get_list(
		"Post",
		fields=["name", "content", "owner", "creation", "liked_by", "is_pinned", "is_globally_pinned"],
		filters=filters,
		limit_start=limit_start,
		limit=20,
		order_by="is_globally_pinned desc, creation desc",
	)
	viewed_posts = get_viewed_posts()
	for post in posts:
		post["seen"] = post.name in viewed_posts
	return posts


def get_viewed_posts(only_count=False):
	view_logs = finergy.db.get_all(
		"View Log",
		filters={"reference_doctype": "Post", "viewed_by": finergy.session.user},
		fields=["reference_name"],
	)

	return len(view_logs) if only_count else [log.reference_name for log in view_logs]


@finergy.whitelist()
def set_seen(post_name):
	finergy.get_doc(
		{
			"doctype": "View Log",
			"reference_doctype": "Post",
			"reference_name": post_name,
			"viewed_by": finergy.session.user,
		}
	).insert(ignore_permissions=True)
