import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
_logger = logging.getLogger(__name__)

class TemplateMonthlyCheckup(models.Model):
    _name ='template.monthly.checkup'
    _description = 'Template Monthly Checkup'



    name = fields.Char('Template', store=True )
    template_monthly_line_ids = fields.One2many('template.monthly.line', 'template_monthly_checkup_id', string='Template Monthly Line')
    company_ids = fields.Many2many('res.company', string='Company')




class TemplateMonthlyLine(models.Model):
    _name = 'template.monthly.line'
    _description = 'Template Monthly Line'


    component_checkup_request_id = fields.Many2one('component.checkup.request', string='Components')
    category_checkup_request_id = fields.Many2one('category.checkup.request', string='Category')
    template_monthly_checkup_id = fields.Many2one('template.monthly.checkup', string='Template Monthly Check Up')


        
        
