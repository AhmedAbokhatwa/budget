import frappe
from frappe import _
from datetime import datetime, timedelta
import calendar
import traceback


class validationMonthlyBudgetError(frappe.ValidationError):
    """Custom Exception for Monthly Budget Validation"""
    pass
@frappe.whitelist()
def validate_purchase_order_budget(po_doc, items):
    """
    Main API endpoint to validate Purchase Order against monthly budget
    """
    try:
        # Convert string to dict if needed
        if isinstance(po_doc, str):
            po_doc = frappe.parse_json(po_doc)
        if isinstance(items, str):
            items = frappe.parse_json(items)
            
        transaction_date = po_doc.get('transaction_date')
        po_name = po_doc.get('name')
        
        if not transaction_date:
            frappe.throw(_("Transaction Date is required"))
            
        if not items or len(items) == 0:
            frappe.throw(_("Items table cannot be empty"))
        
        # Get fiscal year from transaction date
        fiscal_year = transaction_date.split('-')[0]
        
        # Get existing PO data for the month
        existing_po_data = get_monthly_po_data(transaction_date, po_name)
        
        # Merge current items with existing data
        updated_totals = merge_current_items_with_existing(existing_po_data, items)
        
        # Get budget details for relevant accounts
        budget_details = get_budget_details(updated_totals, fiscal_year)
        
        # Get monthly distribution amounts
        monthly_allocations = get_monthly_allocations(transaction_date, budget_details)
        
        # Validate against budget
        validation_result = validate_against_monthly_budget(items, updated_totals, monthly_allocations)
        print('validation_result',validation_result)
        print('validation_result.get("has_stops")',validation_result.get("has_stops"))
        if validation_result.get("has_stops"):
            return {    
                'success': False,
                'type': 'validationMonthlyBudgetError',
                'validation_result': validation_result,
                'existing_po_data': existing_po_data,
                'updated_totals': updated_totals,
                'monthly_allocations': monthly_allocations
            }

        # Warnings ممكن ترجع success=True بس مع البيانات
        return {
            'success': True,
            'validation_result': validation_result,
            'existing_po_data': existing_po_data,
            'updated_totals': updated_totals,
            'monthly_allocations': monthly_allocations
        }
    except Exception as e:
        frappe.log_error(f"System validation error: {str(e)}", "System Validation")
        return {
            'success': False,
            'type': 'systemError',
            'error': str(e)
        }

@frappe.whitelist()
def debug_budget_validation(po_doc, items):
    """
    Debug version that returns detailed information for troubleshooting
    """
    try:
        if isinstance(po_doc, str):
            po_doc = frappe.parse_json(po_doc)
        if isinstance(items, str):
            items = frappe.parse_json(items)
            
        transaction_date = po_doc.get('transaction_date')
        po_name = po_doc.get('name')
        fiscal_year = transaction_date.split('-')[0]
        
        # Step by step debug
        debug_info = {
            'step1_existing_po_data': get_monthly_po_data(transaction_date, po_name),
            'step2_current_items': items,
        }
        
        debug_info['step3_updated_totals'] = merge_current_items_with_existing(
            debug_info['step1_existing_po_data'], 
            items
        )
        
        debug_info['step4_budget_details'] = get_budget_details(
            debug_info['step3_updated_totals'], 
            fiscal_year
        )
        
        debug_info['step5_monthly_allocations'] = get_monthly_allocations(
            transaction_date, 
            debug_info['step4_budget_details']
        )
        
        debug_info['step6_validation_result'] = validate_against_monthly_budget(
            items, 
            debug_info['step3_updated_totals'], 
            debug_info['step5_monthly_allocations']
        )
        
        return {
            'success': True,
            'debug_info': debug_info
        }
        
    except Exception as e:
        frappe.log_error(f"Debug budget validation error: {str(e)}", "Debug Budget Validation")
        return {
            'success': False,
            'error': str(e),
            'traceback': frappe.get_traceback()
        }

def get_monthly_po_data(transaction_date, current_po_name=None):
    """
    Get all submitted PO data for the current month
    """
    date_obj = datetime.strptime(transaction_date, '%Y-%m-%d')
    start_of_month = datetime(date_obj.year, date_obj.month, 1)
    end_of_month = datetime(date_obj.year, date_obj.month + 1, 1) if date_obj.month < 12 else datetime(date_obj.year + 1, 1, 1)
    
    # Get all submitted POs for the month (excluding current PO if it's an update)
    filters = [
        ["docstatus", "=", 1],
        ["transaction_date", ">=", start_of_month.strftime('%Y-%m-%d')],
        ["transaction_date", "<", end_of_month.strftime('%Y-%m-%d')]
    ]
    
    if current_po_name:
        filters.append(["name", "!=", current_po_name])
    
    po_list = frappe.get_list(
        "Purchase Order",
        filters=filters,
        fields=["name"],
        limit_page_length=10000
    )
    
    results = {}
    
    for po in po_list:
        po_doc = frappe.get_doc("Purchase Order", po.name)
        
        for item in po_doc.items:
            cost_center = item.cost_center
            expense_account = item.expense_account
            item_code = item.item_code
            amount = item.amount or 0
            
            if cost_center and expense_account and item_code:
                if cost_center not in results:
                    results[cost_center] = {}
                if expense_account not in results[cost_center]:
                    results[cost_center][expense_account] = {}
                if item_code not in results[cost_center][expense_account]:
                    results[cost_center][expense_account][item_code] = 0
                    
                results[cost_center][expense_account][item_code] += amount
    
    return results

def merge_current_items_with_existing(existing_data, current_items):
    """
    Merge current PO items with existing monthly data
    Always return data for current items, even if no existing data
    """
    updated_results = {}
    
    for item in current_items:
        cost_center = item.get('cost_center')
        expense_account = item.get('expense_account')
        item_code = item.get('item_code')
        amount = item.get('amount', 0)
        
        if not all([cost_center, expense_account, item_code]):
            continue
            
        # Initialize nested structure
        if cost_center not in updated_results:
            updated_results[cost_center] = {}
        if expense_account not in updated_results[cost_center]:
            updated_results[cost_center][expense_account] = {}
        if item_code not in updated_results[cost_center][expense_account]:
            updated_results[cost_center][expense_account][item_code] = 0
        
        # Add existing amount (if any) plus current amount
        existing_amount = 0
        if (existing_data and 
            cost_center in existing_data and 
            expense_account in existing_data[cost_center] and 
            item_code in existing_data[cost_center][expense_account]):
            existing_amount = existing_data[cost_center][expense_account][item_code]
        
        updated_results[cost_center][expense_account][item_code] = existing_amount + amount
    
    return updated_results

def get_budget_details(updated_totals, fiscal_year):
    """
    Get budget details for the relevant cost centers and accounts
    """
    budget_details = []
    processed_accounts = set()  # Track processed accounts to avoid duplicates
    
    for cost_center in updated_totals:
        # Get budgets for this cost center
        budgets = frappe.get_list(
            "Budget",
            filters=[
                ["docstatus", "=", 1],
                ["fiscal_year", "=", fiscal_year],
                ["cost_center", "=", cost_center],
                ["applicable_on_purchase_order", "=", 1]
            ],
            fields=["name", "cost_center", "custom_action_if__monthly_budget_exceeded_on_po"]
        )
        
        frappe.logger().info(f"Found {len(budgets)} budgets for cost center: {cost_center}")
        
        for budget in budgets:
            budget_doc = frappe.get_doc("Budget", budget.name)
            
            # Get accounts that match our expense accounts
            for account_row in budget_doc.accounts:
                expense_account = account_row.account
                
                # Create unique key to avoid duplicate processing
                account_key = f"{cost_center}||{expense_account}"
                
                # Check if this expense account exists in our current items AND not already processed
                if (expense_account in updated_totals[cost_center] and 
                    account_key not in processed_accounts):
                    
                    processed_accounts.add(account_key)
                    frappe.logger().info(f"Adding budget detail for account: {expense_account}, cost center: {cost_center}")
                    
                    budget_details.append({
                        'account': expense_account,
                        'cost_center': cost_center,
                        'budget_amount': account_row.budget_amount or 0,
                        'monthly_distribution': account_row.custom_monthly_distribution,
                        'budget_name': budget.name,
                        'action_if_exceeded': budget.custom_action_if__monthly_budget_exceeded_on_po or "Warn"
                    })
                elif account_key in processed_accounts:
                    frappe.logger().info(f"Skipping duplicate account: {expense_account}, cost center: {cost_center}")
    
    frappe.logger().info(f"Total budget details found: {len(budget_details)}")
    return budget_details

def get_monthly_allocations(transaction_date, budget_details):
    """
    Calculate monthly budget allocations based on monthly distribution
    """
    date_obj = datetime.strptime(transaction_date, '%Y-%m-%d')
    current_month = date_obj.strftime('%B')  # Full month name
    
    monthly_allocations = []
    
    for budget in budget_details:
        allocated_amount = 0
        
        if budget['monthly_distribution']:
            # Get monthly distribution document
            monthly_dist = frappe.get_doc("Monthly Distribution", budget['monthly_distribution'])
            
            # Find percentage for current month
            month_percentage = 0
            for percentage_row in monthly_dist.percentages:
                if percentage_row.month == current_month:
                    month_percentage = percentage_row.percentage_allocation or 0
                    break
            
            allocated_amount = (month_percentage * budget['budget_amount']) / 100
        else:
            # Equal distribution if no monthly distribution specified
            allocated_amount = budget['budget_amount'] / 12
        
        monthly_allocations.append({
            'account': budget['account'],
            'cost_center': budget['cost_center'],
            'monthly_budget': allocated_amount,
            'budget_name': budget['budget_name'],
            'month': current_month,
            'action_if_exceeded': budget['action_if_exceeded']
        })
    
    return monthly_allocations

# def validate_against_monthly_budget(current_items, updated_totals, monthly_allocations):
#     """
#     Validate current items against monthly budget allocations
#     """
#     warnings = []
#     stops = []
#     processed_combinations = set()  # Track processed combinations to avoid duplicates
    
#     frappe.logger().info(f"Validating {len(current_items)} items against {len(monthly_allocations)} allocations")
    
#     # Group items by cost_center + expense_account to avoid duplicates
#     grouped_items = {}
#     for item in current_items:
#         cost_center = item.get('cost_center')
#         expense_account = item.get('expense_account')
#         item_code = item.get('item_code')
#         current_amount = item.get('amount', 0)
        
#         if not all([cost_center, expense_account, item_code]):
#             frappe.logger().info(f"Skipping item due to missing data: {item}")
#             continue
        
#         # Create a unique key for this combination
#         key = f"{cost_center}||{expense_account}"
        
#         if key not in grouped_items:
#             grouped_items[key] = {
#                 'cost_center': cost_center,
#                 'expense_account': expense_account,
#                 'items': []
#             }
        
#         grouped_items[key]['items'].append({
#             'item_code': item_code,
#             'amount': current_amount
#         })
    
#     # Process each unique cost_center + expense_account combination
#     for key, group in grouped_items.items():
#         cost_center = group['cost_center']
#         expense_account = group['expense_account']
        
#         # Find matching allocation
#         matching_allocation = None
#         for allocation in monthly_allocations:
#             if (allocation['account'] == expense_account and 
#                 allocation['cost_center'] == cost_center):
#                 matching_allocation = allocation
#                 break
        
#         if not matching_allocation:
#             frappe.logger().info(f"No budget allocation found for account: {expense_account}, cost center: {cost_center}")
#             continue
        
#         # Calculate total for all items in this group
#         total_current_amount = sum(item['amount'] for item in group['items'])
#         monthly_budget = matching_allocation['monthly_budget']
        
#         # Get total from updated_totals (this includes existing + current)
#         total_after_po = 0
#         if (cost_center in updated_totals and 
#             expense_account in updated_totals[cost_center]):
#             total_after_po = sum(updated_totals[cost_center][expense_account].values())
        
#         already_spent = total_after_po - total_current_amount
        
#         frappe.logger().info(f"Budget validation for {expense_account}: Budget={monthly_budget}, Already Spent={already_spent}, Current Total={total_current_amount}, Total After PO={total_after_po}")
        
#         if total_after_po > monthly_budget:
#             # Get representative item (first one) for the message
#             representative_item = group['items'][0]
            
#             excess_data = {
#                 'item_code': representative_item['item_code'],
#                 'cost_center': cost_center,
#                 'expense_account': expense_account,
#                 'monthly_budget': monthly_budget,
#                 'already_spent': already_spent,
#                 'current_amount': total_current_amount,
#                 'total_after_po': total_after_po,
#                 'excess_amount': total_after_po - monthly_budget,
#                 'month': matching_allocation['month'],
#                 'budget_name': matching_allocation['budget_name'],
#                 'item_count': len(group['items'])  # Show how many items are involved
#             }
            
#             if matching_allocation['action_if_exceeded'] == 'Stop':
#                 frappe.logger().info(f"Adding to STOPS: {expense_account} exceeds budget")
#                 stops.append(excess_data)
#             else:
#                 frappe.logger().info(f"Adding to WARNINGS: {expense_account} exceeds budget")
#                 warnings.append(excess_data)
#         else:
#             frappe.logger().info(f"✅ {expense_account} is within budget")
    
#     frappe.logger().info(f"Validation complete: {len(stops)} stops, {len(warnings)} warnings")
    
#     return {
#         'warnings': warnings,
#         'stops': stops,
#         'has_stops': len(stops) > 0,
#         'has_warnings': len(warnings) > 0
#     }
def validate_against_monthly_budget(current_items, updated_totals, monthly_allocations):
    warnings = []
    stops = []
    print('yesssssssssssssssssssssss')
    # Group items by cost_center + expense_account once
    grouped = {}
    for item in current_items:
        cc, acc = item.get("cost_center"), item.get("expense_account")
        amt = item.get("amount", 0)
        if not (cc and acc):
            continue
        grouped.setdefault((cc, acc), 0)
        grouped[(cc, acc)] += amt

    for (cost_center, expense_account), current_total in grouped.items():
        # Find allocation
        allocation = next(
            (a for a in monthly_allocations 
             if a["account"] == expense_account and a["cost_center"] == cost_center),
            None
        )
        if not allocation:
            continue

        monthly_budget = allocation["monthly_budget"]
        total_after_po = sum(updated_totals[cost_center][expense_account].values())
        already_spent = total_after_po - current_total

        if total_after_po > monthly_budget:
            excess_data = {
                "item_code": None,  # or representative one
                "cost_center": cost_center,
                "expense_account": expense_account,
                "monthly_budget": monthly_budget,
                "already_spent": already_spent,
                "current_amount": current_total,
                "total_after_po": total_after_po,
                "excess_amount": total_after_po - monthly_budget,
                "month": allocation["month"],
                "budget_name": allocation["budget_name"],
            }
            if allocation["action_if_exceeded"] == "Stop":
                stops.append(excess_data)
            else:
                warnings.append(excess_data)
    print('warnings',warnings)
    print("stops", stops)
    print("has_stops",  bool(stops))
    print("has_warnings",  bool(warnings))
    # print("DEBUG CALL STACK:\n", traceback.format_stack())
    return {
        "warnings": warnings,
        "stops": stops,
        "has_stops": bool(stops),
        "has_warnings": bool(warnings),
    }

@frappe.whitelist()
def get_budget_summary(cost_center, fiscal_year, transaction_date):
    """
    Get budget summary for a specific cost center and month
    """
    try:
        date_obj = datetime.strptime(transaction_date, '%Y-%m-%d')
        current_month = date_obj.strftime('%B')
        
        # Get existing PO data for the month
        existing_po_data = get_monthly_po_data(transaction_date)
        
        # Get budget details
        budget_details = []
        budgets = frappe.get_list(
            "Budget",
            filters=[
                ["docstatus", "=", 1],
                ["fiscal_year", "=", fiscal_year],
                ["cost_center", "=", cost_center],
                ["applicable_on_purchase_order", "=", 1]
            ],
            fields=["name"]
        )
        
        summary = []
        
        for budget in budgets:
            budget_doc = frappe.get_doc("Budget", budget.name)
            
            for account_row in budget_doc.accounts:
                expense_account = account_row.account
                
                # Calculate monthly allocation
                allocated_amount = 0
                if account_row.custom_monthly_distribution:
                    monthly_dist = frappe.get_doc("Monthly Distribution", account_row.custom_monthly_distribution)
                    for percentage_row in monthly_dist.percentages:
                        if percentage_row.month == current_month:
                            allocated_amount = (percentage_row.percentage_allocation * account_row.budget_amount) / 100
                            break
                else:
                    allocated_amount = account_row.budget_amount / 12
                
                # Calculate spent amount
                spent_amount = 0
                if (cost_center in existing_po_data and 
                    expense_account in existing_po_data[cost_center]):
                    for item_code, amount in existing_po_data[cost_center][expense_account].items():
                        spent_amount += amount
                
                summary.append({
                    'account': expense_account,
                    'budget_amount': account_row.budget_amount,
                    'monthly_allocation': allocated_amount,
                    'spent_amount': spent_amount,
                    'remaining': allocated_amount - spent_amount,
                    'month': current_month
                })
        
        return {
            'success': True,
            'summary': summary,
            'cost_center': cost_center,
            'month': current_month
        }
        
    except Exception as e:
        frappe.log_error(f"Budget summary error: {str(e)}", "Budget Summary")
        return {
            'success': False,
            'error': str(e)
        }