# Custom from SanQua MIS
# Author : Hafizh Hasan A R
{
    'name': 'Form Lembar Pemeriksaan Bulanan Kendaraan',
    'version': '1.0',
    'category': 'Fleet Vehicle',
    'summary': 'Form Lembar Pemeriksaan Bulanan Kendaraan',
    'depends': [
        'fleet','hr', 'stock', 'maintenance'
    ],
    'data': [
        'reports/template_monthly_check.xml',
        'views/category_request.xml',
        'views/componen_request.xml',
        'views/template_checkup.xml',
        'views/maintenance_request_inherited_view.xml',
        'views/fleet_vehicle_log_service_view.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}