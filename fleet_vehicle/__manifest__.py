# Custom from SanQua MIS
# Author : Peter Susanto
{
    'name': 'Fleet Vehicle Inherited',
    'version': '1.0',
    'category': 'Fleet Vehicle',
    'summary': 'Inherited from fleet vehicle to handle STNK, KIR, SPKB',
    'depends': [
        'fleet', 'esanqua_lib','hr', 'stock'
    ],
    'data': [
        'data/ir.sequence.xml',
        'views/fleet_vehicle_view.xml',
        'views/fleet_vehicle_log_service_view.xml',
        'views/maintenance_request_inherited_view.xml',
        'views/stock_picking_inherited_view.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}