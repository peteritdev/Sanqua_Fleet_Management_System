import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
_logger = logging.getLogger(__name__)

class PartsCheckupRequest(models.Model):
    _name ='category.checkup.request'
    _description = 'Category Request Monthly'


    name = fields.Char('Category Check', store=True )




class ComponentCheckRequest(models.Model):
    _name = 'component.checkup.request'
    _description = 'Component Checkup Request'

    name = fields.Char('Component Check', store=True)











        
        
