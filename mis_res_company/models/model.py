from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError

class MISResCompany(models.Model):
    _inherit = 'res.company'

    code_plant =fields.Char(string="Code Plant")