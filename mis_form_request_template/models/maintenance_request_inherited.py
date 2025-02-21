import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
import re
_logger = logging.getLogger(__name__)

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'
    _description = 'Inherit from maintenance request'


    show_print_button = fields.Boolean(
        string="Show Print Button",
        compute="_compute_show_print_button",
        store=False
    )

    @api.depends('maintenance_type')
    def _compute_show_print_button(self):
        """ Menampilkan tombol hanya jika asset_type = 'corrective' """
        for record in self:
            record.show_print_button = True if record.maintenance_type == 'corrective' else False

    def print_template_service_request(self):
        """Method to print the service request template"""
        self.ensure_one()
        report_action = self.env.ref('mis_form_request_template.action_template_service_request')
        if not report_action:
            _logger.error("Report template_service_request not found!")
            return False
        return report_action.report_action(self)

    
        
