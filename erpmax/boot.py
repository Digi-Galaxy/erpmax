import frappe


def boot_session(bootinfo):
    bootinfo.app_name = "ERPMax"
    bootinfo.app_version = "0.0.1"
