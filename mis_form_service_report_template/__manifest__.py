# Custom from SanQua MIS
# Author : Hafizh Hasan A R
{
    'name': 'Form Lembar Laporan Service Kendaraan',
    'version': '1.0',
    'category': 'Fleet Vehicle',
    'summary': 'Form Lembar Laporan Service Kendaraan',
    'depends': [
        'fleet','hr', 'stock'
    ],
    'data': [
        'reports/template_service_report.xml',
        'views/maintenance_service_report_inherited_view.xml',
        # 'security/ir.model.access.csv'
    ],
    'assets': {
        'web.assets_backend': [
            'maintenance/static/src/**/*',
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True
}