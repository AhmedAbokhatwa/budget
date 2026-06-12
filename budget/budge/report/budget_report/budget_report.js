frappe.query_reports["Budget Report"] = {
    filters: [
        {
            fieldname: "department",
            label: __("Department"),
            fieldtype: "MultiSelectList",
            reqd: 0,
            get_data: function(txt) {
                return frappe.db.get_link_options("Department", txt);
            }
        }
    ]
};