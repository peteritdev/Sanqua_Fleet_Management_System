import logging
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class WizardSyncEmployeeESanQua(models.TransientModel):
    _name = 'wizard.sync.employee.esanqua'
    _description = 'Wizard sync employee from e-SanQua'

    def button_sync(self):
        xESanQuaEmp = self.env['esanqua.hris'].get_employee(7)
        if xESanQuaEmp['status_code'] == '00':
            for data in xESanQuaEmp['data']:
                self.env['hr.employee'].sudo().create({
                    'name': data['name'],
                    'barcode': data['nik'],
                    'company_id': data['company_id']
                })
        _logger.info(('>>> button_sync: %s')%(self.env.company.id))

