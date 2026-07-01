# Copyright (c) 2025, ahmed and contributors
# For license information, please see license.txt
# pyright: reportUndefinedVariable=false

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate
class BudgetRequest(Document):
    def before_submit(self):
        self.validate_budget_items()
        self.validate_cost_center()
        self.validate_duplicate_items()

    def on_submit(self):
        self.posting_date = nowdate()
        self.status = "Requested"
        check_and_create_budget(self.name)

    def validate_cost_center(self):
        if not self.cost_center:
            frappe.throw("Please select a Cost Center before submitting the form.")

    def validate_budget_items(self):
        if not self.budget_items_details or len(self.budget_items_details) == 0:
            frappe.throw(_("Please add at least one budget item."))

        accepted_item = [item for item in self.budget_items_details if item.status == "Accepted"]
        if len(accepted_item) == 0:
            not_accepted_rows = [str(item.idx) for item in self.budget_items_details]
            frappe.throw(
                "Please accept at least one item before submitting the form. "
                f"Currently, all rows ({', '.join(not_accepted_rows)}) are not accepted."
            )

        invalid_rows = [
            item for item in self.budget_items_details
            if not item.expense_account or not item.expected_price or item.expected_price <= 0
        ]
        if len(invalid_rows) > 0:
            for item in self.budget_items_details:
                if not item.expense_account or not item.expected_price or item.expected_price <= 0:
                    frappe.throw(
                        f"Row #{item.idx}: Please ensure this row has a valid expense account "
                        f"and expected price greater than 0."
                    )

        # ✅ check for duplicate expense accounts
        seen_accounts = {}
        for item in self.budget_items_details:
            if item.expense_account in seen_accounts:
                frappe.throw(
                    _("Duplicate Expense Account found in row #{0}. "
                      "Expense Account <b>{1}</b> is already used in row #{2}.").format(
                        item.idx, item.expense_account, seen_accounts[item.expense_account]
                    )
                )
            else:
                seen_accounts[item.expense_account] = item.idx



    def validate_duplicate_items(self):
        for row in self.budget_items_details:
            duplicates = frappe.db.sql("""
                SELECT
                    br.name AS budget_request_name,
                    br.docstatus AS budget_request_status,
                    br.fiscal_year,
                    br.cost_center,
                    bid.item_code,
                    bid.expense_account
                FROM `tabBudget Request` br
                LEFT JOIN `tabBudget Items Details` bid
                    ON br.name = bid.parent
                WHERE br.fiscal_year = %s
                  AND br.cost_center = %s
                  AND bid.item_code = %s
                  AND bid.expense_account = %s
                  AND br.name != %s
                  AND br.docstatus < 2
            """, (
                self.fiscal_year,
                self.cost_center,
                row.item_code,
                row.expense_account,
                self.name
            ), as_dict=True)

            if duplicates:

                frappe.throw(
                    _("Duplicate Budget Item found for Item Code <b>{0}</b>, Expense Account <b>{1}</b>, "
                      "Cost Center <b>{2}</b>, Fiscal Year <b>{3}</b> (Already exists in Request: {4})").format(
                        row.item_code,
                        row.expense_account,
                        self.cost_center,
                        self.fiscal_year,
                        duplicates[0].budget_request_name
                    ),
                    title=_("Duplicate Budget Item")
                )

def check_and_create_budget(budget_request_name):
    """
    Server-side method to check and create budget with proper locking mechanism
    """
    try:
        budget_request = frappe.get_doc("Budget Request", budget_request_name)

        if budget_request.budget_created:
            frappe.throw(_("Budget already created for this request."))

        check_for_duplicate_budgets_server(budget_request)

        budget_name = create_budget_with_distributions_server(budget_request)

        frappe.db.set_value("Budget Request", budget_request_name, "budget_created", 1)
        frappe.msgprint(_("Budget {0} created successfully").format(budget_name))

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(
            title="Budget Creation Error",
            message=frappe.get_traceback()  # أو str(e) لكن كـ message مش title
        )
        return {
            "success": False,
            "error": str(e)
        }


def check_for_duplicate_budgets_server(budget_request):
    accepted_items = [item for item in budget_request.budget_items_details if item.status == "Accepted"]
    fiscal_year = budget_request.fiscal_year
    cost_center = budget_request.cost_center


    for item in accepted_items:
        if frappe.db.has_column("Budget", "fiscal_year"):
            existing_budget = frappe.db.sql("""
                SELECT b.name as budget_name
                FROM `tabBudget` b
                JOIN `tabBudget Account` ba ON ba.parent = b.name
                WHERE b.cost_center = %s
                AND b.fiscal_year = %s
                AND ba.account = %s
                AND ba.custom_item_code = %s
                AND b.docstatus != 2
            """, (cost_center, fiscal_year, item.expense_account, item.item_code), as_dict=True)
        else:
            existing_budget = frappe.db.sql("""
                SELECT b.name as budget_name
                FROM `tabBudget` b
                JOIN `tabBudget Account` ba ON ba.parent = b.name
                WHERE b.cost_center = %s
                AND b.from_fiscal_year = %s
                AND b.to_fiscal_year = %s
                AND ba.account = %s
                AND ba.custom_item_code = %s
                AND b.docstatus != 2
            """, (cost_center, fiscal_year, fiscal_year, item.expense_account, item.item_code), as_dict=True)
        if existing_budget:
            frappe.throw(_("Budget already exists: '{0}' for Cost Center '{1}', Account '{2}' in Fiscal Year {3} item is '{4}'").format(
                existing_budget[0].budget_name, cost_center, item.expense_account, fiscal_year, item.item_code
            ))

    return {"has_duplicate": False}

def create_budget_with_distributions_server(budget_request):
    """
    Server-side budget creation with distributions
    """
    try:
        accepted_items = [item for item in budget_request.budget_items_details if item.status == "Accepted"]
        print('ssssssssssssssssssssssssssssssssssssssssssssssssssssss')
        print('accepted_items',accepted_items)
        if not accepted_items:
            frappe.throw(_("No accepted budget items found to create budgets."))

        accounts_table = []

        # إنشاء Monthly Distribution لكل صف
        for item in accepted_items:

            account_budget = {
                "account": item.expense_account,
                "budget_amount": float(item.total or 0),
                "custom_item_code": item.item_code
            }
            # for Each Item ->  Monthly Distribution
            monthly_dist = create_monthly_distribution_server(budget_request, item)
            if monthly_dist:
                print('monthly_dist',monthly_dist.name)
                # إعداد الـ account budget
                account_budget["custom_monthly_distribution"]= monthly_dist.name

                accounts_table.append(account_budget)

        # إنشاء البادجيت
        budget_name = create_budget_document_server(budget_request, accounts_table)
        return budget_name

    except Exception as e:
        frappe.log_error(
            title="Error creating budget",
            message= frappe.get_traceback()
            )
        raise

def create_monthly_distribution_server(budget_request, item):

    dist_id = f"{budget_request.name}-{item.expense_account}"
    if frappe.db.exists("Monthly Distribution", dist_id):
        frappe.throw(_("Duplicate Monthly Distribution found for Expense Account '{0}' and Cost Center '{1}'").format(
            item.expense_account, budget_request.cost_center))

    monthly_dist = frappe.new_doc("Monthly Distribution")
    monthly_dist.distribution_id = dist_id
    monthly_dist.fiscal_year = budget_request.fiscal_year
    monthly_dist.custom_expense_account = item.expense_account
    monthly_dist.custom_cost_center = budget_request.cost_center
    monthly_dist.custom_item_code = item.item_code
    monthly_dist.custom_department = budget_request.department
    # حساب النسب الشهرية
    percentages = calculate_monthly_percentages_server([item])
    for row in percentages:
        monthly_dist.append('percentages',row)
    monthly_dist.insert()
    return monthly_dist

def create_budget_document_server(budget_request, accounts_table):
    """
    إنشاء البادجيت في الـ server
    """
    try:

        budget = frappe.new_doc("Budget")
        budget.budget_against = "Cost Center"
        budget.cost_center = budget_request.cost_center
        if frappe.db.has_column("Budget", "fiscal_year"):
            budget.fiscal_year = budget_request.fiscal_year
        else:
            budget.from_fiscal_year = budget_request.fiscal_year
            budget.to_fiscal_year = budget_request.fiscal_year
        budget.custom_budget_request_reference = budget_request.name
        budget.applicable_on_purchase_order = 1
        budget.applicable_on_material_request = 1
        budget.applicable_on_booking_actual_expenses = 1
        budget.custom_action_if__monthly_budget_exceeded_on_po = 'Stop'
        print(f"Adding {len(accounts_table)} accounts to budget...")
        # إضافة الـ accounts
        for idx, account_data in enumerate(accounts_table):
            budget.append("accounts", account_data)
            print(f"  - Added account {idx+1}: {account_data['account']}")

        print("Inserting budget...")
        budget.insert()
        print(f"Budget inserted with name: {budget.name}")

        for account_data in accounts_table:
            md_doc = frappe.get_doc("Monthly Distribution", account_data['custom_monthly_distribution'])
            md_doc.custom_budget = budget.name
            md_doc.save(ignore_permissions=True)

        print("Submitting budget...")
        budget.submit()
        print(f"Budget submitted, docstatus: {budget.docstatus}")
        return budget.name

    except Exception as e:
        print(f"ERROR in create_budget_document_server: {str(e)}")
        frappe.db.rollback()
        frappe.throw(_("Error creating budget: {0}").format(str(e)))
def calculate_monthly_percentages_server(items):
    """
    حساب النسب الشهرية في الـ server
    """
    month_list = ["january", "february", "march", "april", "may", "june",
                  "july", "august", "september", "october", "november", "december"]
    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    total = 0
    monthly_values = {}

    # جمع القيم لكل شهر
    for item in items:
        for month in month_list:
            qty = float(getattr(item, month, 0) or 0)
            value = qty * float(item.expected_price or 0)
            monthly_values[month] = monthly_values.get(month, 0) + value
            total += value

    # إنشاء array النسب
    percentages = []
    for idx, name in enumerate(month_names):
        month_key = month_list[idx]
        perc = (monthly_values.get(month_key, 0) / total * 100) if total > 0 else (100 / 12)
        percentages.append({
            "month": name,
            "custom_amount": monthly_values.get(month_key, 0),
            "percentage_allocation": round(perc, 4)
        })

    return percentages
@frappe.whitelist()
def delete_budget_related_records(fiscal_year, department, cost_center):
    budget_requests = frappe.get_all(
        "Budget Request",
        filters={"fiscal_year": fiscal_year, "department": department, "cost_center": cost_center},
        fields=["name"]
    )

    for br in budget_requests:
        br_name = br.name
        try:
            budgets = frappe.get_all(
                "Budget",
                filters={"custom_budget_request_reference": br_name},
                fields=["name"]
            )

            for budget in budgets:
                budget_name = budget.name

                monthly_distributions = frappe.get_all(
                    "Monthly Distribution",
                    filters={"custom_budget": budget_name},
                    fields=["name"]
                )

                for md in monthly_distributions:
                    frappe.db.delete("Monthly Distribution Percentage", {"parent": md.name})
                    frappe.db.delete("Monthly Distribution", {"name": md.name})

                frappe.db.delete("Budget Account", {"parent": budget_name})
                frappe.db.set_value("Budget", budget_name, "custom_budget_request_reference", None)
                frappe.db.delete("Budget", {"name": budget_name})

            frappe.db.delete("Budget Items Details", {"parent": br_name})
            frappe.db.delete("Budget Request", {"name": br_name})

        except Exception as e:
            frappe.db.rollback()
            frappe.throw(_("Error deleting records for Budget Request {0}: {1}").format(br_name, str(e)))

    frappe.msgprint(_("Successfully deleted all records for Budget"))
    return {"success": True, "message": "Successfully deleted all records for Budget"}
