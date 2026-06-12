import frappe


def execute():
    if frappe.db.exists("Report", "Budget Report"):
        report = frappe.get_doc("Report", "Budget Report")

        if report.module != "Budge":
            report.module = "Budge"
            report.save(ignore_permissions=True)

            frappe.db.commit()