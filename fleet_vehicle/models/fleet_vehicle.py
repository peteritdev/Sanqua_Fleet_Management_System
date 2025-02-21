import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.tools import format_datetime

_logger = logging.getLogger(__name__)

class FleetVechileKIRLog(models.Model):
    _name = 'fleet.vehicle.kir.log'

    def _get_selection_pic(self, pKeyword=None):
        xSelection = list()
        xSelection.append(('','--- Please Select --'))
        # _logger.info('>>> Here 1')
        if pKeyword:
            # _logger.info('>>> Here 2')
            xOAuthRes = self.env['esanqua.oauth'].login()
            # _logger.info('>>> Here 3')
            if xOAuthRes['status_code'] == '00':
                _logger.info('>>> Here 4')
                _logger.info(('>>> LOGIN RESULT : %s') % (xOAuthRes['token']))

                # Get employee via api dropdown
                xDropdownRes = self.env['esanqua.hris'].dd_get_employee(xOAuthRes['token'], pKeyword)
                if xDropdownRes['status_code'] == '00':
                    xData = xDropdownRes['data']
                    for data in xData:
                        _logger.info(('>>> NIK : %s') % (data['nik']))
                        _logger.info(('>>> Name : %s') % (data['name']))
                        xSelection.append((data['nik'], data['name']))
        # _logger.info(('>>> xSelection RESULT : %s') % (xSelection))
        return xSelection

    # def _get_selected_company(self):
    #     return [('company_id','=', self.env.company)]

    vehicle_id = fields.Many2one('fleet.vehicle', required=True, string='Vehicle')
    kir_date = fields.Date(string='KIR Date', required=True)
    pic = fields.Many2one('hr.employee', string='PIC')
    # pic = fields.Char(string='PIC')
    expiration_kir_date = fields.Date(string='KIR Date Expiration', required=True)
    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        result = super(FleetVechileKIRLog, self).create(vals)
        result.vehicle_id.write({
            # 'expire_date_kir': vals['expiration_kir_date']
            'expire_date_kir': result.expiration_kir_date
        })

        return result

class FleetVehicleRegistrationLog(models.Model):
    _name = 'fleet.vehicle.registration.log'

    # def _get_selected_company(self):
    #     return [('company_id','=', self.env.company)]

    vehicle_id = fields.Many2one('fleet.vehicle', required=True, string='Vehicle')
    date_registration = fields.Date(string='Date of Registration')
    # is_stnk = fields.Boolean(string='STNK')
    # is_skpd = fields.Boolean(string='SKPD')
    registration_type = fields.Selection([('stnk', 'STNK'),('skpd', 'SKPD')], string='Registration Type', default='stnk')
    pic = fields.Many2one('hr.employee', string='PIC')
    expiration_date = fields.Date(string='Expiration Date', required=True)
    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        result = super(FleetVehicleRegistrationLog, self).create(vals)

        if result.registration_type == 'stnk':
            result.vehicle_id.write({
                'expire_date_stnk': result.expiration_date
            })
        elif result.registration_type == 'skpd':
            result.vehicle_id.write({
                'expire_date_skpd': result.expiration_date
            })
        return result

class FleetVehicleRegistration(models.Model):
    _inherit = 'fleet.vehicle'

    stnk_no = fields.Char(string='STNK No', store=True)
    skpd_no = fields.Char(string='SKPD No', store=True)
    kir_no = fields.Char(string='KIR No', store=True)
    notification_expire_date_stnk = fields.Date(string='Next notification expire date STNK')
    notification_expire_date_skpd = fields.Date(string='Next notification expire date SKPD')
    notification_expire_date_kir = fields.Date(string='Next notification expire date KIR')
    expire_date_stnk = fields.Date(string='Expire Date STNK')
    expire_date_skpd = fields.Date(string='Expire Date SKPD')
    expire_date_kir = fields.Date(string='Expire Date KIR')

    kir_line_ids = fields.One2many('fleet.vehicle.kir.log', 'vehicle_id', string='KIR History')
    registration_line_ids = fields.One2many('fleet.vehicle.registration.log', 'vehicle_id', string='Registration History')

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    _description = 'Inherited from fleet.vehicle.log.services'

    name = fields.Char(string="Service No.", readonly=True)
    maintenance_request_id = fields.Many2one('maintenance.request', string='Maintenance Request', store=True, readonly=True)
    mechanic_check_log_ids = fields.One2many('mechanic.check.log', 'service_log_id', string='Mechanic Checking Logs')
    mechanic_fix_log_ids = fields.One2many('mechanic.fix.log', 'service_log_id', string='Mechanic Fix Logs')
    vehicle_id = fields.Many2one('fleet.vehicle', related='maintenance_request_id.vehicle_id', string='Vehicle', required=False, store=True, readonly=True)

    state = fields.Selection(selection='_get_selection_state', string='Stage', tracking=True)

    picking_ids = fields.One2many('stock.picking', 'service_log_id', string='Sparepart Request', store=True)
    summary_sparepart_request_ids = fields.One2many('summary.sparepart.request', 'service_log_id', string='Summary Sparepart Request')
    move_ids = fields.One2many(comodel_name="stock.move",inverse_name="service_log_id",string="Sparepart Moves",store=False,compute="_compute_move_ids")
    is_maintenance_type = fields.Boolean(string='Maintenance Type', compute='_compute_maintenance_type')
    service_type = fields.Selection([('internal', 'Internal'), ('external', 'External')], string='Service Type', store=True, required=True)
    purchaser_id = fields.Many2one('res.partner', string="Driver", store=True, readonly=True, related='maintenance_request_id.driver_id')   
    service_type_id = fields.Many2one(
        'fleet.service.type', 'Service Type', required=False,
        default=lambda self: self.env.ref('fleet.type_service_service_7', raise_if_not_found=False),
    )
    display_name = fields.Char(compute='_compute_display_name', string='Display Name', store=True)


    def _compute_display_name(self):
        for record in self:
            record.display_name = record.name
    

    def _compute_maintenance_type(self):
        for record in self:
            maintenance_type = record.maintenance_request_id.maintenance_type
            record.is_maintenance_type = True if maintenance_type == 'corrective' else False

    @api.depends("picking_ids")
    def _compute_move_ids(self):
        for record in self:
            record.move_ids = self.env["stock.move"].search([
                ("picking_id", "in", record.picking_ids.ids)
            ])
            
    # @api.model
    # def default_get(self, default_fields):
    #     res = super(FleetVehicleLogServices, self).default_get(default_fields)
    #     _logger.info('>>> Res: ' + str(res))
    #     _logger.info('>>> default_fields: ' + str(default_fields))
    #     _logger.info('>>> vehicle_id : ' + str(res['maintenance_request_id']))
    #     # res['vehicle_id'] = res['maintenance_request_id']
    #     return res

    @api.model
    def create(self, vals):
        res = super(FleetVehicleLogServices, self).create(vals)

        res.write({'name': self._fetch_next_seq()})
        return res

    def _fetch_next_seq(self):
        return self.env['ir.sequence'].next_by_code('seq.service.log.request')

    def do_cancel(self):
        if self.state not in ('done'):
            self.write({
                'state': 'canceled'
            })
            # self.perm_mech_fix_log = 0
            # self.perm_mech_check_log = 0

    def do_finish(self):
        if self.state not in ('canceled', 'new', 'checking'):
            self.write({
                'state': 'done'
            })
            # self.perm_mech_fix_log = 0
            # self.perm_mech_check_log = 0

    def do_submit(self):
        _logger.info('>>> Call do_submit()')
        if self.state == 'new':
            self.write({
                'state': 'checking'
            })
        # elif self.state == 'checking':
        #     self.write({
        #         'state': 'fixing'
        #     })
        # elif self.state == 'fixing':
        #     self.write({
        #         'state': 'done'
        #     })
    def do_fixing(self):
        if self.state == 'checking':
            self.write({
                'state': 'fixing'
            })

    @api.model
    def _get_selection_state(self):
        return [
            ('new', 'Draft'),
            ('checking', 'On Checking'),
            ('fixing', 'On Fixing'),
            ('done', 'Done'),
            ('canceled', 'Canceled')
        ]

    def btn_request_sparepart(self):
        _logger.info('>>> Here btn_request_sparepart()')
        self.ensure_one()
        context = dict(self.env.context or {})
        res = {
            'name': '%s' % (_('Request Sparepart')),
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'context': {'default_service_log_id': self.id},
            'domain': [('service_log_id', '=', self.id)]
        }
        return res



class MechanicCheckLog(models.Model):
    _name = 'mechanic.check.log'
    _description = 'Mechanic check log'

    # def _get_driver_request_domain(self):
    #     _logger.info('>>> ID : ' + str(self.env.context.get('active_id')))
    #     return [('request_id.id', '=', 17)]

    service_log_id = fields.Many2one('fleet.vehicle.log.services', 'Service')
    maintenance_request_id = fields.Many2one(related='service_log_id.maintenance_request_id')
    driver_request_id = fields.Many2one('maintenance.request.driver.request')
    driver_request_ids_domain = fields.Binary(compute='_get_driver_request_id')
    check_list = fields.Text(string='Check Description')

    @api.depends('maintenance_request_id')
    def _get_driver_request_id(self):
        for rec in self:
            domain = []
            if rec.maintenance_request_id:
                _logger.info('>>> maintenance_request_id: ' + str(rec.maintenance_request_id))
                domain = [('request_id', '=', rec.maintenance_request_id.id)]
            rec.driver_request_ids_domain = domain


class MechanicFixLog(models.Model):
    _name = 'mechanic.fix.log'
    _description = 'Mechanic Fix Log'

    service_log_id = fields.Many2one('fleet.vehicle.log.services', 'Service')
    fix_list = fields.Text(string='Fix Description')
    user_id = fields.Many2one('res.users', 'Mechanic')
    start_time = fields.Datetime(string='Start Time')
    finish_time = fields.Datetime(string='Finish Time')

    start_time_fmt = fields.Char(string="Start Time Formatted", compute="_compute_time_format")
    finish_time_fmt = fields.Char(string="Finish Time Formatted", compute="_compute_time_format")

    @api.depends('start_time', 'finish_time')
    def _compute_time_format(self):
        for record in self:
            record.start_time_fmt = record.start_time and format_datetime(self.env, record.start_time, tz=self.env.user.tz, dt_format='dd MMMM yyyy HH:mm:ss') or ""
            record.finish_time_fmt = record.finish_time and format_datetime(self.env, record.finish_time, tz=self.env.user.tz, dt_format='dd MMMM yyyy HH:mm:ss') or ""



class StockMove(models.Model):
    _inherit = "stock.move"

    service_log_id = fields.Many2one(
        comodel_name="fleet.vehicle.log.services",
        related="picking_id.service_log_id",
        store=True
    )


