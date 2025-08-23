
import frappe

def execute():
    if frappe.db.exists("Custom Field", {"dt": "Monthly Distribution", "fieldname": "budget"}):
        frappe.delete_doc("Custom Field", f"Monthly Distribution-budget")
