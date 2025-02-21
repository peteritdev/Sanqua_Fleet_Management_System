# Custom from SanQua MIS
# Author : Peter Susanto
{
    'name': 'Fleet Vehicle Inherited',
    'version': '1.0',
    'category': 'Fleet Vehicle',
    'summary': 'Inherited from fleet vehicle to handle STNK, KIR, SPKB',
    'depends': [
        'fleet', 'esanqua_lib','hr', 'stock', 'maintenance'
    ],
    'data': [
        'data/ir_sequence.xml',
        'views/fleet_vehicle_view.xml',
        'views/fleet_vehicle_log_service_view.xml',
        'views/maintenance_request_inherited_view.xml',
        'views/master_problem.xml',
        'views/stock_picking_inherited_view.xml',
        'security/ir.model.access.csv',
    ],
#     'assets': {
#     'web.assets_backend': [
#         'fleet_vehicle/static/src/js/calendar_with_recurrence_model.js',  # File override
#     ],
# },
    'installable': True,
    'auto_install': False,
    'application': True
}