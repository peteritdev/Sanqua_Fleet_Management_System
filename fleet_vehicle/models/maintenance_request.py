import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
_logger = logging.getLogger(__name__)

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'
    _description = 'Inherit from maintenance request'

    request_no = fields.Char(string='Request No.')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    service_log_id = fields.One2many('fleet.vehicle.log.services', 'maintenance_request_id', string='Log Service', store=True)
    asset_type = fields.Selection([('equipment', 'Equipment'), ('vehicle', 'Vehicle')], string='Asset Type')
    driver_request_ids = fields.One2many('maintenance.request.driver.request', 'request_id', string='Driver Request')
    log_service_count = fields.Integer(compute="_compute_log_service")
    is_show_service_log = fields.Integer(default=1)

    @api.model
    def create(self, vals):
        res = super(MaintenanceRequest,self).create(vals)
        res.write({
            'request_no': self._fetch_next_seq()
        })
        return res

    def _fetch_next_seq(self):
        return self.env['ir.sequence'].next_by_code('seq.maintenance.request')

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

    request_id = fields.Many2one('maintenance.request', string='Request')
    name = fields.Char(string='Request')
