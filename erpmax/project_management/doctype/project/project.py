import frappe
from frappe.model.document import Document

class Project(Document):
    def before_save(self):
        if not self.cost_centre:
            self.create_cost_centre()

    def create_cost_centre(self):
        cc_name = "{0} - {1}".format(self.project_name, self.company)
        if not frappe.db.exists("Cost Centre", cc_name):
            cc = frappe.new_doc("Cost Centre")
            cc.cost_centre_name = cc_name
            cc.company = self.company
            cc.project = self.name
            cc.description = "Auto-created for project: {0}".format(self.project_name)
            cc.insert()
            frappe.db.commit()
            self.cost_centre = cc.name
        else:
            self.cost_centre = cc_name
