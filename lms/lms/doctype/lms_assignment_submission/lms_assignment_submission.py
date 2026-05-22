# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.desk.doctype.notification_log.notification_log import make_notification_logs
from frappe.model.document import Document
from frappe.utils import validate_url

from lms.lms.utils import get_lms_route


class LMSAssignmentSubmission(Document):
	def validate(self):
		self.validate_duplicates()
		self.validate_url()
		self.validate_status()

	def on_update(self):
		self.validate_private_attachments()

	def validate_duplicates(self):
		if frappe.db.exists(
			"LMS Assignment Submission",
			{"assignment": self.assignment, "member": self.member, "name": ["!=", self.name]},
		):
			lesson_title = frappe.db.get_value("Course Lesson", self.lesson, "title")
			frappe.throw(
				_("Assignment for Lesson {0} by {1} already exists.").format(lesson_title, self.member_name)
			)

	def validate_url(self):
		if self.type == "URL" and not validate_url(self.answer, True, ["http", "https"]):
			frappe.throw(_("Please enter a valid URL."))

	def validate_status(self):
		if not self.is_new():
			doc_before_save = self.get_doc_before_save()
			if doc_before_save.status != self.status or doc_before_save.comments != self.comments:
				self.trigger_update_notification()

	def validate_private_attachments(self):
		self.attach_file_to_document(self.assignment_attachment, "assignment_attachment")
		if self.type == "Text":
			from bs4 import BeautifulSoup

			soup = BeautifulSoup(self.answer, "html.parser")
			self.attach_media_to_document(soup)

	def attach_media_to_document(self, soup):
		urls = set()
		for selector, attribute in (("img", "src"), ("video", "src"), ("source", "src")):
			for element in soup.find_all(selector):
				url = element.get(attribute, "")
				if url:
					urls.add(url)

		for url in urls:
			self.attach_file_to_document(url, "answer")

	def attach_file_to_document(self, file_url, attached_to_field):
		if not file_url:
			return

		file_name = frappe.db.get_value("File", {"file_url": file_url}, "name")
		if not file_name:
			return

		frappe.db.set_value(
			"File",
			file_name,
			{
				"attached_to_doctype": self.doctype,
				"attached_to_name": self.name,
				"attached_to_field": attached_to_field,
			},
		)

	def trigger_update_notification(self):
		notification = frappe._dict(
			{
				"subject": _("The instructor has left a comment on your assignment {0}").format(
					frappe.bold(self.assignment_title)
				),
				"email_content": self.comments,
				"document_type": self.doctype,
				"document_name": self.name,
				"from_user": self.evaluator,
				"type": "Alert",
				"link": get_lms_route(f"assignment-submission/{self.assignment}/{self.name}"),
			}
		)
		make_notification_logs(notification, [self.member])
