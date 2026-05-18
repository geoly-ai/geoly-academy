import frappe


def execute():
	if not frappe.db.exists("Custom Field", {"dt": "File", "fieldname": "cos_uploaded"}):
		frappe.get_doc(
			{
				"doctype": "Custom Field",
				"dt": "File",
				"fieldname": "cos_uploaded",
				"label": "COS Uploaded",
				"fieldtype": "Check",
				"read_only": 1,
				"hidden": 1,
				"insert_after": "is_private",
			}
		).insert(ignore_permissions=True)
