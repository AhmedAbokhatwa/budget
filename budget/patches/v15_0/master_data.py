import frappe
def execute():
    create_expense_accounts()
    create_test_items()
    
def create_expense_accounts():
    accounts = [
        {"account_name": "Office Supplies", "parent_account": "Expenses", "account_type": "Expense Account"},
        {"account_name": "Travel Expenses", "parent_account": "Expenses", "account_type": "Expense Account"},
        {"account_name": "Utilities", "parent_account": "Expenses", "account_type": "Expense Account"},
        {"account_name": "Marketing", "parent_account": "Expenses", "account_type": "Expense Account"},
        {"account_name": "Employee Welfare", "parent_account": "Expenses", "account_type": "Expense Account"},
    ]

    company = frappe.get_all("Company", fields=["name"], limit=1)
    if not company:
        frappe.throw("No company found. Please create a company first.")
    company_name = company[0].name

    for acc in accounts:
        if not frappe.db.exists("Account", {"account_name": acc["account_name"], "company": company_name}):
            doc = frappe.get_doc({
                "doctype": "Account",
                "account_name": acc["account_name"],
                "parent_account": acc["parent_account"] + " - " + company_name,
                "company": company_name,
                "is_group": 0,
                "account_type": "Expense Account",
                "root_type": "Expense"
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"Created {acc['account_name']}")


def create_test_items():
    items = [
        {"item_code": "ITEM-001", "item_name": "Printer Paper Pack", "expense_account": "Office Supplies"},
        {"item_code": "ITEM-002", "item_name": "Flight Ticket", "expense_account": "Travel Expenses"},
        {"item_code": "ITEM-003", "item_name": "Electricity Bill", "expense_account": "Utilities"},
        {"item_code": "ITEM-004", "item_name": "Facebook Ads", "expense_account": "Marketing"},
    ]

    company = frappe.get_all("Company", fields=["name"], limit=1)
    if not company:
        frappe.throw("No company found. Please create a company first.")
    company_name = company[0].name

    for itm in items:
        if not frappe.db.exists("Item", {"item_code": itm["item_code"]}):
            doc = frappe.get_doc({
                "doctype": "Item",
                "item_code": itm["item_code"],
                "item_name": itm["item_name"],
                "item_group": "All Item Groups",
                "stock_uom": "Nos",
                "is_stock_item": 0,   # خدمة/مصروف مش مخزون
                "default_expense_account": f"{itm['expense_account']} - {company_name}",
                "company": company_name
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"Created {itm['item_name']}")


def create_test_cost_centers():
    cost_centers = [
        {"cost_center_name": "Head Office"},
        {"cost_center_name": "Marketing Department"},
        {"cost_center_name": "IT Department"},
        {"cost_center_name": "Cairo Branch"}
    ]

    company = frappe.get_all("Company", fields=["name"], limit=1)
    if not company:
        frappe.throw("No company found. Please create a company first.")
    company_name = company[0].name

    for cc in cost_centers:
        if not frappe.db.exists("Cost Center", {"cost_center_name": cc["cost_center_name"], "company": company_name}):
            doc = frappe.get_doc({
                "doctype": "Cost Center",
                "cost_center_name": cc["cost_center_name"],
                "parent_cost_center": company_name,  # الجذر بيبقى باسم الشركة
                "is_group": 0,
                "company": company_name
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"✅ Created Cost Center: {cc['cost_center_name']}")
