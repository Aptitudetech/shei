# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aptitude technologie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class StatesperCountry(Document):
	def validate(self):
		self.state_abbr = self.state_abbr.strip().upper()
		self.state = self.state.strip()
