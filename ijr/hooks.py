from . import __version__ as app_version

app_name = "ijr"
app_title = "India Justice Report"
app_publisher = "Frappe Technologies Pvt. Ltd."
app_description = "The India Justice Report ranks 18 large and 7 small states according to their capacity to deliver justice to all"
app_email = "faris@frappe.io"
app_license = "AGPLv3"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ijr/css/ijr.css"
# app_include_js = "/assets/ijr/js/ijr.js"

# include js, css files in header of web template
web_include_css = "/assets/ijr/css/ijr.css"
web_include_js = "/assets/ijr/js/ijr.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ijr/public/scss/website"

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

website_route_rules = [
    {"from_route": "/rankings/ijr-<int:ijr_number>/<rank_by>/<cluster>/<view>", "to_route": "rankings"},

	{"from_route": "/state/<state>", "to_route": "state"},
	{"from_route": "/state/<state>/ijr-<int:ijr_number>", "to_route": "state"},
	{"from_route": "/state/<state>/ijr-<int:ijr_number>/<pillar_or_theme>", "to_route": "state"},

	{"from_route": "/indicator/<indicator_id>", "to_route": "indicator"},
	{"from_route": "/indicator/<indicator_id>/ijr-<int:ijr_number>/<cluster>/<view>", "to_route": "indicator"},

	{"from_route": "/pictures/theme/<theme>", "to_route": "pictures"},
	{"from_route": "/pictures/i/<picture_id>", "to_route": "pictures"},
]

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
	"methods": "ijr.jinja_helpers"
}

# Installation
# ------------

# before_install = "ijr.install.before_install"
# after_install = "ijr.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "ijr.uninstall.before_uninstall"
# after_uninstall = "ijr.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ijr.notifications.get_notification_config"

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
#		"ijr.tasks.all"
#	],
#	"daily": [
#		"ijr.tasks.daily"
#	],
#	"hourly": [
#		"ijr.tasks.hourly"
#	],
#	"weekly": [
#		"ijr.tasks.weekly"
#	],
#	"monthly": [
#		"ijr.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "ijr.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "ijr.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "ijr.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


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
#	"ijr.auth.validate"
# ]

fixtures = [
	"State Cluster",
	"Pillar",
	"Theme"
]