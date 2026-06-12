# Copyright (c) 2025, ahmed and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate, getdate, add_months, cstr
import json

class BudgetControl(Document):
    def before_save(self):
        """Skip core mandatory validation for Project mode"""
        if self.custom_budget_against == 'Project':
            self.flags.ignore_mandatory = True
    def before_submit(self):
        """Validation before submitting the document"""
        if self.custom_budget_against == 'Project':
            self.flags.ignore_mandatory = True
        self.validate_fiscal_year()
        self.validate_required_fields()
        self.delete_draft_budget_control()
        self.validate_submitted_budget_control()
        self.validate_budget_controller()
    def on_submit(self):
        """Actions to perform after document submission"""
        try:
            self.create_budget_requests()
        except Exception as e:
            self.handle_submission_error(e)

    def validate_required_fields(self):
        """Validate that all required fields are filled"""
        required_fields = [
            'budget_controller', 'department',
            'fiscal_year', 'budget_name', 'status'
        ]

        if self.custom_budget_against == 'Cost Center':
            required_fields.append('cost_center')
        elif self.custom_budget_against == 'Project':
            required_fields.append('custom_project')

        missing_fields = []
        for field in required_fields:
            field_value = getattr(self, field, None)
            if not field_value or (isinstance(field_value, str) and not field_value.strip()):
                missing_fields.append(field)

        if missing_fields:
            fields_list = ", ".join([f"'{field}'" for field in missing_fields])
            frappe.throw(
                _("The following required fields are missing: {0}").format(fields_list),
                title=_("Required Fields Missing")
            )

    def validate_fiscal_year(self):
        """Validate fiscal year exists and is active"""
        if not frappe.db.exists("Fiscal Year", self.fiscal_year):
            frappe.throw(
                _("Fiscal Year '{0}' does not exist").format(self.fiscal_year),
                title=_("Invalid Fiscal Year")
            )

    def validate_budget_controller(self):
        """Validate budget controller value"""
        valid_controllers = ['Financial', 'Departmental', 'Project', 'Employee']
        if self.budget_controller not in valid_controllers:
            frappe.throw(
                _("Budget Controller must be one of: {0}").format(", ".join(valid_controllers)),
                title=_("Invalid Budget Controller")
            )

    def delete_draft_budget_control(self):
        """Handle duplicate budget controls for the same cost center"""
        if not self.cost_center:
            return  # No cost center specified, skip duplicate check
        duplicates = frappe.get_list(
            'Budget Control',
            filters={
                'cost_center': self.cost_center,
                'fiscal_year': self.fiscal_year,
                'name': ['!=', self.name],
                'docstatus': ['=', 0]
            },
            fields=['name', 'budget_name']
        )

        if duplicates:
            print('d',duplicates)
            self.handle_duplicate_records(duplicates)
    def validate_submitted_budget_control(self):
        '''
            Prevent Create Another Sumitted B Control
        '''
        if not self.cost_center:
            return
        duplicates = frappe.get_list(
            'Budget Control',
            filters={
                'cost_center': self.cost_center,
                'fiscal_year': self.fiscal_year,
                'name': ['!=', self.name],
                'docstatus': ['=', 1]
            },
            fields=['name', 'budget_name']
        )

        if duplicates:
            duplicate_names = [d.name for d in duplicates]
            frappe.throw(f"Found Existing Budget Controls {', '.join(duplicate_names)}")

    def handle_duplicate_records(self, duplicates):
        """Handle duplicate budget control records"""
        duplicate_names = [d.name for d in duplicates]
        print('NAMES',duplicate_names)
        # Ask user for confirmation before deleting
        frappe.msgprint(
            _("Found existing Budget Controls for Cost Center '{0}': {1}").format(
                self.cost_center, ", ".join(duplicate_names)
            ),
            title=_("Duplicate Records Found"),
            indicator="orange"
        )

        # Delete duplicates (you might want to add user confirmation here)
        deleted_count = 0
        errors = []

        for duplicate in duplicates:
            try:
                # Check if document can be deleted
                doc = frappe.get_doc('Budget Control', duplicate.name)
                if doc.docstatus == 1:  # Submitted document
                    doc.cancel()

                frappe.delete_doc('Budget Control', duplicate.name, force=True)
                deleted_count += 1

            except Exception as e:
                error_msg = f"Failed to delete {duplicate.name}: {str(e)}"
                errors.append(error_msg)
                frappe.log_error(
                    title="Budget Control Deletion Error",
                    message=error_msg
                )

        # Report results
        if deleted_count > 0:
            frappe.msgprint(
                _("Successfully deleted {0} duplicate Budget Control(s)").format(deleted_count),
                title=_("Cleanup Complete"),
                indicator="green"
            )

        if errors:
            frappe.msgprint(
                _("Some records could not be deleted. Check error logs for details."),
                title=_("Partial Cleanup"),
                indicator="yellow"
            )

    def create_budget_requests(self):
        """Create budget requests based on budget controller type"""
        created_requests = []

        if self.budget_controller == 'Financial':
            request = self.create_financial_budget_request()
            if request:
                created_requests.append(request)

        elif self.budget_controller == 'Departmental':
            request = self.create_departmental_budget_request()
            if request:
                created_requests.append(request)
        elif self.budget_controller == 'Employee':
            request = self.create_employee_budget_request()
            if request:
                created_requests.append(request)
        else:
            frappe.throw(
                _("Budget Controller '{0}' is not supported for automatic request creation").format(
                    self.budget_controller
                ),
                title=_("Unsupported Controller Type")
            )

        if created_requests:
            # self.show_success_message(created_requests)
            req_name = request.get('name')
            req_dept = request.get('department')
            print(f"Request name: {req_name}, Department: {req_dept}")
            # رسالة بسيطة بدون HTML معقد
            simple_message = f"Budget Request is Created {req_name} Department: {req_dept}"
            frappe.msgprint(simple_message)
        else:
            frappe.msgprint(
                _("No budget requests were created"),
                title=_("No Action Taken"),
                indicator="orange"
            )

    def create_financial_budget_request(self):
        """Create a financial budget request"""
        doc_dict = {
            'doctype': 'Budget Request',
            'department': self.department,
            'fiscal_year': self.fiscal_year,
            'budget_control': self.name,
            'budget_controller': self.budget_controller,
            'custom_budget_against': self.custom_budget_against,
            'posting_date': nowdate(),
            'status': 'Requested'
        }

        if self.custom_budget_against == 'Cost Center':
            doc_dict['cost_center'] = self.cost_center
        elif self.custom_budget_against == 'Project':
            doc_dict['custom_project'] = self.custom_project

        print('DICT',doc_dict)
        try:
            budget_request = frappe.get_doc(doc_dict)
            budget_request.insert()

            frappe.log_error(
                title="Budget Request Created Successfully",
                message=f"Created Budget Request: {budget_request.name} for Budget Control: {self.name}"
            )

            return {
                'name': budget_request.name,
                'department': cstr(budget_request.department),
                'cost_center': cstr(budget_request.cost_center),
                'type': 'Financial'
            }

        except Exception as e:
            frappe.log_error(
                title="Budget Request Creation Failed",
                message=f"Failed to create budget request for {self.name}: {str(e)}"
            )
            raise e

    def create_departmental_budget_request(self):
        """Create a departmental budget request"""
        # Similar to financial but with different logic
        doc_dict = {
            'doctype': 'Budget Request',
            'department': self.department,
            'fiscal_year': self.fiscal_year,
            'budget_control': self.name,
            'budget_controller': self.budget_controller,
            'custom_budget_against': self.custom_budget_against,
            'request_date': nowdate(),
            'status': 'Requested'
        }

        if self.custom_budget_against == 'Cost Center':
            doc_dict['cost_center'] = self.cost_center
        elif self.custom_budget_against == 'Project':
            doc_dict['custom_project'] = self.custom_project

        try:
            budget_request = frappe.get_doc(doc_dict)
            budget_request.insert(ignore_permissions=True)

            return {
                'name': budget_request.name,
                'department': cstr(budget_request.department),
                'cost_center': cstr(budget_request.cost_center),
                'type': 'Departmental'
            }

        except Exception as e:
            frappe.log_error(
                title="Departmental Budget Request Creation Failed",
                message=f"Failed to create departmental budget request for {self.name}: {str(e)}"
            )
            raise e
    def create_employee_budget_request(self):
        """Create a employee budget request"""
        # Similar to financial but with different logic
        doc_dict = {
            'doctype': 'Budget Request',
            'department': self.department,
            'fiscal_year': self.fiscal_year,
            'budget_control': self.name,
            'budget_controller': self.budget_controller,
            'custom_budget_against': self.custom_budget_against,
            'request_date': nowdate(),
            'status': 'Requested'
        }

        if self.custom_budget_against == 'Cost Center':
            doc_dict['cost_center'] = self.cost_center
        elif self.custom_budget_against == 'Project':
            doc_dict['custom_project'] = self.custom_project

        try:
            budget_request = frappe.get_doc(doc_dict)
            budget_request.insert(ignore_permissions=True)

            return {
                'name': budget_request.name,
                'department': cstr(budget_request.department),
                'cost_center': cstr(budget_request.cost_center),
                'type': 'Employee'
            }

        except Exception as e:
            frappe.log_error(
                title="Departmental Budget Request Creation Failed",
                message=f"Failed to create Employee budget request for {self.name}: {str(e)}"
            )
            raise e


    def on_cancel(self):
        """Actions to perform when document is cancelled"""
        try:
            # Cancel related budget requests
            related_requests = frappe.get_list(
                'Budget Request',
                filters={'budget_control': self.name, 'docstatus': 1},
                fields=['name']
            )

            for request in related_requests:
                try:
                    request_doc = frappe.get_doc('Budget Request', request.name)
                    request_doc.cancel()
                    frappe.msgprint(
                        _("Cancelled related Budget Request: {0}").format(request.name)
                    )
                except Exception as e:
                    frappe.log_error(
                        title="Failed to cancel Budget Request",
                        message=f"Could not cancel {request.name}: {str(e)}"
                    )

        except Exception as e:
            frappe.log_error(
                title="Budget Control Cancellation Error",
                message=f"Error during cancellation of {self.name}: {str(e)}"
            )


    def show_success_message(self, requests_list):
        """Display success message with created requests details"""
        if not requests_list:
            return

        # Create HTML message
        message_html = '<div style="text-align: center; padding: 20px;">'
        message_html += f'''
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <h3 style="margin: 0; font-size: 18px;">🎉 Budget Requests Created Successfully!</h3>
        </div>
        '''

        message_html += '<div style="text-align: right;">'
        message_html += f'<p style="font-size: 16px; color: #2c3e50;"><strong>تم إنشاء {len(requests_list)} طلب ميزانية بنجاح:</strong></p>'
        message_html += '<div style="display: flex; flex-wrap: wrap; gap: 15px; justify-content: center;">'

        for req in requests_list:
            req_name = req.get('name', 'N/A')
            req_dept = req.get('department', 'N/A')
            req_center = req.get('cost_center', 'N/A')
            req_type = req.get('type', 'Standard')

            message_html += f'''
            <div style="background: #f8f9fa; border: 2px solid #28a745; border-radius: 12px;
                        padding: 20px; min-width: 250px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 15px;">
                    <span style="font-size: 24px;">📋</span>
                </div>
                <div style="text-align: right;">
                    <p style="margin: 5px 0; font-weight: bold; color: #2c3e50;">
                        📄 الطلب: <span style="color: #28a745;">{req_name}</span>
                    </p>
                    <p style="margin: 5px 0; color: #6c757d;">
                        🏢 القسم: {req_dept}
                    </p>
                    <p style="margin: 5px 0; color: #6c757d;">
                        🏛️ مركز التكلفة: {req_center}
                    </p>
                    <p style="margin: 5px 0; color: #6c757d;">
                        🔧 النوع: {req_type}
                    </p>
                </div>
            </div>
            '''

        message_html += '</div></div></div>'

        frappe.msgprint({
            'title': _('Budget Control Processing Complete ✅'),
            'message': message_html,
            'indicator': 'green',
            'wide': True
        })

    def handle_submission_error(self, error):
        """Handle errors during submission"""
        import traceback
        error_trace = traceback.format_exc()
        error_message = str(error)

        # Log detailed error
        frappe.log_error(
            title=f"Budget Control Submission Error - {self.name}",
            message=f"Error: {error_message}\n\nFull Trace:\n{error_trace}"
        )

        # Show user-friendly error
        frappe.throw(
            _("Failed to process Budget Control submission: {0}").format(error_message),
            title=_("Submission Error")
        )

@frappe.whitelist()
def get_monthly_distribution_department(cost_center=None, fiscal_year=None, department=None, budget=None, project=None):
    allocations = []

    # هات كل الـ Monthly Distributions الخاصة بالـ Cost Center او Project
    md_filters = {
        "fiscal_year": fiscal_year,
        "custom_department": department,
    }

    if budget:
        md_filters["custom_budget"] = budget
    if project:
        md_filters["custom_project"] = project
    else:
        md_filters["custom_cost_center"] = cost_center

    monthly_distributions = frappe.get_all(
        "Monthly Distribution",
        filters=md_filters,
        fields=[
            "name",
            "custom_expense_account",
            "custom_budget",
            "custom_cost_center",
            "custom_project",
            "custom_item_code",
        ],
    )
    print("monthly_distributions",monthly_distributions)
    for md in monthly_distributions:
        # هات تفاصيل النسب الشهرية
        monthly_allocations = frappe.get_all(
            "Monthly Distribution Percentage",
            filters={"parent": md.name},
            fields=["month", "custom_amount", "percentage_allocation", "parent"],
            order_by = "idx asc"
        )

        for alloc in monthly_allocations:
            # هنا هنضيف بيانات كل شهر لكل Item
            requested = alloc.custom_amount or 0
            consumed = get_consumed_amount(
                item_code=md.custom_item_code,
                account=md.custom_expense_account,
                cost_center=md.custom_cost_center,
                project=md.custom_project,
                month=alloc.month,
            )

            allocations.append(
                {
                    "item_code": md.custom_item_code,
                    "account": md.custom_expense_account,
                    "cost_center": md.custom_cost_center,
                    "project": md.custom_project,
                    "month": alloc.month,
                    "monthly_allocation": alloc.percentage_allocation,
                    "requested": requested,
                    "consumed": consumed,
                    "remaining": requested - consumed,
                }
            )


    return allocations


def get_consumed_amount(item_code, account, cost_center=None, project=None, month=None):
    """
    احسب المصروف من Purchase Invoice / Purchase Order
    على حسب الـ item_code + account + (cost_center او project) + الشهر
    """
    import calendar
    from datetime import datetime

    # تحويل اسم الشهر إلى رقم الشهر
    month_mapping = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }

    if month not in month_mapping:
        return 0

    month_num = month_mapping[month]
    current_year = datetime.now().year

    # احسب أول وآخر يوم في الشهر
    first_day = f"{current_year}-{month_num:02d}-01"
    last_day_num = calendar.monthrange(current_year, month_num)[1]
    last_day = f"{current_year}-{month_num:02d}-{last_day_num}"

    consumed_amount = 0

    # حدد هل الفلترة على أساس Project ولا Cost Center
    if project:
        ref_condition_pii = "pii.project = %(ref_value)s"
        ref_condition_poi = "poi.project = %(ref_value)s"
        ref_value = project
    else:
        ref_condition_pii = "pii.cost_center = %(ref_value)s"
        ref_condition_poi = "poi.cost_center = %(ref_value)s"
        ref_value = cost_center

    base_values = {
        "item_code": item_code,
        "account": account,
        "ref_value": ref_value,
        "start_date": first_day,
        "end_date": last_day,
    }

    # البحث في Purchase Invoice Items
    try:
        purchase_invoice_items = frappe.db.sql(
            f"""
            SELECT SUM(pii.amount) as total_amount
            FROM `tabPurchase Invoice Item` pii
            INNER JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
            WHERE pii.item_code = %(item_code)s
            AND pii.expense_account = %(account)s
            AND {ref_condition_pii}
            AND pi.posting_date >= %(start_date)s
            AND pi.posting_date <= %(end_date)s
            AND pi.docstatus = 1
        """,
            base_values,
            as_dict=True,
        )

        if purchase_invoice_items and purchase_invoice_items[0].total_amount:
            consumed_amount += purchase_invoice_items[0].total_amount

    except Exception as e:
        frappe.log_error(f"Error in getting Purchase Invoice consumed amount: {str(e)}")

    # البحث في Purchase Order Items (إختياري - إذا كنت تريد تضمين PO)
    try:
        purchase_order_items = frappe.db.sql(
            f"""
            SELECT SUM(poi.amount) as total_amount
            FROM `tabPurchase Order Item` poi
            INNER JOIN `tabPurchase Order` po ON poi.parent = po.name
            WHERE poi.item_code = %(item_code)s
            AND poi.expense_account = %(account)s
            AND {ref_condition_poi}
            AND po.transaction_date >= %(start_date)s
            AND po.transaction_date <= %(end_date)s
            AND po.docstatus = 1
            AND po.status NOT IN ('Cancelled', 'Closed')
        """,
            base_values,
            as_dict=True,
        )

        # إضافة PO amount فقط إذا لم يتم إنشاء Purchase Invoice منه بعد
        # يمكنك تعديل هذا المنطق حسب احتياجاتك
        if purchase_order_items and purchase_order_items[0].total_amount:
            # تحقق من عدم وجود Purchase Invoice مرتبط
            pending_po_amount = frappe.db.sql(
                f"""
                SELECT SUM(poi.amount - IFNULL(poi.received_qty * poi.rate, 0)) as pending_amount
                FROM `tabPurchase Order Item` poi
                INNER JOIN `tabPurchase Order` po ON poi.parent = po.name
                WHERE poi.item_code = %(item_code)s
                AND poi.expense_account = %(account)s
                AND {ref_condition_poi}
                AND po.transaction_date >= %(start_date)s
                AND po.transaction_date <= %(end_date)s
                AND po.docstatus = 1
                AND po.status NOT IN ('Cancelled', 'Closed')
                AND poi.received_qty < poi.qty
            """,
                base_values,
                as_dict=True,
            )

            if pending_po_amount and pending_po_amount[0].pending_amount:
                consumed_amount += pending_po_amount[0].pending_amount

    except Exception as e:
        frappe.log_error(f"Error in getting Purchase Order consumed amount: {str(e)}")

    return consumed_amount or 0


# دالة مساعدة لإرجاع تقرير مفصل (إختياري)
@frappe.whitelist()
def get_monthly_distribution_report(cost_center=None, fiscal_year=None, department=None, month=None, project=None):
    """
    إرجاع تقرير مفصل للتوزيع الشهري
    """
    data = get_monthly_distribution_department(cost_center, fiscal_year, department, project=project)

    if month:
        # فلترة البيانات حسب الشهر المحدد
        data = [d for d in data if d["month"] == month]

    # إضافة إجماليات
    totals = {
        "total_requested": sum(d["requested"] for d in data),
        "total_consumed": sum(d["consumed"] for d in data),
        "total_remaining": sum(d["remaining"] for d in data),
    }

    return {"data": data, "totals": totals, "cost_center": cost_center, "project": project, "month": month}


# budget.budge.doctype.budget_control.budget_control.py


@frappe.whitelist()
def update_budget_amount(cost_center, item_code, account, month, new_amount, action):
    """
    Update budget amount for a specific item/account/month combination
    """
    try:
        # التحقق من الصلاحيات
        print("Cost Center",cost_center)
        print("item code",item_code)
        print("account",account)
        print("month",month)
        print("new_amount",new_amount, action)
        if not frappe.has_permission("Budget", "write"):
            frappe.throw(_("You don't have permission to update budget amounts"))

        # التحقق من صحة البيانات
        if not cost_center or not account or not month:
            return {"success": False, "error": "Missing required parameters"}

        new_amount = flt(new_amount)
        if new_amount < 0:
            return {"success": False, "error": "Budget amount cannot be negative"}

        # البحث عن Budget الأساسي
        md_name = find_budget(cost_center, account, item_code)
        print('MD ==>',md_name)
        if not md_name:
            return {
                "success": False,
                "error": "Could not find Monthly Distribution document",
            }

        # تحديث Monthly Distribution
        success = update_monthly_distribution(md_name, month, new_amount, action)

        print('success ==>',success)
        if success and success.get("success") == True:
            # إضافة سجل في Budget Control Log
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
    """
    Find existing budget or create new one
    """
    try:
        # البحث عن Budget موجود

        conditions = """
            ba.account = %(account)s
            AND b.cost_center = %(cost_center)s
            AND b.docstatus = 1
        """
        filters = {
            "account": account,
            "cost_center": cost_center,
        }


        if item_code:
            conditions += " AND ba.custom_item_code = %(item_code)s "
            filters["item_code"] = item_code
        query = f"""
                select
                    b.name as budget_name,
                    b.cost_center as cost_center,
                    ba.account as account,
                    ba.custom_item_code as item_code ,
                    ba.custom_monthly_distribution as monthly_distribution
                from `tabBudget` b
                left join `tabBudget Account` ba
                on ba.parent = b.name
                WHERE {conditions}
            """
        result = frappe.db.sql(query, filters, as_dict=True)

        print('existing Budget',result)

        if len(result) > 1 :
            frappe.throw("You have more than one Budget matching these filters")

        if result and len(result) == 1:
            monthly_distribution = result[0].monthly_distribution
            print('monthly_distribution',monthly_distribution)
            if not monthly_distribution:
                frappe.throw("Can't Find monthly distribution")
            return monthly_distribution

    except Exception as e:
        frappe.log_error(f"Error finding/creating budget: {str(e)}", "Budget Control")
        return None

def update_monthly_distribution(md_name, month, diff_amount, action):
    try:
        updated_table = {
            'changed_amount':diff_amount,
            "monthly_distribution": md_name

        }
        if not md_name:
            frappe.throw(_("No Monthly Distribution linked"))

        exists = frappe.db.exists("Monthly Distribution", md_name)
        print("exists:", exists)
        if not exists:
            frappe.throw(_(f"Monthly Distribution : {md_name} does not exist"))

        monthly_dist_doc = frappe.get_doc("Monthly Distribution", md_name)
        print("monthly_dist_doc",monthly_dist_doc)

        budget_exists = frappe.db.exists("Budget", monthly_dist_doc.custom_budget)
        if not budget_exists:
            frappe.throw(_(f"Budget {monthly_dist_doc.custom_budget} does not exist"))

        budget_doc = frappe.get_doc("Budget", monthly_dist_doc.custom_budget)
        print("budget_doc",budget_doc)

        updated_table['budget_name'] = monthly_dist_doc.custom_budget
        # تعديل الاجمالي
        print("updated_table",updated_table)
        budget_account = next(
            (
                row
                for row in budget_doc.accounts
                if row.account == monthly_dist_doc.custom_expense_account
            ),
            None,
        )
        print("budget_account:", budget_account)
        if not budget_account:
            frappe.throw(_("Account not found in Budget"))

        if action == "increase":
            # تعديل البادجيت الاحمالي
            budget_account.db_set(
                "budget_amount", budget_account.budget_amount + diff_amount
            )

            # # تعديل الشهر
            month_row = next(
                (row for row in monthly_dist_doc.percentages if row.month == month),
                None,
            )
            if month_row:
                updated_table['old_amount'] = month_row.custom_amount
                month_row.custom_amount = (month_row.custom_amount or 0) + diff_amount
                updated_table['new_amount'] = month_row.custom_amount
            else:
                frappe.throw(_(f"{month} not found in {monthly_dist_doc.name}"))

        if action == "decrease":

            if diff_amount > budget_account.budget_amount:
                frappe.throw(_("Deduction exceeds total annual Budget Amount"))

            month_row = next((row for row in monthly_dist_doc.percentages if row.month == month), None)

             # # تعديل الشهر شرطين
            #  - Greater than month NO
            #  - Greater Than Budget No
            if not month_row:
                frappe.throw(_(f"{month} not found in {monthly_dist_doc.name}"))

            if diff_amount > (month_row.custom_amount or 0):
                frappe.throw(_("Deduction exceeds the Monthly allocated amount"))

            else:
                budget_account.db_set(
                    "budget_amount", max(0, budget_account.budget_amount - diff_amount)
                )
                updated_table['old_amount'] = month_row.custom_amount
                month_row.custom_amount = (month_row.custom_amount or 0) - diff_amount
                updated_table['new_amount'] = month_row.custom_amount
        # تحديث النسبة الجديدة
        total_precentage = sum([row.custom_amount for row in monthly_dist_doc.percentages])
        if total_precentage > 0:
            for row in monthly_dist_doc.percentages:
                row.percentage_allocation = (row.custom_amount/total_precentage) * 100
        else:
            for row in monthly_dist_doc.percentages:
                row.percentage_allocation = 0

        budget_doc.save()
        monthly_dist_doc.save()
        updated_table['success'] = True
        print("updated_table",updated_table)
        return updated_table

    except Exception as e:
        frappe.log_error(
            f"Error updating monthly distribution: {str(e)}", "Budget Control"
        )
        return False


def create_monthly_distribution(budget_doc, month, amount):
    """
    Create new monthly distribution
    """
    try:
        monthly_dist = frappe.new_doc("Monthly Distribution")
        monthly_dist.distribution_id = f"MD-{budget_doc.cost_center}-{nowdate()}"

        # إضافة الشهر
        monthly_dist.append(
            "percentages",
            {"month": month, "percentage_allocation": 100 if amount > 0 else 0},
        )

        monthly_dist.save()
        return monthly_dist

    except Exception as e:
        frappe.log_error(
            f"Error creating monthly distribution: {str(e)}", "Budget Control"
        )
        return None


def create_budget_log(
    budget_name, cost_center, item_code, account, month, old_amount, new_amount, changed_amount, user
):
    """
    Create audit log for budget changes
    """
    try:
        # إنشاء سجل في Budget Control Log (إذا كان موجود)
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
        # لا نريد أن يفشل التحديث بسبب مشكلة في التسجيل
        frappe.log_error(f"Error creating budget log: {str(e)}", "Budget Control Log")


@frappe.whitelist()
def bulk_update_budget(updates):
    """
    Update multiple budget items at once
    """
    try:
        if isinstance(updates, str):
            updates = json.loads(updates)

        success_count = 0
        error_count = 0
        errors = []

        for update in updates:
            result = update_budget_amount(
                update.get("cost_center"),
                update.get("item_code"),
                update.get("account"),
                update.get("month"),
                update.get("new_amount"),
            )

            if result.get("success"):
                success_count += 1
            else:
                error_count += 1
                errors.append(
                    {"item": update.get("item_code"), "error": result.get("error")}
                )

        return {
            "success": error_count == 0,
            "updated": success_count,
            "errors": error_count,
            "error_details": errors,
        }

    except Exception as e:
        frappe.log_error(f"Bulk update error: {str(e)}", "Budget Control Bulk")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def validate_budget_permissions(cost_center):
    """
    Validate user permissions for budget operations
    """
    try:
        # فحص الصلاحيات العامة
        if not frappe.has_permission("Budget", "write"):
            return {"valid": False, "message": "No write permission for Budget"}

        # فحص صلاحيات Cost Center
        if not frappe.has_permission("Cost Center", "read", cost_center):
            return {"valid": False, "message": "No access to this Cost Center"}

        # فحص Role محددة (اختياري)
        user_roles = frappe.get_roles(frappe.session.user)
        allowed_roles = ["Budget Manager", "Accounts Manager", "System Manager"]

        if not any(role in user_roles for role in allowed_roles):
            return {"valid": False, "message": "Insufficient role permissions"}

        return {"valid": True, "message": "Permissions validated"}

    except Exception as e:
        return {"valid": False, "message": f"Permission check failed: {str(e)}"}


def session_data():
    return frappe.session.user