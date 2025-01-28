# Custom from SanQua MIS
# Author : Peter Susanto
{
    'name': 'HR Employee Inherited',
    'version': '1.0',
    'category': 'Fleet Vehicle',
    'summary': 'Inherited from fleet vehicle to handle STNK, KIR, SPKB',
    'depends': [
        'esanqua_lib'
    ],
    'data': [
        'wizard/wizard_sync_employee_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}