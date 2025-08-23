
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    # لو الحقل مش موجود ضيفه
    if not frappe.db.exists("Custom Field", {"dt": "Monthly Distribution", "fieldname": "budget"}):
        create_custom_field(
            "Monthly Distribution",
            {
                "fieldname": "budget",
                "label": "Budget",
                "fieldtype": "Link",
                "options": "Budget",
                "insert_after": "distribution_id",  
                "read_only": 0,
                "hidden": 0
            }
        )
        print("Field 'budget' created successfully.")
    else:
        print("Field 'budget' already exists, skipping creation.")
