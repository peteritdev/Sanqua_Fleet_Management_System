import logging

from odoo import api, fields, models,tools, _
from odoo.exceptions import ValidationError, AccessError, UserError

_logger = logging.getLogger(__name__)

class StockPickingInherited(models.Model):
    _inherit = 'stock.picking'
    _description = 'Inherited stock.picking'

    service_log_id = fields.Many2one('fleet.vehicle.log.services', 'Service', store=True, readonly=True)
    service_request_no = fields.Char(related='service_log_id.name')

    # @api.depends('service_log_id')
    # def _set_default_picking_type(self):
    #     for rec in self:
    #         if rec.service_log_id:
    #             rec.picking_type_id = 30

    @api.model
    def default_get(self, default_fields):
        rec = super(StockPickingInherited,self).default_get(default_fields)
        rec.update({
            'picking_type_id': 30
        })
        return rec

class StockPickingReturnInherited(models.TransientModel):
    _inherit = 'stock.return.picking'

    service_log_id = fields.Many2one('fleet.vehicle.log.services', related='picking_id.service_log_id')
    service_request_no = fields.Char(related='service_log_id.name')

    # def _create_returns(self):
    #     picking_id, picking_type_id = super(StockPickingReturnInherited, self)._create_returns()
    #     picking = self.env['stock.picking'].sudo().browse(picking_id)
    #     picking.sudo().write({
    #         'picking_type_id': 30
    #     })
    #     return picking_id, picking_type_id

class SummarySparepartRequest(models.Model):
    _name = 'summary.sparepart.request'
    _description = 'Summary of sparepart request for view only'
    _auto = False

    service_log_id = fields.Many2one('fleet.vehicle.log.services', string="Service Log" )
    product_code = fields.Char(string='Product Code')
    product_name = fields.Char(string='Product Name')
    qty_done = fields.Float(string='Qty Done')
    qty_return = fields.Float(string='Qty Return')

    def _get_query(self):
        xSql = """  
            CREATE or REPLACE VIEW %s AS          
            select ROW_NUMBER() OVER (ORDER BY pt.default_code ASC) AS id, 
                pt.default_code AS "product_code", 
				pt.name->>'en_US' AS "product_name",
					SUM(sm.quantity) AS "qty_done",
						COALESCE(sm_return.product_uom_qty, 0::numeric) AS "qty_return",
							sp.service_log_id
            from stock_picking sp left join stock_move sm on sp.id = sm.picking_id
                left join product_product pp on pp.id = sm.product_id
                    left join product_template pt on pt.id = pp.product_tmpl_id
                        left join stock_move sm_return on sm.id = sm_return.origin_returned_move_id and sm_return.state::text = 'done'::text
            where sm.origin_returned_move_id IS NULL
                and sp.service_log_id is not null
            group by pt.default_code, pt.name, sm_return.product_uom_qty, sp.service_log_id
        """ % (self._table)
        return xSql

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(self._get_query())


