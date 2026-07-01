from . import __version__ as app_version

app_name = "budget"
app_title = "Budget Expenses"
app_publisher = "ahmed"
app_description = "Department-level monthly budget management for ERPNext. Allocate and adjust budgets month by month per department, with built-in increase/decrease control and a complete audit log for every change."
app_email = "ahmed"
app_license = "MIT"

# Includes in <head>
# ------------------
required_apps = ["erpnext"]
add_to_apps_screen = [
    {
        "name": "budget_controller",
        "logo": "/assets/budget/images/budget_icon.png",
        "title": "Budget Expenses",
        "route": "/desk/budget-expenses",
    }
]
# include js, css files in header of desk.html
# app_include_css = "/assets/budget/css/budget.css"
# app_include_js = "/assets/budget/js/budget.js"

# include js, css files in header of web template
# web_include_css = "/assets/budget/css/budget.css"
# web_include_js = "/assets/budget/js/budget.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "budget/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "budget.utils.jinja_methods",
#	"filters": "budget.utils.jinja_filters"
# }

# Installation
# ------------
after_install = "budget.budget_control.after_install"

# Uninstallation
# ------------

# before_uninstall = "budget.uninstall.before_uninstall"
before_uninstall = "budget.budget_control.before_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "budget.utils.before_app_install"
# after_app_install = "budget.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "budget.utils.before_app_uninstall"
# after_app_uninstall = "budget.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "budget.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events
doc_events = {
    "Department": {
        "after_insert": "budget.budget.event.department.create_Head_role_for_department"
    }
}

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"budget.tasks.all"
#	],
#	"daily": [
#		"budget.tasks.daily"
#	],
#	"hourly": [
#		"budget.tasks.hourly"
#	],
#	"weekly": [
#		"budget.tasks.weekly"
#	],
#	"monthly": [
#		"budget.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "budget.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "budget.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "budget.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["budget.utils.before_request"]
# after_request = ["budget.utils.after_request"]

# Job Events
# ----------
# before_job = ["budget.utils.before_job"]
# after_job = ["budget.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"budget.auth.validate"
# ]

# after_migrate = "budget.budget.setup_config.run"

fixtures = [
    {
        "dt": "DocType Link",
        "filters": [["parent", "in", ["Budget Request"]]]
    },
    {
        "dt": "Client Script",
        "filters": [
            ["module", "=", "budget"]
        ]
    },
]
