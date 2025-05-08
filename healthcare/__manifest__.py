{
    "name": "Health Care Management",
    'author': "SME Intellect Co. Ltd",
    'website': "https://www.smeintellect.com/",
    "installed_version": "1.0",
    "category": "All",
    "license": 'LGPL-3',
    "summary": """
    
    """,

    # |-------------------------------------------------------------------------
    # | Dependencies
    # |-------------------------------------------------------------------------
    "depends": ["base", "sale", "account", "mail", "product"],

    # |-------------------------------------------------------------------------
    # | Data References
    # |-------------------------------------------------------------------------
    "data": [
        # Data
        'data/ir_sequence.xml',

        # Views
        "views/healthcare_facility_views.xml",
        "views/healthcare_resources_views.xml",
        "views/healthcare_providers_speciality_views.xml",
        "views/healthcare_providers_views.xml",
        "views/healthcare_visit_types_views.xml",
        "views/healthcare_schedule_rules_views.xml",
        "views/healthcare_appointment_status_views.xml",
        "views/healthcare_patients.xml",
        "views/healthcare_appointments_views.xml",
        "views/healthcare_images_views.xml",
        "views/healthcare_billing_views.xml",
        "views/healthcare_labs_views.xml",
        "views/healthcare_patients.xml",
        "views/healthcare_procedures_views.xml",
        "views/healthcare_product_views.xml",
        "views/res_config_settings_views.xml",
        "views/sale_order.xml",
        "views/account_move.xml",

        #report
        "report/ir_action_report.xml",

        # MenuItems
        "views/menu_items.xml",

        # Security
        "security/ir.model.access.csv",
        "security/security.xml",
    ],
    "installable": True,
    "application": True,
}
