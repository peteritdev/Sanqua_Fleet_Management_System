import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    def action_print_service_report(self):
        """ Generate Service Report PDF """
        return self.env.ref('mis_form_service_report_template.action_template_service_report').report_action(self)

        
        
