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
        # ✅ CHANGED: conditional based on custom_budget_against
        if self.custom_budget_against == 'Cost Center' and not self.cost_center:
            frappe.throw("Please select a Cost Center before submitting the form.")
        elif self.custom_budget_against == 'Project' and not self.custom_project:
            frappe.throw("Please select a Project before submitting the form.")

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
            # ✅ CHANGED: conditional based on custom_budget_against
            if self.custom_budget_against == 'Cost Center':
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
            elif self.custom_budget_against == 'Project':
                duplicates = frappe.db.sql("""
                    SELECT
                        br.name AS budget_request_name,
                        br.docstatus AS budget_request_status,
                        br.fiscal_year,
                        br.custom_project,
                        bid.item_code,
                        bid.expense_account
                    FROM `tabBudget Request` br
                    LEFT JOIN `tabBudget Items Details` bid
                        ON br.name = bid.parent
                    WHERE br.fiscal_year = %s
                      AND br.custom_project = %s
                      AND bid.item_code = %s
                      AND bid.expense_account = %s
                      AND br.name != %s
                      AND br.docstatus < 2
                """, (
                    self.fiscal_year,
                    self.custom_project,
                    row.item_code,
                    row.expense_account,
                    self.name
                ), as_dict=True)
            else:
                duplicates = []

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
        # إنشاء database lock لمنع التكرار

        frappe.db.sql("SELECT GET_LOCK(%s, 10)", (f"budget_creation_{budget_request_name}",))

        try:
            budget_request = frappe.get_doc("Budget Request", budget_request_name)

            # فحص إذا كان البادجيت اتعمل خلاص
            if budget_request.budget_created:
                frappe.throw("Budget already created for this request.")
                # return {
                #     "success": False,
                #     "error": _("1Budget already created for this request.")
                # }

            # فحص للـ duplicate budgets
            duplicate_check = check_for_duplicate_budgets_server(budget_request)
            if duplicate_check["has_duplicate"]:
                frappe.throw("Budget already created for this request.")
                # return {
                #     "success": False,
                #     "error": duplicate_check["message"]
                # }

            # إنشاء البادجيت
            budget_name = create_budget_with_distributions_server(budget_request)
            if budget_name:
                print("*************?????***************")
                # تحديث الـ Budget Request
                frappe.db.set_value("Budget Request", budget_request_name, "budget_created", 1)
                frappe.db.commit()
                frappe.msgprint(
                    _("Budget {0} is created successfully").format(budget_name)
                )

                return {
                    "success": True,
                    "budget_name": budget_name
                }
            else:
                frappe.throw("ERROR Create Budget")
        finally:
            frappe.db.sql(
                "SELECT RELEASE_LOCK(%s)",
                (f"budget_creation_{budget_request_name}",)
            )

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
    """
    Server-side duplicate budget check
    """
    try:
        accepted_items = [item for item in budget_request.budget_items_details if item.status == "Accepted"]
        fiscal_year = budget_request.fiscal_year
        cost_center = budget_request.cost_center

        for item in accepted_items:
            # فحص وجود بادجيت مماثل
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

            if existing_budget:
                message = _("Budget already exists: '{0}' for Cost Center '{1}', Account '{2}' in Fiscal Year {3} item is '{4}' ").format(
                    existing_budget[0].budget_name,
                    cost_center,
                    item.expense_account,
                    fiscal_year,
                    item.item_code
                )
                print('TTTTTTTTTTTTTTTTTTTTTTTTTTTTT')
                frappe.throw(message)
                return {
                    "has_duplicate": True,
                    "message": message
                }

        return {"has_duplicate": False}

    except Exception as e:
        frappe.log_error(
            title="Error checking duplicates",
            message=frappe.get_traceback()  # أو str(e) لكن كـ message مش title
        )
        raise

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
                account_budget["custom_monthly_distribution"]= monthly_dist.name,

                accounts_table.append(account_budget)

        # إنشاء البادجيت
        budget = create_budget_document_server(budget_request, accounts_table)
        # print('budget',budget.name)
        # monthly_dist.custom_budget = budget.name
        # monthly_dist.save(ignore_permissions=True)
        # monthly_dist.db_set("custom_budget", budget.name)
        # frappe.db.commit()
        # ربط الـ distributions بالبادجيت
        return budget.name

    except Exception as e:
        frappe.log_error(
            title="Error creating budget",
            message= frappe.get_traceback()
            )
        raise

def create_monthly_distribution_server(budget_request, item):
    """
    إنشاء Monthly Distribution في الـ server
    """
    monthly_dist = frappe.new_doc("Monthly Distribution")
    monthly_dist.distribution_id = f"{budget_request.name}-{item.expense_account}"
    monthly_dist.fiscal_year = budget_request.fiscal_year
    monthly_dist.custom_expense_account = item.expense_account
    monthly_dist.custom_budget_control = budget_request.budget_control
    monthly_dist.custom_item_code = item.item_code
    monthly_dist.custom_department = budget_request.department

    monthly_dist.custom_budget_against = budget_request.custom_budget_against
    
    # ✅ CHANGED: conditional based on custom_budget_against
    if budget_request.custom_budget_against == 'Cost Center':
        monthly_dist.custom_cost_center = budget_request.cost_center
    elif budget_request.custom_budget_against == 'Project':
        monthly_dist.custom_project = budget_request.custom_project

    # حساب النسب الشهرية
    percentages = calculate_monthly_percentages_server([item])
    for row in percentages:
        monthly_dist.append('percentages', row)
    monthly_dist.insert()
    frappe.db.commit()
    return monthly_dist

def create_budget_document_server(budget_request, accounts_table):
    """
    إنشاء البادجيت في الـ server
    """
    try:
        print("\nBuilding budget document...")
        budget = frappe.new_doc("Budget")

        # ✅ CHANGED: conditional budget_against
        budget.budget_against = budget_request.custom_budget_against
        if budget_request.custom_budget_against == 'Cost Center':
            budget.cost_center = budget_request.cost_center
        elif budget_request.custom_budget_against == 'Project':
            budget.project = budget_request.custom_project

        budget.fiscal_year = budget_request.fiscal_year
        budget.custom_budget_control = budget_request.budget_control
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

        control_doc = frappe.get_doc("Budget Control", budget_request.budget_control)
        control_doc.db_set("budget", budget.name)

        print("Submitting budget...")
        budget.submit()
        print(f"Budget submitted, docstatus: {budget.docstatus}")
        frappe.db.commit()
        print(f"Budget submitted, docstatus: {budget.docstatus}")

        return budget

    except Exception as e:
        print(f"ERROR in create_budget_document_server: {str(e)}")
        frappe.log_error(
            title="Error creating budget document",
            message=frappe.get_traceback()
        )
        raise
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
def delete_budget_related_records(budget_control_name, fiscal_year, department, budget_controller, cost_center):
    """
    Delete all budget-related records in correct order:
    1. Monthly Distribution Percentages (Child)
    2. Monthly Distribution (Parent)
    3. Budget Accounts (Child)
    4. Budget (Parent) - but first unlink from Budget Request
    5. Budget Items Details (Child)
    6. Budget Request (Parent)
    """
    try:
        print("\n========== START DELETE BUDGET RECORDS ==========")

        # Get all Budget Requests matching filters
        budget_requests = frappe.get_all(
            "Budget Request",
            filters={
                "budget_control": budget_control_name,
                "fiscal_year": fiscal_year,
                "department": department,
                "budget_controller": budget_controller,
                "cost_center": cost_center
            },
            fields=["name"]
        )

        print(f"Found {len(budget_requests)} Budget Requests")

        for br in budget_requests:
            br_name = br.name
            print(f"\n--- Processing Budget Request: {br_name} ---")

            try:
                # Get budgets linked to this Budget Request
                budgets = frappe.get_all(
                    "Budget",
                    filters={"custom_budget_request_reference": br_name},
                    fields=["name"]
                )

                print(f"Found {len(budgets)} Budgets for {br_name}")

                # Process each budget
                for budget in budgets:
                    budget_name = budget.name
                    print(f"  Deleting Budget: {budget_name}")

                    # 1️⃣ Delete Monthly Distribution Percentages first
                    monthly_distributions = frappe.get_all(
                        "Monthly Distribution",
                        filters={"custom_budget": budget_name},
                        fields=["name"]
                    )

                    for md in monthly_distributions:
                        md_name = md.name
                        print(f"    - Deleting Monthly Distribution: {md_name}")

                        # Delete percentages (child table)
                        frappe.db.sql(
                            "DELETE FROM `tabMonthly Distribution Percentage` WHERE parent=%s",
                            (md_name,)
                        )
                        print(f" ✓ Deleted percentages")

                        # Delete Monthly Distribution itself
                        frappe.db.sql(
                            "DELETE FROM `tabMonthly Distribution` WHERE name=%s",
                            (md_name,)
                        )
                        print(f"      ✓ Deleted Monthly Distribution")

                    # 2️⃣ Delete Budget Accounts (child table)
                    frappe.db.sql(
                        "DELETE FROM `tabBudget Account` WHERE parent=%s",
                        (budget_name,)
                    )
                    print(f" ✓ Deleted Budget Accounts")

                    # 3️⃣ Unlink budget from Budget Request BEFORE deleting
                    frappe.db.sql(
                        "UPDATE `tabBudget` SET custom_budget_request_reference=NULL WHERE name=%s",
                        (budget_name,)
                    )
                    print(f"    ✓ Unlinked from Budget Request")

                    # 4️⃣ Delete Budget itself
                    frappe.db.sql(
                        "DELETE FROM `tabBudget` WHERE name=%s",
                        (budget_name,)
                    )
                    print(f"    ✓ Deleted Budget")

                # 5️⃣ Now safe to delete Budget Request
                # First delete Budget Items Details (child table)
                frappe.db.sql(
                    "DELETE FROM `tabBudget Items Details` WHERE parent=%s",
                    (br_name,)
                )
                print(f"  ✓ Deleted Budget Items Details")

                # Delete Budget Request itself
                frappe.db.sql(
                    "DELETE FROM `tabBudget Request` WHERE name=%s",
                    (br_name,)
                )
                print(f"  ✓ Deleted Budget Request: {br_name}")

                frappe.db.commit()

            except Exception as e:
                frappe.db.rollback()
                print(f"ERROR processing {br_name}: {str(e)}")
                frappe.log_error(
                    title=f"Error deleting Budget Request {br_name}",
                    message=frappe.get_traceback()
                )
                raise

        print("\n========== DELETE COMPLETED SUCCESSFULLY ==========\n")

        return {
            "success": True,
            "message": f"Successfully deleted all records for Budget Control {budget_control_name}"
        }

    except Exception as e:
        frappe.db.rollback()
        print(f"FATAL ERROR: {str(e)}")
        frappe.log_error(
            title="Error in delete_budget_related_records",
            message=frappe.get_traceback()
        )
        return {
            "success": False,
            "error": str(e)
        }