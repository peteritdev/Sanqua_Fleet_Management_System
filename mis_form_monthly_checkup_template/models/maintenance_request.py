import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
_logger = logging.getLogger(__name__)

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'
    _description = 'Inherit from maintenance request'

    
    fleet_vehicle_checkup_request_ids = fields.One2many('fleet.vehicle.checkup.request', 'maintenance_request_id', string='Check Up Request')
    template_monthly_checkup_id = fields.Many2one('template.monthly.checkup', string='Template Monthly Check Up', domain="[('company_ids', 'in', company_id)]")



    def write(self, vals):
        """Mengupdate fleet_vehicle_checkup_request_ids setelah perubahan disimpan."""
        res = super(MaintenanceRequest, self).write(vals)
        if 'maintenance_type' in vals and vals['maintenance_type'] == 'corrective':
            for rec in self:
                rec.fleet_vehicle_checkup_request_ids.unlink()  # Hapus semua record terkait
                
        if 'template_monthly_checkup_id' in vals:
            self._update_checkup_requests()
        return res

    def create(self, vals):
        """Mengisi fleet_vehicle_checkup_request_ids saat membuat record baru."""
        record = super(MaintenanceRequest, self).create(vals)
        record._update_checkup_requests()
        return record
    
    def _update_checkup_requests(self):
        """Update fleet_vehicle_checkup_request_ids berdasarkan pilihan template."""
        FleetVehicleCheckupRequest = self.env['fleet.vehicle.checkup.request']

        for rec in self:
            rec.fleet_vehicle_checkup_request_ids.unlink()  

            if not rec.template_monthly_checkup_id:
                continue  # Jika tidak ada template yang dipilih, lanjutkan

            template_lines = rec.template_monthly_checkup_id.template_monthly_line_ids

            if not template_lines:
                continue  # Jika tidak ada data di template, lanjutkan

            checkup_requests = []
            for line in template_lines:
                if not line.component_checkup_request_id or not line.category_checkup_request_id:
                    continue  # Jika salah satu tidak ada, skip

                checkup_requests.append((0, 0, {
                    'maintenance_request_id': rec.id,
                    'component_checkup_request_id': line.component_checkup_request_id.id,
                    'category_checkup_request_id': line.category_checkup_request_id.id,
                }))

            if checkup_requests:
                rec.fleet_vehicle_checkup_request_ids = checkup_requests

    







    


    


        

            



