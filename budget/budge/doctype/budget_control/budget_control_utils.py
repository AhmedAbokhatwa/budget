# hooks.py - إضافة هذه الأسطر إلى ملف hooks.py الخاص بك

# Additional whitelisted methods
whitelisted_methods = [
    "budget.budge.doctype.budget_control.budget_control.update_budget_amount",
    "budget.budge.doctype.budget_control.budget_control.get_monthly_distribution_department", 
    "budget.budge.doctype.budget_control.budget_control.bulk_update_budget",
    "budget.budge.doctype.budget_control.budget_control.validate_budget_permissions"
]

# ===================================
# budget_control_utils.py - ملف منفصل للدوال المساعدة
# ===================================

import frappe
from frappe import _
from frappe.utils import flt, nowdate, getdate, cstr
from datetime import datetime
import calendar

class BudgetControlUtils:
    """
    Utility class for budget control operations
    """
    
    @staticmethod
    def get_fiscal_year_dates():
        """Get current fiscal year start and end dates"""
        try:
            fiscal_year = frappe.defaults.get_user_default("fiscal_year")
            if fiscal_year:
                fy_doc = frappe.get_doc("Fiscal Year", fiscal_year)
                return fy_doc.year_start_date, fy_doc.year_end_date
            else:
                # Default to current year if no fiscal year set
                current_year = datetime.now().year
                return f"{current_year}-01-01", f"{current_year}-12-31"
        except:
            current_year = datetime.now().year
            return f"{current_year}-01-01", f"{current_year}-12-31"
    
    @staticmethod
    def calculate_monthly_budget(annual_amount, distribution_percentages):
        """Calculate monthly budget amounts based on distribution percentages"""
        monthly_amounts = {}
        
        for month_data in distribution_percentages:
            month = month_data.get('month')
            percentage = flt(month_data.get('percentage_allocation', 0))
            monthly_amounts[month] = (annual_amount * percentage) / 100
            
        return monthly_amounts
    
    @staticmethod
    def get_actual_expenses(cost_center, account, from_date, to_date):
        """Get actual expenses for given parameters"""
        try:
            conditions = []
            values = {"cost_center": cost_center, "from_date": from_date, "to_date": to_date}
            
            if account:
                conditions.append("account = %(account)s")
                values["account"] = account
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
                SELECT 
                    account,
                    SUM(debit - credit) as actual_amount,
                    COUNT(*) as transaction_count
                FROM `tabGL Entry`
                WHERE cost_center = %(cost_center)s
                    AND posting_date BETWEEN %(from_date)s AND %(to_date)s
                    AND {where_clause}
                    AND docstatus = 1
                GROUP BY account
            """
            
            return frappe.db.sql(query, values, as_dict=True)
            
        except Exception as e:
            frappe.log_error(f"Error getting actual expenses: {str(e)}", "Budget Control Utils")
            return []
    
    @staticmethod
    def format_month_name(month_number):
        """Convert month number to name"""
        try:
            if isinstance(month_number, str) and month_number.isdigit():
                month_number = int(month_number)
            elif isinstance(month_number, str):
                return month_number  # Already a month name
                
            if 1 <= month_number <= 12:
                return calendar.month_name[month_number]
            else:
                return str(month_number)
        except:
            return str(month_number)
    
    @staticmethod
    def validate_budget_data(cost_center, account, amount, month=None):
        """Validate budget data before processing"""
        errors = []
        
        if not cost_center:
            errors.append("Cost Center is required")
        elif not frappe.db.exists("Cost Center", cost_center):
            errors.append(f"Cost Center '{cost_center}' does not exist")
            
        if not account:
            errors.append("Account is required")
        elif not frappe.db.exists("Account", account):
            errors.append(f"Account '{account}' does not exist")
            
        if amount is None or amount < 0:
            errors.append("Amount must be a positive number")
            
        if month and month not in [calendar.month_name[i] for i in range(1, 13)]:
            errors.append(f"Invalid month: {month}")
            
        return {"valid": len(errors) == 0, "errors": errors}

# ===================================
# budget_control_reports.py - تقارير إضافية
# ===================================
from budget.budge.doctype.budget_control.budget_control import get_monthly_distribution_department
@frappe.whitelist()
def get_budget_variance_report(cost_center, from_date=None, to_date=None):
    """Generate budget vs actual variance report"""
    try:
        if not from_date or not to_date:
            from_date, to_date = BudgetControlUtils.get_fiscal_year_dates()
        
        # Get budget data
        budget_data = get_monthly_distribution_department(cost_center)
        
        # Get actual expenses
        actual_data = BudgetControlUtils.get_actual_expenses(cost_center, None, from_date, to_date)
        
        # Combine and calculate variance
        variance_report = []
        
        for budget_item in budget_data:
            account = budget_item.get('account')
            budgeted = flt(budget_item.get('requested', 0))
            
            # Find matching actual data
            actual_amount = 0
            for actual_item in actual_data:
                if actual_item.get('account') == account:
                    actual_amount = flt(actual_item.get('actual_amount', 0))
                    break
            
            variance = budgeted - actual_amount
            variance_percent = (variance / budgeted * 100) if budgeted > 0 else 0
            
            variance_report.append({
                'account': account,
                'item_code': budget_item.get('item_code'),
                'month': budget_item.get('month'),
                'budgeted': budgeted,
                'actual': actual_amount,
                'variance': variance,
                'variance_percent': variance_percent,
                'status': 'Favorable' if variance >= 0 else 'Unfavorable'
            })
        
        return variance_report
        
    except Exception as e:
        frappe.log_error(f"Error generating variance report: {str(e)}", "Budget Variance Report")
        return []

@frappe.whitelist()
def get_budget_summary(cost_center=None):
    """Get budget summary across all cost centers or specific cost center"""
    try:
        conditions = ""
        values = {}
        
        if cost_center:
            conditions = "WHERE b.cost_center = %(cost_center)s"
            values["cost_center"] = cost_center
        
        query = f"""
            SELECT 
                b.cost_center,
                COUNT(DISTINCT b.name) as budget_count,
                SUM(ba.budget_amount) as total_budget,
                AVG(ba.budget_amount) as avg_budget,
                MAX(ba.budget_amount) as max_budget,
                MIN(ba.budget_amount) as min_budget
            FROM `tabBudget` b
            LEFT JOIN `tabBudget Account` ba ON b.name = ba.parent
            {conditions}
            AND b.docstatus = 1
            GROUP BY b.cost_center
            ORDER BY total_budget DESC
        """
        
        summary = frappe.db.sql(query, values, as_dict=True)
        
        # Add utilization data
        for item in summary:
            actual_data = BudgetControlUtils.get_actual_expenses(
                item['cost_center'], None, *BudgetControlUtils.get_fiscal_year_dates()
            )
            total_actual = sum([flt(a.get('actual_amount', 0)) for a in actual_data])
            item['total_actual'] = total_actual
            item['utilization_percent'] = (total_actual / item['total_budget'] * 100) if item['total_budget'] > 0 else 0
        
        return summary
        
    except Exception as e:
        frappe.log_error(f"Error getting budget summary: {str(e)}", "Budget Summary")
        return []

# ===================================
# validation.py - التحقق من صحة البيانات
# ===================================

def validate_budget_control(doc, method):
    """Validation function for Budget Control document"""
    
    # التحقق من وجود Cost Center
    if not doc.cost_center:
        frappe.throw(_("Cost Center is mandatory"))
    
    # التحقق من صلاحية Cost Center
    if not frappe.db.exists("Cost Center", doc.cost_center):
        frappe.throw(_("Invalid Cost Center: {0}").format(doc.cost_center))
    
    # التحقق من الصلاحيات
    if not frappe.has_permission("Cost Center", "read", doc.cost_center):
        frappe.throw(_("You don't have permission to access this Cost Center"))

def on_update_budget_control(doc, method):
    """After save operations for Budget Control"""
    
    # إنشاء سجل تدقيق
    create_audit_trail(doc)
    
    # تحديث ذاكة التخزين المؤقت
    clear_budget_cache(doc.cost_center)

def create_audit_trail(doc):
    """Create audit trail for budget control changes"""
    try:
        if hasattr(doc, '_doc_before_save'):
            # مقارنة التغييرات
            changes = []
            old_doc = doc._doc_before_save
            
            for field in ['cost_center', 'department']:
                if doc.get(field) != old_doc.get(field):
                    changes.append({
                        'field': field,
                        'old_value': old_doc.get(field),
                        'new_value': doc.get(field)
                    })
            
            if changes:
                # حفظ سجل التغيير
                frappe.get_doc({
                    'doctype': 'Budget Control Log',
                    'reference_document': doc.name,
                    'changed_by': frappe.session.user,
                    'change_date': nowdate(),
                    'changes': str(changes)
                }).insert(ignore_permissions=True)
                
    except Exception as e:
        frappe.log_error(f"Error creating audit trail: {str(e)}", "Budget Control Audit")

def clear_budget_cache(cost_center):
    """Clear budget related cache"""
    try:
        cache_keys = [
            f"budget_data_{cost_center}",
            f"monthly_dist_{cost_center}",
            "budget_summary"
        ]
        
        for key in cache_keys:
            frappe.cache().delete_key(key)
            
    except Exception as e:
        frappe.log_error(f"Error clearing cache: {str(e)}", "Budget Control Cache")