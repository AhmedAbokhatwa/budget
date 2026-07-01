# Copyright (c) 2025, ahmed and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, nowdate, cstr
import json
import calendar
from datetime import datetime


@frappe.whitelist()
def get_monthly_distribution_department(cost_center, fiscal_year, department, budget):
    allocations = []

    monthly_distributions = frappe.get_all(
        "Monthly Distribution",
        filters={
            "custom_cost_center": cost_center,
            "fiscal_year": fiscal_year,
            "custom_department": department,
            "custom_budget": budget,
        },
        fields=[
            "name",
            "custom_expense_account",
            "custom_budget",
            "custom_cost_center",
            "custom_item_code",
        ],
    )

    for md in monthly_distributions:
        monthly_allocations = frappe.get_all(
            "Monthly Distribution Percentage",
            filters={"parent": md.name},
            fields=["month", "custom_amount", "percentage_allocation", "parent"],
            order_by="idx asc",
        )

        for alloc in monthly_allocations:
            requested = alloc.custom_amount or 0
            consumed = get_consumed_amount(
                item_code=md.custom_item_code,
                account=md.custom_expense_account,
                cost_center=md.custom_cost_center,
                month=alloc.month,
            )

            allocations.append(
                {
                    "item_code": md.custom_item_code,
                    "account": md.custom_expense_account,
                    "cost_center": md.custom_cost_center,
                    "month": alloc.month,
                    "monthly_allocation": alloc.percentage_allocation,
                    "requested": requested,
                    "consumed": consumed,
                    "remaining": requested - consumed,
                }
            )

    return allocations


def get_consumed_amount(item_code, account, cost_center, month):
    month_mapping = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12,
    }

    if month not in month_mapping:
        return 0

    month_num = month_mapping[month]
    current_year = datetime.now().year
    first_day = f"{current_year}-{month_num:02d}-01"
    last_day_num = calendar.monthrange(current_year, month_num)[1]
    last_day = f"{current_year}-{month_num:02d}-{last_day_num}"
    consumed_amount = 0

    try:
        purchase_invoice_items = frappe.db.sql(
            """
            SELECT SUM(pii.amount) as total_amount
            FROM `tabPurchase Invoice Item` pii
            INNER JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
            WHERE pii.item_code = %(item_code)s
            AND pii.expense_account = %(account)s
            AND pii.cost_center = %(cost_center)s
            AND pi.posting_date >= %(start_date)s
            AND pi.posting_date <= %(end_date)s
            AND pi.docstatus = 1
            """,
            {
                "item_code": item_code,
                "account": account,
                "cost_center": cost_center,
                "start_date": first_day,
                "end_date": last_day,
            },
            as_dict=True,
        )
        if purchase_invoice_items and purchase_invoice_items[0].total_amount:
            consumed_amount += purchase_invoice_items[0].total_amount
    except Exception as e:
        frappe.log_error(f"Error in getting Purchase Invoice consumed amount: {str(e)}")

    try:
        pending_po_amount = frappe.db.sql(
            """
            SELECT SUM(poi.amount - IFNULL(poi.received_qty * poi.rate, 0)) as pending_amount
            FROM `tabPurchase Order Item` poi
            INNER JOIN `tabPurchase Order` po ON poi.parent = po.name
            WHERE poi.item_code = %(item_code)s
            AND poi.expense_account = %(account)s
            AND poi.cost_center = %(cost_center)s
            AND po.transaction_date >= %(start_date)s
            AND po.transaction_date <= %(end_date)s
            AND po.docstatus = 1
            AND po.status NOT IN ('Cancelled', 'Closed')
            AND poi.received_qty < poi.qty
            """,
            {
                "item_code": item_code,
                "account": account,
                "cost_center": cost_center,
                "start_date": first_day,
                "end_date": last_day,
            },
            as_dict=True,
        )
        if pending_po_amount and pending_po_amount[0].pending_amount:
            consumed_amount += pending_po_amount[0].pending_amount
    except Exception as e:
        frappe.log_error(f"Error in getting Purchase Order consumed amount: {str(e)}")

    return consumed_amount or 0


@frappe.whitelist()
def get_monthly_distribution_report(cost_center, fiscal_year, department, budget, month=None):
    data = get_monthly_distribution_department(cost_center, fiscal_year, department, budget)

    if month:
        data = [d for d in data if d["month"] == month]

    totals = {
        "total_requested": sum(d["requested"] for d in data),
        "total_consumed": sum(d["consumed"] for d in data),
        "total_remaining": sum(d["remaining"] for d in data),
    }

    return {"data": data, "totals": totals, "cost_center": cost_center, "month": month}


@frappe.whitelist()
def update_budget_amount(cost_center, item_code, account, month, new_amount, action):
    try:
        if not frappe.has_permission("Budget", "write"):
            frappe.throw(_("You don't have permission to update budget amounts"))

        if not cost_center or not account or not month:
            return {"success": False, "error": "Missing required parameters"}

        new_amount = flt(new_amount)
        if new_amount < 0:
            return {"success": False, "error": "Budget amount cannot be negative"}

        md_name = find_budget(cost_center, account, item_code)
        if not md_name:
            return {"success": False, "error": "Could not find Monthly Distribution document"}

        success = update_monthly_distribution(md_name, month, new_amount, action)

        if success and success.get("success") is True:
            create_budget_log(
                success.get("budget_name"),
                cost_center,
                item_code,
                account,
                month,
                success.get("old_amount"),
                success.get("new_amount"),
                success.get("changed_amount"),
                frappe.session.user,
            )
            return {"success": True, "message": "Budget updated successfully"}
        else:
            return {"success": False, "error": "Failed to update monthly distribution"}

    except Exception as e:
        frappe.log_error(f"Budget update error: {str(e)}", "Budget Control Update")
        return {"success": False, "error": str(e)}


def find_budget(cost_center, account, item_code):
    try:
        conditions = """
            ba.account = %(account)s
            AND b.cost_center = %(cost_center)s
            AND b.docstatus = 1
        """
        filters = {"account": account, "cost_center": cost_center}

        if item_code:
            conditions += " AND ba.custom_item_code = %(item_code)s "
            filters["item_code"] = item_code

        query = """
            SELECT
                b.name as budget_name,
                b.cost_center as cost_center,
                ba.account as account,
                ba.custom_item_code as item_code,
                ba.custom_monthly_distribution as monthly_distribution
            FROM `tabBudget` b
            LEFT JOIN `tabBudget Account` ba ON ba.parent = b.name
            WHERE %s
        """ % conditions

        result = frappe.db.sql(query, filters, as_dict=True)

        if len(result) > 1:
            frappe.throw("You have more than one Budget matching these filters")

        if result and len(result) == 1:
            monthly_distribution = result[0].monthly_distribution
            if not monthly_distribution:
                frappe.throw("Can't Find monthly distribution")
            return monthly_distribution

    except Exception as e:
        frappe.throw(_("Error finding budget"))

def update_monthly_distribution(md_name, month, diff_amount, action):
    try:
        updated_table = {"changed_amount": diff_amount, "monthly_distribution": md_name}

        if not md_name:
            frappe.throw(_("No Monthly Distribution linked"))

        if not frappe.db.exists("Monthly Distribution", md_name):
            frappe.throw(_(f"Monthly Distribution: {md_name} does not exist"))

        monthly_dist_doc = frappe.get_doc("Monthly Distribution", md_name)

        if not frappe.db.exists("Budget", monthly_dist_doc.custom_budget):
            frappe.throw(_(f"Budget {monthly_dist_doc.custom_budget} does not exist"))

        budget_doc = frappe.get_doc("Budget", monthly_dist_doc.custom_budget)
        updated_table["budget_name"] = monthly_dist_doc.custom_budget

        budget_account = next(
            (row for row in budget_doc.accounts if row.account == monthly_dist_doc.custom_expense_account),
            None,
        )
        if not budget_account:
            frappe.throw(_("Account not found in Budget"))

        if action == "increase":
            budget_account.db_set("budget_amount", budget_account.budget_amount + diff_amount)
            month_row = next((row for row in monthly_dist_doc.percentages if row.month == month), None)
            if month_row:
                updated_table["old_amount"] = month_row.custom_amount
                month_row.custom_amount = (month_row.custom_amount or 0) + diff_amount
                updated_table["new_amount"] = month_row.custom_amount
            else:
                frappe.throw(_(f"{month} not found in {monthly_dist_doc.name}"))

        if action == "decrease":
            if diff_amount > budget_account.budget_amount:
                frappe.throw(_("Deduction exceeds total annual Budget Amount"))

            month_row = next((row for row in monthly_dist_doc.percentages if row.month == month), None)

            if not month_row:
                frappe.throw(_(f"{month} not found in {monthly_dist_doc.name}"))

            if diff_amount > (month_row.custom_amount or 0):
                frappe.throw(_("Deduction exceeds the Monthly allocated amount"))
            else:
                budget_account.db_set("budget_amount", max(0, budget_account.budget_amount - diff_amount))
                updated_table["old_amount"] = month_row.custom_amount
                month_row.custom_amount = (month_row.custom_amount or 0) - diff_amount
                updated_table["new_amount"] = month_row.custom_amount

        total_percentage = sum([row.custom_amount for row in monthly_dist_doc.percentages])
        if total_percentage > 0:
            for row in monthly_dist_doc.percentages:
                row.percentage_allocation = (row.custom_amount / total_percentage) * 100
        else:
            for row in monthly_dist_doc.percentages:
                row.percentage_allocation = 0

        budget_doc.save()
        monthly_dist_doc.save()
        updated_table["success"] = True
        return updated_table

    except Exception as e:
        frappe.log_error(f"Error updating monthly distribution: {str(e)}", "Budget Control")
        return False


def create_budget_log(budget_name, cost_center, item_code, account, month, old_amount, new_amount, changed_amount, user):
    try:
        if frappe.db.exists("DocType", "Budget Control Log"):
            log_doc = frappe.new_doc("Budget Control Log")
            log_doc.budget = budget_name
            log_doc.cost_center = cost_center
            log_doc.item_code = item_code
            log_doc.account = account
            log_doc.month = month
            log_doc.old_amount = old_amount
            log_doc.new_amount = new_amount
            log_doc.change_amount = changed_amount
            log_doc.changed_by = user
            log_doc.change_date = nowdate()
            log_doc.save()
    except Exception as e:
        frappe.log_error(f"Error creating budget log: {str(e)}", "Budget Control Log")


@frappe.whitelist()
def delete_budget_related_records(fiscal_year, department, cost_center):
    try:
        from budget.budget.doctype.budget_request.budget_request import delete_budget_related_records as _delete
        return _delete(
            fiscal_year=fiscal_year,
            department=department,
            cost_center=cost_center,
        )
    except Exception as e:
        frappe.log_error(f"Delete budget records error: {str(e)}", "Budget Control Page")
        return {"success": False, "error": str(e)}
