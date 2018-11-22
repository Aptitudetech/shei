#-*- coding: utf-8 -*-

import frappe

def get_product_configurator_permissions_query_conditions(user):
        if not user:
                user = frappe.session.user

        if 'Product Configurator Customer' in frappe.get_roles(user):
                pcu = frappe.db.exists("Product Configurator User", {"pc_user_email": user})
                if pcu:
                        return '''(`tabProduct Configurator`.name = "{pcu}")'''.format(pcu=frappe.db.escape(pcu))


def has_permission_to_product_configurator(doc, user):
        if 'Product Configurator Customer' in frappe.get_roles(user):
                pcu = frappe.db.exists("Product Configurator", { "pc_user_email": user })
                if pcu:
                        return doc.name == pcu
