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
            rec.fleet_vehicle_checkup_request_ids.unlink()  # Hapus semua record terkait sebelum update

            if not rec.template_monthly_checkup_id:
                continue  # Jika tidak ada template yang dipilih, lanjutkan

            # Ambil semua baris dalam template yang dipilih
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

    # def _update_checkup_requests(self):
    #     """Update fleet_vehicle_checkup_request_ids berdasarkan pilihan template."""
    #     FleetVehicleCheckupRequest = self.env['fleet.vehicle.checkup.request']

    #     for rec in self:
    #         rec.fleet_vehicle_checkup_request_ids.unlink()

    #         if not rec.template_monthly_checkup_id:
    #             continue  # Jika tidak ada template yang dipilih, lanjutkan

    #         # Ambil semua parts dari template yang dipilih
    #         part_checkup_requests = rec.template_monthly_checkup_id.part_checkup_request_ids

    #         if not part_checkup_requests:
    #             continue  # Jika tidak ada parts, lanjutkan

    #         # Ambil semua komponen terkait part yang dipilih
    #         component_checkup_requests = self.env['component.checkup.request'].search([
    #             ('part_checkup_request_ids', 'in', part_checkup_requests.ids)
    #         ])

    #         if not component_checkup_requests:
    #             continue  # Jika tidak ada komponen, lanjutkan

    #         checkup_requests = [(0, 0, {
    #             'maintenance_request_id': rec.id,
    #             'component_checkup_request_id': component.id,
    #             'part_checkup_request_id': part.id,  
    #         }) for part in part_checkup_requests for component in component_checkup_requests if component in part.component_checkup_request_ids]

    #         rec.fleet_vehicle_checkup_request_ids = checkup_requests





    # select_template_monthly_checkup_test_id = fields.Many2one('part.checkup.request', string='Select Template')   
    # template_monthly_full = fields.Selection([
    #     ('full', 'Full Template'),
    #     ('template', 'Template')], string='Template Monthly Check Up')
    
    # template_selection = fields.Selection(selection='_get_template_selection', string='Template', store=True)
    # template_value = fields.Char(string='Template Value', compute='_compute_template_value', inverse='_inverse_template_value', store=True)

    # @api.depends('template_selection')
    # def _compute_template_value(self):
    #     """Mengisi template_value dengan format "Template: {nilai_template}"."""
    #     for record in self:
    #         if record.template_selection:
    #             record.template_value = f"Template: {record.template_selection}"
    #         else:
    #             record.maintenance_type == 'corrective' or record.template_monthly_full == 'full'
    #             record.template_value = ""

    # def _get_template_selection(self):
    #     templates = self.env['part.checkup.request'].search([])
    #     unique_templates = set(temp.template for temp in templates if temp.template)
    #     return [(temp, str(temp)) for temp in sorted(unique_templates)]
    

    # @api.onchange('template_monthly_full', 'template_selection')
    # def _onchange_template_monthly_full(self):
    #     """ Reset template_selection jika memilih 'full'. """
    #     if self.template_monthly_full == 'full':
    #         self.template_selection = False
        
    #     if self.template_selection:
    #         self.template_value = self.template_selection

    
    # def write(self, vals):
    #     """Mengupdate fleet_vehicle_checkup_request_ids setelah perubahan disimpan."""
    #     res = super(MaintenanceRequest, self).write(vals)
    #     if 'maintenance_type' in vals and vals['maintenance_type'] == 'corrective':
    #         for rec in self:
    #             rec.fleet_vehicle_checkup_request_ids.unlink()  # Hapus semua record terkait
                
    #     if 'template_monthly_full' in vals or 'template_selection' in vals:
    #         self._update_checkup_requests()
    #     return res

    # def create(self, vals):
    #     """Mengisi fleet_vehicle_checkup_request_ids saat membuat record baru."""
    #     record = super(MaintenanceRequest, self).create(vals)
    #     record._update_checkup_requests()
    #     return record

    # def _update_checkup_requests(self):
    #     """Update fleet_vehicle_checkup_request_ids berdasarkan pilihan template."""
    #     FleetVehicleCheckupRequest = self.env['fleet.vehicle.checkup.request']

    #     for rec in self:
    #         rec.fleet_vehicle_checkup_request_ids.unlink()

    #         if rec.template_monthly_full == 'full':
    #             domain = []
    #         else:
    #             if not rec.template_selection:
    #                 continue  # 
    #             domain = [('part_checkup_request_id.template', '=', int(rec.template_selection))]

    #         components = self.env['component.checkup.request'].search(domain)

    #         checkup_requests = [(0, 0, {
    #             'maintenance_request_id': rec.id,
    #             'component_checkup_request_id': component.id,
    #             'part_checkup_request_id': component.part_checkup_request_id.id,
    #         }) for component in components]

    #         rec.fleet_vehicle_checkup_request_ids = checkup_requests







    


    


        

            



