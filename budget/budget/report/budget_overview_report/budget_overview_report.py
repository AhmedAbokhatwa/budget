# Copyright (c) 2026, ahmed and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
import calendar
from datetime import datetime


MONTHS = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December",
]


def execute(filters=None):
    filters = filters or {}
    validate_filters(filters)
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)
    return columns, data, None, chart, summary


def validate_filters(filters):
    if not filters.get("fiscal_year"):
        frappe.throw(_("Fiscal Year is required."))
    if not filters.get("cost_center"):
        frappe.throw(_("Cost Center is required."))


def get_columns():
    return [
        {
            "fieldname": "month",
            "label": _("Month"),
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "item_code",
            "label": _("Item"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 150,
        },
        {
            "fieldname": "account",
            "label": _("Account"),
            "fieldtype": "Link",
            "options": "Account",
            "width": 180,
        },
        {
            "fieldname": "requested",
            "label": _("Budgeted"),
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "fieldname": "consumed",
            "label": _("Consumed"),
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "fieldname": "remaining",
            "label": _("Remaining"),
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "fieldname": "consumed_pct",
            "label": _("Consumed %"),
            "fieldtype": "Percent",
            "width": 110,
        },
    ]


def get_data(filters):
    conditions, params = build_conditions(filters)

    sql_query = """
        SELECT
            md.name,
            md.custom_expense_account  AS account,
            md.custom_cost_center      AS cost_center,
            md.custom_item_code        AS item_code
        FROM `tabMonthly Distribution` md
        WHERE %s
        """ % conditions
    monthly_distributions = frappe.db.sql(sql_query, params, as_dict=True)

    if not monthly_distributions:
        return []

    rows = []

    for md in monthly_distributions:
        percentages = frappe.get_all(
            "Monthly Distribution Percentage",
            filters={"parent": md.name},
            fields=["month", "custom_amount", "percentage_allocation"],
            order_by="idx asc",
        )

        for p in percentages:
            if filters.get("month") and p.month != filters["month"]:
                continue

            requested = flt(p.custom_amount)
            consumed = _get_consumed(
                item_code=md.item_code,
                account=md.account,
                cost_center=md.cost_center,
                month=p.month,
                fiscal_year=filters["fiscal_year"],
            )
            remaining = requested - consumed
            consumed_pct = (consumed / requested * 100) if requested else 0

            rows.append({
                "month": p.month,
                "item_code": md.item_code,
                "account": md.account,
                "requested": requested,
                "consumed": consumed,
                "remaining": remaining,
                "consumed_pct": flt(consumed_pct, 2),
            })

    rows.sort(key=lambda r: MONTHS.index(r["month"]) if r["month"] in MONTHS else 99)
    return rows


def build_conditions(filters):
    conditions = ["1=1"]
    params = {}

    conditions.append("md.fiscal_year = %(fiscal_year)s")
    params["fiscal_year"] = filters["fiscal_year"]

    conditions.append("md.custom_cost_center = %(cost_center)s")
    params["cost_center"] = filters["cost_center"]

    if filters.get("department"):
        conditions.append("md.custom_department = %(department)s")
        params["department"] = filters["department"]

    if filters.get("budget"):
        conditions.append("md.custom_budget = %(budget)s")
        params["budget"] = filters["budget"]

    if filters.get("item_code"):
        conditions.append("md.custom_item_code = %(item_code)s")
        params["item_code"] = filters["item_code"]

    return " AND ".join(conditions), params


def _get_consumed(item_code, account, cost_center, month, fiscal_year):
    month_map = {m: i + 1 for i, m in enumerate(MONTHS)}

    if month not in month_map:
        return 0

    year = _get_fiscal_year_start(fiscal_year)
    month_num = month_map[month]
    import calendar as cal
    last_day = cal.monthrange(year, month_num)[1]
    start = f"{year}-{month_num:02d}-01"
    end = f"{year}-{month_num:02d}-{last_day}"

    params = {
        "item_code": item_code,
        "account": account,
        "cost_center": cost_center,
        "start": start,
        "end": end,
    }

    pi_amount = frappe.db.sql(
        """
        SELECT IFNULL(SUM(pii.amount), 0)
        FROM `tabPurchase Invoice Item` pii
        JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
        WHERE pii.item_code      = %(item_code)s
          AND pii.expense_account = %(account)s
          AND pii.cost_center     = %(cost_center)s
          AND pi.posting_date BETWEEN %(start)s AND %(end)s
          AND pi.docstatus = 1
        """,
        params,
    )[0][0] or 0

    po_amount = frappe.db.sql(
        """
        SELECT IFNULL(SUM(poi.amount - IFNULL(poi.received_qty * poi.rate, 0)), 0)
        FROM `tabPurchase Order Item` poi
        JOIN `tabPurchase Order` po ON poi.parent = po.name
        WHERE poi.item_code      = %(item_code)s
          AND poi.expense_account = %(account)s
          AND poi.cost_center     = %(cost_center)s
          AND po.transaction_date BETWEEN %(start)s AND %(end)s
          AND po.docstatus = 1
          AND po.status NOT IN ('Cancelled', 'Closed')
          AND poi.received_qty < poi.qty
        """,
        params,
    )[0][0] or 0

    return flt(pi_amount) + flt(po_amount)


def _get_fiscal_year_start(fiscal_year):
    fy = frappe.db.get_value("Fiscal Year", fiscal_year, ["year_start_date"], as_dict=True)
    if fy and fy.year_start_date:
        return fy.year_start_date.year
    from datetime import datetime
    return datetime.now().year


def get_chart(data):
    month_totals = {}

    for row in data:
        m = row["month"]
        if m not in month_totals:
            month_totals[m] = {"requested": 0, "consumed": 0, "remaining": 0}
        month_totals[m]["requested"] += flt(row["requested"])
        month_totals[m]["consumed"] += flt(row["consumed"])
        month_totals[m]["remaining"] += flt(row["remaining"])

    sorted_months = sorted(month_totals.keys(), key=lambda m: MONTHS.index(m) if m in MONTHS else 99)

    return {
        "data": {
            "labels": sorted_months,
            "datasets": [
                {
                    "name": _("Budgeted"),
                    "values": [month_totals[m]["requested"] for m in sorted_months],
                    "chartType": "bar",
                },
                {
                    "name": _("Consumed"),
                    "values": [month_totals[m]["consumed"] for m in sorted_months],
                    "chartType": "bar",
                },
                {
                    "name": _("Remaining"),
                    "values": [month_totals[m]["remaining"] for m in sorted_months],
                    "chartType": "line",
                },
            ],
        },
        "type": "axis-mixed",
        "colors": ["#4463F0", "#CB2929", "#29CD42"],
    }


def get_summary(data):
    total_requested = sum(flt(r["requested"]) for r in data)
    total_consumed = sum(flt(r["consumed"]) for r in data)
    total_remaining = sum(flt(r["remaining"]) for r in data)
    overall_pct = (total_consumed / total_requested * 100) if total_requested else 0

    return [
        {
            "value": total_requested,
            "label": _("Total Budgeted"),
            "datatype": "Currency",
            "indicator": "blue",
        },
        {
            "value": total_consumed,
            "label": _("Total Consumed"),
            "datatype": "Currency",
            "indicator": "red" if overall_pct > 80 else "orange",
        },
        {
            "value": total_remaining,
            "label": _("Total Remaining"),
            "datatype": "Currency",
            "indicator": "green" if total_remaining > 0 else "red",
        },
        {
            "value": flt(overall_pct, 2),
            "label": _("Consumed %"),
            "datatype": "Percent",
            "indicator": "red" if overall_pct > 90 else "orange" if overall_pct > 70 else "green",
        },
    ]
