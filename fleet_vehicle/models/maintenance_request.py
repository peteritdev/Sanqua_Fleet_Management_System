import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'
    _description = 'Inherit from maintenance request'



    request_no = fields.Char(string='Request No.', readonly=True, copy=False)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    service_log_id = fields.One2many('fleet.vehicle.log.services', 'maintenance_request_id', string='Log Service', store=True)
    asset_type = fields.Selection([('equipment', 'Equipment'), ('vehicle', 'Vehicle')], string='Asset Type')
    driver_request_ids = fields.One2many('maintenance.request.driver.request', 'request_id', string='Driver Request', store=True)
    log_service_count = fields.Integer(compute="_compute_log_service")
    is_show_service_log = fields.Integer(default=1)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Created By', default=lambda self: self.env["hr.employee"].search([('user_id', '=', self.env.uid)], limit=1), store=True)
    odometer = fields.Float(string='Odometer', store=True)
    schedule_date = fields.Datetime('Scheduled Date', default=fields.Datetime.now, help="Date the maintenance team plans the maintenance.  It should not differ much from the Request Date. ")
    driver_id = fields.Many2one('res.partner', string='Driver', store=True, tracking=True)


    # @api.model
    # def create(self, vals):
    #     res = super(MaintenanceRequest,self).create(vals) 
    #     res.write({
    #         'request_no': self._fetch_next_seq()
    #     })
    #     return res

    @api.model
    def create(self, vals):
        if not vals.get('request_no'):  
            vals['request_no'] = self.env['ir.sequence'].next_by_code('seq.maintenance.request') or ''
        return super(MaintenanceRequest, self).create(vals)

    def write(self, vals):
        """ Pastikan odometer di fleet.vehicle selalu diperbarui """
        res = super(MaintenanceRequest, self).write(vals)
        if 'odometer' in vals and self.vehicle_id:
            # self.vehicle_id.odometer = vals['odometer']
            self.vehicle_id.sudo().write({'odometer': vals['odometer']})
        return res  
    
        
    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        """ Ketika memilih vehicle, otomatis mengisi odometer sesuai kendaraan """
        if self.vehicle_id:
            self.odometer = self.vehicle_id.odometer

    # def _fetch_next_seq(self):
    #     return self.env['ir.sequence'].next_by_code('seq.maintenance.request')

    def _compute_log_service(self):
        for rec in self:
            rec.log_service_count = len(rec.service_log_id)

    def open_log_service(self):
        self.ensure_one()
        context = dict(self.env.context or {})
        # context.update({}) #uncomment if need append context
        res = {
            'name': "%s" % (_('Services')),
            'view_mode': 'tree,form',
            'res_model': 'fleet.vehicle.log.services',
            # 'view_ids': [(False, 'tree'), (False, 'form')],
            'type': 'ir.actions.act_window',
            'context': {'default_maintenance_request_id': self.id},
            'domain': [('maintenance_request_id', '=', self.id)]
        }
        return res

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if self.stage_id.name == 'New Request' and len(self.service_log_id) > 0:
            raise UserError(_('You can not change stage to New Request since you already have Log Services .'))

        if self.stage_id.name == 'New Request':
            self.is_show_service_log = 1
        else:
            self.is_show_service_log = 0

class MaintenanceRequestDriverRequest(models.Model):
    _name = 'maintenance.request.driver.request'
    _description = 'Request of driver'

    name = fields.Char(string='Name', related='problem_id.name', readonly=True, invisible=True, store=True) 
    request_id = fields.Many2one('maintenance.request', string='Request', store=True)
    problem_id = fields.Many2one('master.problem.vehicle', string='Problem', store=True)
    def name_get(self):
        """Menampilkan problem_id sebagai name, bukan ID."""
        result = []
        for rec in self:
            name = rec.problem_id.name if rec.problem_id else "No Problem"
            result.append((rec.id, name))
        return result


class MasterProblemVehicle(models.Model):
    _name = 'master.problem.vehicle'
    _description = 'Vehicle Problem'

    name = fields.Char(string='Problem', store=True)
    category_id = fields.Many2one('category.problem.vehicle', string='Category', store=True)


class CategoryProblem(models.Model):
    _name = 'category.problem.vehicle'
    _description = 'Category Problem'

    name = fields.Char(string='Category', store=True)
    
