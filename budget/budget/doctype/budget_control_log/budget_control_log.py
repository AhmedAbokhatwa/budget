import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate, now_datetime

class BudgetControlLog(Document):
    """Budget Control Log Document Controller"""

    def before_save(self):
        """Execute before saving the document"""
        self.calculate_change_amount()
        self.set_defaults()
        self.validate_amounts()

    def before_submit(self):
        """Execute before submitting the document"""
        self.validate_permissions()
        self.update_budget_amount()

    def on_submit(self):
        """Execute after submitting the document"""
        self.send_notification()
        self.update_budget_cache()

    def on_cancel(self):
        """Execute when cancelling the document"""
        self.reverse_budget_changes()
        self.send_cancellation_notification()

    def calculate_change_amount(self):
        """Calculate the change amount"""
        old_amount = flt(self.old_amount or 0)
        new_amount = flt(self.new_amount or 0)
        # self.change_amount = new_amount - old_amount

    def set_defaults(self):
        """Set default values"""
        if not self.changed_by:
            self.changed_by = frappe.session.user

        if not self.change_date:
            self.change_date = nowdate()

        if not self.change_time:
            self.change_time = now_datetime().strftime("%H:%M:%S")

    def validate_amounts(self):
        """Validate amount values"""
        if flt(self.new_amount) < 0:
            frappe.throw(_("New amount cannot be negative"))

        if not self.new_amount:
            frappe.throw(_("New amount is required"))

    def validate_permissions(self):
        """Validate user permissions"""
        if not frappe.has_permission("Budget", "write"):
            frappe.throw(_("You don't have permission to update budget amounts"))

        # Check cost center permissions
        if self.cost_center and not frappe.has_permission("Cost Center", "read", self.cost_center):
            frappe.throw(_("You don't have permission to access this Cost Center"))

    def update_budget_amount(self):
        """Update the actual budget amount"""
        try:
            if self.budget:
                budget_doc = frappe.get_doc("Budget", self.budget)

                # Find the budget account and update
                for account in budget_doc.accounts:
                    if account.account == self.account:
                        account.budget_amount = flt(self.new_amount)
                        break
                else:
                    # Add new budget account if not found
                    budget_doc.append("accounts", {
                        "account": self.account,
                        "budget_amount": flt(self.new_amount)
                    })

                budget_doc.save(ignore_permissions=True)

        except Exception as e:
            frappe.log_error(f"Error updating budget: {str(e)}", "Budget Control Log")
            frappe.throw(_("Failed to update budget: {0}").format(str(e)))

    def send_notification(self):
        """Send notification about budget change"""
        try:
            # Get notification recipients
            recipients = self.get_notification_recipients()

            if recipients:
                subject = _("Budget Updated: {0}").format(self.cost_center)

                message = _("""
                    <h3>Budget Amount Updated</h3>
                    <p><strong>Cost Center:</strong> {0}</p>
                    <p><strong>Account:</strong> {1}</p>
                    <p><strong>Item Code:</strong> {2}</p>
                    <p><strong>Month:</strong> {3}</p>
                    <p><strong>Old Amount:</strong> {4}</p>
                    <p><strong>New Amount:</strong> {5}</p>
                    <p><strong>Change:</strong> {6}</p>
                    <p><strong>Changed By:</strong> {7}</p>
                    <p><strong>Date:</strong> {8}</p>
                    {9}
                """).format(
                    self.cost_center or "N/A",
                    self.account or "N/A",
                    self.item_code or "N/A",
                    self.month or "N/A",
                    frappe.format_value(self.old_amount, "Currency"),
                    frappe.format_value(self.new_amount, "Currency"),
                    frappe.format_value(self.change_amount, "Currency"),
                    self.changed_by,
                    frappe.format_value(self.change_date, "Date"),
                    f"<p><strong>Comments:</strong> {self.comments}</p>" if self.comments else ""
                )

                frappe.sendmail(
                    recipients=recipients,
                    subject=subject,
                    message=message,
                    reference_doctype=self.doctype,
                    reference_name=self.name
                )

        except Exception as e:
            frappe.log_error(f"Error sending notification: {str(e)}", "Budget Control Log Notification")

    def get_notification_recipients(self):
        """Get list of users to notify"""
        recipients = []

        try:
            # Get Budget Managers
            budget_managers = frappe.get_all("Has Role",
                filters={"role": "Budget Manager"},
                fields=["parent"]
            )
            recipients.extend([user.parent for user in budget_managers])

            # Get Accounts Managers
            accounts_managers = frappe.get_all("Has Role",
                filters={"role": "Accounts Manager"},
                fields=["parent"]
            )
            recipients.extend([user.parent for user in accounts_managers])

            # Get Cost Center managers if available
            if self.cost_center:
                cost_center_doc = frappe.get_doc("Cost Center", self.cost_center)
                if hasattr(cost_center_doc, 'manager') and cost_center_doc.manager:
                    recipients.append(cost_center_doc.manager)

            # Remove duplicates and current user
            recipients = list(set(recipients))
            if frappe.session.user in recipients:
                recipients.remove(frappe.session.user)

            return recipients

        except Exception as e:
            frappe.log_error(f"Error getting notification recipients: {str(e)}", "Budget Control Log")
            return []

    def reverse_budget_changes(self):
        """Reverse budget changes when cancelled"""
        try:
            if self.budget and self.old_amount is not None:
                budget_doc = frappe.get_doc("Budget", self.budget)

                # Revert to old amount
                for account in budget_doc.accounts:
                    if account.account == self.account:
                        account.budget_amount = flt(self.old_amount)
                        break

                budget_doc.save(ignore_permissions=True)

        except Exception as e:
            frappe.log_error(f"Error reversing budget changes: {str(e)}", "Budget Control Log")

    def send_cancellation_notification(self):
        """Send notification about budget change cancellation"""
        try:
            recipients = self.get_notification_recipients()

            if recipients:
                subject = _("Budget Update Cancelled: {0}").format(self.cost_center)

                message = _("""
                    <h3>Budget Update Cancelled</h3>
                    <p><strong>Cost Center:</strong> {0}</p>
                    <p><strong>Account:</strong> {1}</p>
                    <p><strong>Amount Reverted to:</strong> {2}</p>
                    <p><strong>Cancelled By:</strong> {3}</p>
                    <p><strong>Cancellation Date:</strong> {4}</p>
                """).format(
                    self.cost_center or "N/A",
                    self.account or "N/A",
                    frappe.format_value(self.old_amount, "Currency"),
                    frappe.session.user,
                    frappe.format_value(nowdate(), "Date")
                )

                frappe.sendmail(
                    recipients=recipients,
                    subject=subject,
                    message=message,
                    reference_doctype=self.doctype,
                    reference_name=self.name
                )

        except Exception as e:
            frappe.log_error(f"Error sending cancellation notification: {str(e)}", "Budget Control Log")

    def update_budget_cache(self):
        """Update budget cache after changes"""
        try:
            if self.cost_center:
                cache_keys = [
                    f"budget_data_{self.cost_center}",
                    f"monthly_dist_{self.cost_center}",
                    "budget_summary"
                ]

                for key in cache_keys:
                    frappe.cache().delete_key(key)

        except Exception as e:
            frappe.log_error(f"Error updating cache: {str(e)}", "Budget Control Log")

@frappe.whitelist()
def get_budget_control_logs(cost_center=None, from_date=None, to_date=None, limit=50):
    """Get budget control logs with filters"""
    try:
        conditions = ["bcl.docstatus = 1"]
        values = {}

        if cost_center:
            conditions.append("bcl.cost_center = %(cost_center)s")
            values["cost_center"] = cost_center

        if from_date:
            conditions.append("bcl.change_date >= %(from_date)s")
            values["from_date"] = from_date

        if to_date:
            conditions.append("bcl.change_date <= %(to_date)s")
            values["to_date"] = to_date

        # build WHERE clause safely
        where_clause = " AND ".join(conditions)

        query = """
            SELECT
                bcl.name,
                bcl.cost_center,
                bcl.account,
                bcl.item_code,
                bcl.month,
                bcl.old_amount,
                bcl.new_amount,
                bcl.change_amount,
                bcl.changed_by,
                bcl.change_date,
                bcl.change_time,
                bcl.comments,
                u.full_name as changed_by_name
            FROM `tabBudget Control Log` bcl
            LEFT JOIN `tabUser` u ON bcl.changed_by = u.name
            WHERE %s
            ORDER BY bcl.change_date DESC, bcl.change_time DESC
            LIMIT %(limit)s
        """ % where_clause

        values["limit"] = limit

        return frappe.db.sql(query, values, as_dict=True)

    except Exception as e:
        frappe.throw(_("Error getting budget control logs"))

@frappe.whitelist()
def get_budget_change_summary(cost_center=None, period="Monthly"):
    """Get summary of budget changes"""
    try:

        date_format_map = {
            "Monthly": "%Y-%m",
            "Daily": "%Y-%m-%d"
        }

        date_format = date_format_map.get(period, "%Y-%m")

        conditions = ["bcl.docstatus = 1"]
        values = {}

        if cost_center:
            conditions.append("bcl.cost_center = %(cost_center)s")
            values["cost_center"] = cost_center

        where_clause = " AND ".join(conditions)

        query = """
            SELECT
                DATE_FORMAT(bcl.change_date, %(date_format)s) as period,
                COUNT(*) as total_changes,
                SUM(ABS(bcl.change_amount)) as total_change_amount,
                SUM(CASE WHEN bcl.change_amount > 0 THEN bcl.change_amount ELSE 0 END) as total_increases,
                SUM(CASE WHEN bcl.change_amount < 0 THEN ABS(bcl.change_amount) ELSE 0 END) as total_decreases,
                COUNT(DISTINCT bcl.cost_center) as affected_cost_centers,
                COUNT(DISTINCT bcl.account) as affected_accounts
            FROM `tabBudget Control Log` bcl
            WHERE {where_clause}
            GROUP BY DATE_FORMAT(bcl.change_date, %(date_format)s)
            ORDER BY period DESC
        """

        values["date_format"] = date_format

        return frappe.db.sql(query, values, as_dict=True)

    except Exception as e:
        frappe.log_error(
            f"Error getting budget change summary: {str(e)}",
            "Budget Control Log Summary"
        )
        return []

@frappe.whitelist()
def export_budget_changes(cost_center=None, from_date=None, to_date=None):
    """Export budget changes to Excel/CSV"""
    try:
        data = get_budget_control_logs(cost_center, from_date, to_date, limit=10000)

        if not data:
            return {"success": False, "message": "No data to export"}

        # Prepare data for export
        export_data = []
        for row in data:
            export_data.append({
                "Log ID": row.get("name"),
                "Cost Center": row.get("cost_center"),
                "Account": row.get("account"),
                "Item Code": row.get("item_code") or "N/A",
                "Month": row.get("month") or "N/A",
                "Old Amount": row.get("old_amount"),
                "New Amount": row.get("new_amount"),
                "Change Amount": row.get("change_amount"),
                "Changed By": row.get("changed_by_name") or row.get("changed_by"),
                "Change Date": row.get("change_date"),
                "Change Time": row.get("change_time"),
                "Comments": row.get("comments") or ""
            })

        # Create file
        from frappe.utils.file_manager import save_file
        import json

        file_content = json.dumps(export_data, indent=2, default=str)
        file_name = f"budget_changes_{frappe.utils.now_datetime().strftime('%Y%m%d_%H%M%S')}.json"

        file_doc = save_file(
            fname=file_name,
            content=file_content,
            dt="Budget Control Log",
            is_private=1
        )

        return {
            "success": True,
            "file_url": file_doc.file_url,
            "message": f"Exported {len(export_data)} records"
        }

    except Exception as e:
        frappe.log_error(f"Error exporting budget changes: {str(e)}", "Budget Control Log Export")
        return {"success": False, "message": str(e)}
