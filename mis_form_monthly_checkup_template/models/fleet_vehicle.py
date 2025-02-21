import logging

from odoo import api, fields, models,tools, _
from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.tools import format_datetime
_logger = logging.getLogger(__name__)


class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    _description = 'Inherited from fleet.vehicle.log.services'

 

    fleet_vehicle_checkup_service_ids = fields.One2many('fleet.vehicle.checkup.service', 'log_service_id', string='Checkup Service',store=True)
    is_checkup_available = fields.Boolean(string="Checkup Available",compute="_compute_is_checkup_available",store=False)

    @api.depends('fleet_vehicle_checkup_service_ids')
    def _compute_is_checkup_available(self):
        for record in self:
            record.is_checkup_available = bool(record.fleet_vehicle_checkup_service_ids)

    def action_print_monthly_checkup(self):
        """ Generate Monthly Checkup PDF """
        return self.env.ref('mis_form_monthly_checkup_template.action_template_monthly_checkup').report_action(self)
    
    def get_checkup_data(self):
        """ Mengambil data service checkup menggunakan query SQL berdasarkan log_service_id """
        query = """
            SELECT 
                fvcs.id,
                fvcs.category_checkup_request_id,
                fvcs.component_checkup_request_id,
                fvcs.check_list_r,
                fvcs.check_list_g,
                fvcs.check_list_p,
                fvcs.check_list_v,
                fvcs.check_list_x,
                fvcs.desc_mechanic,
                ccr.name AS category_name,
                ccr2.name AS component_name
            FROM 
                fleet_vehicle_checkup_service fvcs
            LEFT JOIN 
                category_checkup_request ccr ON fvcs.category_checkup_request_id = ccr.id
            LEFT JOIN 
                component_checkup_request ccr2 ON fvcs.component_checkup_request_id = ccr2.id
            WHERE 
                fvcs.log_service_id = %s
            ORDER BY 
                fvcs.category_checkup_request_id, fvcs.component_checkup_request_id
        """
        self.env.cr.execute(query, (self.id,)) 
        return self.env.cr.dictfetchall()

    @api.model
    def create(self, vals):
        """ Override create untuk menambahkan data ke fleet.vehicle.checkup.service """
        record = super(FleetVehicleLogServices, self).create(vals)
        if record.maintenance_request_id:
            record._sync_checkup_service()
        return record

    def write(self, vals):
        """ Override write untuk memastikan data fleet.vehicle.checkup.service tetap terupdate """
        res = super(FleetVehicleLogServices, self).write(vals)
        if 'maintenance_request_id' in vals:
            self._sync_checkup_service()
        return res


    def _sync_checkup_service(self):
        """ Sinkronisasi data fleet.vehicle.checkup.service berdasarkan fleet.vehicle.checkup.request """
        FleetVehicleCheckupService = self.env['fleet.vehicle.checkup.service']

        for record in self:
            if not record.maintenance_request_id:
                continue  

            existing_services = FleetVehicleCheckupService.search([
                ('log_service_id', '=', record.id)
            ])
            existing_services.unlink()

            checkup_requests = self.env['fleet.vehicle.checkup.request'].search([
                ('maintenance_request_id', '=', record.maintenance_request_id.id)
            ])

            if not checkup_requests:
                continue  

            for checkup in checkup_requests:
                FleetVehicleCheckupService.create({
                        'log_service_id': record.id,
                    'maintenance_request_id': record.maintenance_request_id.id,
                    'category_checkup_request_id': checkup.category_checkup_request_id.id if checkup.category_checkup_request_id else False,
                    'component_checkup_request_id': checkup.component_checkup_request_id.id if checkup.component_checkup_request_id else False,
                    'check_list_r': checkup.check_list_r,
                    'check_list_g': checkup.check_list_g,
                    'check_list_p': checkup.check_list_p,
                    'check_list_v': checkup.check_list_v,
                    'check_list_x': checkup.check_list_x,
                    'desc_mechanic': checkup.desc_mechanic,
                })


    # super 
    def do_fixing(self):
        """Validasi sebelum submit: 
        - Jika is_maintenance_type == True, tetap bisa submit.
        - Jika is_maintenance_type == False, checklist tidak boleh kosong.
        """
        for rec in self:
            if not rec.is_maintenance_type:  # Hanya validasi jika bukan 'corrective'
                for service in rec.fleet_vehicle_checkup_service_ids:
                    if not any([
                        service.check_list_r, 
                        service.check_list_g, 
                        service.check_list_p, 
                        service.check_list_v, 
                        service.check_list_x    
                    ]):
                        raise UserError(
                            "Baris pemeriksaan pada '{}' tidak boleh kosong. Harap isi salah satu checklist."
                            .format(service.component_checkup_request_id.name)
                        )
        return super(FleetVehicleLogServices, self).do_fixing()


class FleetVehicleCheckupRequest(models.Model):
    _name = 'fleet.vehicle.checkup.request'
    _description = 'Fleet Vehicle Checkup Request'


    maintenance_request_id = fields.Many2one('maintenance.request', string='Maintenance Request', store=True)
    category_checkup_request_id = fields.Many2one('category.checkup.request', 'Part', store=True)
    component_checkup_request_id = fields.Many2one('component.checkup.request', 'Component', store=True)
    check_list_r = fields.Boolean('RUSAK', store=True)
    check_list_g = fields.Boolean('GANTI', store=True)
    check_list_p = fields.Boolean('PERIKSA', store=True)
    check_list_v = fields.Boolean('LAYAK JALAN', store=True)
    check_list_x = fields.Boolean('TIDAK LAYAK JALAN', store=True)
    desc_mechanic = fields.Char('Description', store=True)


class FleetVehicleCheckupService(models.Model):
    _name = 'fleet.vehicle.checkup.service'
    _description = 'Fleet Vehicle Checkup Service'


    log_service_id = fields.Many2one('fleet.vehicle.log.services', string='Log Service', store=True)
    maintenance_request_id = fields.Many2one('maintenance.request', string='Maintenance Request', store=True)
    category_checkup_request_id = fields.Many2one('category.checkup.request', 'Part', store=True)
    component_checkup_request_id = fields.Many2one('component.checkup.request', 'Component', store=True)
    check_list_r = fields.Boolean('RUSAK', store=True)
    check_list_g = fields.Boolean('GANTI', store=True)
    check_list_p = fields.Boolean('PERIKSA', store=True)
    check_list_v = fields.Boolean('LAYAK JALAN', store=True)
    check_list_x = fields.Boolean('TIDAK LAYAK JALAN', store=True)
    desc_mechanic = fields.Char('Description', store=True)

    @api.constrains('check_list_r', 'check_list_g', 'check_list_p', 'check_list_v', 'check_list_x')
    def _check_only_one_selected(self):
        """ Pastikan hanya satu opsi checklist yang dipilih dalam satu baris """
        for record in self:
            checklists = [record.check_list_r, record.check_list_g, record.check_list_p, record.check_list_v, record.check_list_x]
            if sum(checklists) > 1:
                raise ValidationError("Baris Pemeriksaan hanya boleh dilakukan satu opsi yang dipilih.")
            
            
            



    # def _get_query(self):
    #     return """
    #         CREATE OR REPLACE VIEW %s AS
    #         SELECT 
    #             row_number() OVER () AS id,
    #             fvcr.maintenance_request_id,
    #             fvl.id AS log_service_id,  
    #             fvcr.category_checkup_request_id,
    #             fvcr.component_checkup_request_id,
    #             fvcr.check_list_r,
    #             fvcr.check_list_g,
    #             fvcr.check_list_p,
    #             fvcr.check_list_v,
    #             fvcr.check_list_x,
    #             fvcr.desc_mechanic
    #         FROM fleet_vehicle_checkup_request fvcr
    #         LEFT JOIN fleet_vehicle_log_services fvl ON fvcr.maintenance_request_id = fvl.maintenance_request_id
    #     """ % (self._table)

    # def init(self):
    #     tools.drop_view_if_exists(self.env.cr, self._table)
    #     self.env.cr.execute(self._get_query())