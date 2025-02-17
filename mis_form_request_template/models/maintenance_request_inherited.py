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

    # def get_cleaned_notes(self):
    #     """
    #     Menambahkan 'margin-bottom: 0px;' pada tag <p> yang ada di field 'notes'.
    #     """
    #     if self.description:
    #         clean_text = re.sub(r'<p(?![^>]*style=)', r'<p style="margin-bottom: 0px;"', self.description)
    #         clean_text = re.sub(r'(<p[^>]*style=")([^"]*)"', r'\1margin-bottom: 0px; \2"', clean_text)
    #         return clean_text.strip()
    #     return ''

        
        
