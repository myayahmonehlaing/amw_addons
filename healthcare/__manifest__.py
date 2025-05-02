{
    "name": "Charm EHR",
    "author": "smei",
    "installed_version": "1.0",
    "category": "All",
    "license": 'LGPL-3',
    "summary": """
    
    """,

    # |-------------------------------------------------------------------------
    # | Dependencies
    # |-------------------------------------------------------------------------
    "depends": ["base", "sale", "mail", "product"],

    # |-------------------------------------------------------------------------
    # | Data References
    # |-------------------------------------------------------------------------
    "data": [
        # Views
        "views/healthcare_facility_views.xml",
        "views/healthcare_resources_views.xml",
        "views/healthcare_providers_views.xml",
        "views/healthcare_visit_types_views.xml",
        "views/healthcare_schedule_rules_views.xml",
        "views/healthcare_appointment_status_views.xml",
        "views/healthcare_appointment_status_patients.xml",
        "views/healthcare_appointments_views.xml",
        "views/healthcare_images_views.xml",
        "views/healthcare_billing_views.xml",
        "views/healthcare_labs_views.xml",
        "views/healthcare_appointment_status_patients.xml",
        "views/healthcare_appointment_procedures_views.xml",
        "views/healthcare_appointment_product_views.xml",
        "views/res_config_settings_views.xml",

        # MenuItems
        "views/menu_items.xml",

        # Security
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": True,
}
