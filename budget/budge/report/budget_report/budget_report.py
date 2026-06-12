import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "label": "Budget Control",
            "fieldname": "budget_control",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": "Department",
            "fieldname": "department",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": "Cost Center",
            "fieldname": "cost_center",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": "Project",
            "fieldname": "project",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": "Fiscal Year",
            "fieldname": "fiscal_year",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": "Budget",
            "fieldname": "budget",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": "Total Budget",
            "fieldname": "total_budget",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": "Total Spent",
            "fieldname": "total_spent",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": "Remaining",
            "fieldname": "remaining",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": "Utilization %",
            "fieldname": "utilization",
            "fieldtype": "Percent",
            "width": 130,
        },
    ]


def get_data(filters=None):
    data = []

    bc_filters = {"docstatus": 1}

    if filters and filters.get("department"):
        departments = filters.get("department")

        if isinstance(departments, str):
            departments = [d.strip() for d in departments.split(",") if d.strip()]

        bc_filters["department"] = ["in", departments]

    budget_controls = frappe.get_all(
        "Budget Control",
        filters=bc_filters,
        fields=[
            "name",
            "department",
            "cost_center",
            "custom_project",
            "fiscal_year",
            "budget",
        ],
    )

    from budget.budge.doctype.budget_control.budget_control import (
        get_consumed_amount,
    )

    for bc in budget_controls:

        total_budget = 0
        total_spent = 0

        # ✅ CHANGE: Project mode છે કે Cost Center mode
        is_project = bool(bc.get("custom_project"))

        if bc.budget:
            budget_doc = frappe.get_doc("Budget", bc.budget)

            for row in budget_doc.accounts:

                total_budget += row.budget_amount or 0

                if row.custom_monthly_distribution:
                    md = frappe.get_doc(
                        "Monthly Distribution",
                        row.custom_monthly_distribution,
                    )

                    for month_row in md.percentages:
                        # ✅ CHANGE: Project mode માં project pass કરો, Cost Center mode માં cost_center
                        if is_project:
                            total_spent += get_consumed_amount(
                                item_code=row.custom_item_code,
                                account=row.account,
                                project=bc.custom_project,
                                month=month_row.month,
                            )
                        else:
                            total_spent += get_consumed_amount(
                                item_code=row.custom_item_code,
                                account=row.account,
                                cost_center=bc.cost_center,
                                month=month_row.month,
                            )

        remaining = total_budget - total_spent
        utilization = (
            (total_spent / total_budget) * 100
            if total_budget else 0
        )

        project_name = ""
        if bc.custom_project:
            project_name = frappe.db.get_value(
                "Project",
                bc.custom_project,
                "project_name"
            ) or bc.custom_project

        data.append(
            {
                "budget_control": bc.name,
                "department": bc.department,
                "cost_center": bc.cost_center or "",
                "project": project_name,
                "fiscal_year": bc.fiscal_year,
                "budget": bc.budget,
                "total_budget": total_budget,
                "total_spent": total_spent,
                "remaining": remaining,
                "utilization": round(utilization, 2),
            }
        )

    return data