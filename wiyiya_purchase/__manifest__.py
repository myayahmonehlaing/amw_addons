{
    "name": "wiyiya",
    "installed_version": "1.0",
    "category": "Purchase",
    "summary": "Add user department selection in purchase Order",
    "depends": ["base","purchase","hr"],
    "data": [
        "security/ir.model.access.csv",
        "security/purchase_security.xml",
        "views/purchase_order.xml"
    ],
    "installable": True,
    "application": False,
}
