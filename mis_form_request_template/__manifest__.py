# Custom from SanQua MIS
# Author : Hafizh Hasan A R
{
    'name': 'Form Request Maintenance Template Inherited',
    'version': '1.0',
    'category': 'Fleet Vehicle',
    'summary': 'Form Request Maintenance Template Inherited',
    'depends': [
        'fleet','hr', 'stock'
    ],
    'data': [
        'reports/template_service_request_inherit.xml',
        'views/maintenance_request_inherited_view.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}