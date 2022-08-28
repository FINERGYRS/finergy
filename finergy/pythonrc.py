#!/usr/bin/env python2.7

# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import os

import finergy

finergy.connect(site=os.environ.get("site"))
