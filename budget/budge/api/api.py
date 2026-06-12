import frappe
from frappe import _
from functools import wraps

@frappe.whitelist()
def get_items_per_department(department):
    item = frappe.qb.DocType("Item")
    item_department = frappe.qb.DocType("Item Department")
    item_default = frappe.qb.DocType("Item Default")
    items = frappe.qb.from_(item).join(item_department).on(
        item_department.parent == item.name).join(item_default).on(
            item.name == item_default.parent).select(
                item.name, item_default.expense_account).where(
                    item_department.department == department).distinct().run(   #.where(item.custom_is_budget == 1) remove this
                            as_dict=True)

    return items


@frappe.whitelist()
def get_expected_price(item_name, price_list):
    expected = frappe.get_doc("")


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not frappe.session.user or frappe.session.user == "Guest":
            frappe.throw("❌ You are not allowed to access this method.")
        return fn(*args, **kwargs)
    return wrapper


# # 1. تحقق من وجود البيانات في قاعدة البيانات
# def check_user_data(email):
#     # استعلام للتحقق من البيانات
#     query = "SELECT * FROM user_data WHERE email = %s"
#     result = execute_query(query, (email,))
#     return result

#     # 2. إضافة معالجة للأخطاء
#     try:
#         user_data = get_user_data(email)
#         if not user_data.get('data'):
#             print("لا توجد بيانات لهذا المستخدم")
#             # إجراء بديل أو إنشاء بيانات افتراضية
#     except Exception as e:
#         print(f"خطأ في استرجاع البيانات: {e}")

#     # 3. تحقق من صحة معرف الجلسة
#     if user_info['sid'] == user_info['user']:
#         # هذا طبيعي إذا كان sid هو نفس البريد الإلكتروني
#         pass