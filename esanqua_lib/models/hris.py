import json
import requests
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

class ESanQuaHRIS(models.TransientModel):
    _name = 'esanqua.hris'

    def dd_get_employee(self, pToken, pKeyword):
        xConfig = self.env['ir.config_parameter'].sudo()
        xBaseUrl = xConfig.get_param('esanqua.hris_baseurl', False)

        xHeaders = {
            'Content-Type': 'application/json',
            'x-token': pToken,
            'x-method': 'conventional'
        }

        xBodyPayload = {}

        xResponse = requests.request('GET',
                                     (xBaseUrl + '/employee/dropdown?keyword=%s&offset=0&limit=10')%(pKeyword),
                                     headers=xHeaders,
                                     data= xBodyPayload)

        _logger.info(('>>> LOGIN RESULT : %s') % (xResponse.text))
        xJsonRes = json.loads(xResponse.text)
        return xJsonRes

    def get_employee(self,pCompanyId):
        xJsonRes = {}
        if pCompanyId:
            xConfig = self.env['ir.config_parameter'].sudo()
            xBaseUrl = xConfig.get_param('esanqua.hris_baseurl', False)

            xOAuthRes = self.env['esanqua.oauth'].login()
            if xOAuthRes['status_code'] == '00':
                if xOAuthRes['token']:
                    xHeaders = {
                        'Content-Type': 'application/json',
                        'x-token': xOAuthRes['token'],
                        'x-method': 'conventional'
                    }

                    xBodyPayload = {}

                    xResponse = requests.request('GET',
                                                 (xBaseUrl + '/employee/dropdown?keyword=&offset=0&limit=all&filter=[{"company_id":%s}]')%(pCompanyId),
                                                 headers=xHeaders,
                                                 data= xBodyPayload)

                    # _logger.info(('>>> dd_get_employee_2 RESULT : %s') % (xResponse.text))
                    xJsonRes = json.loads(xResponse.text)
        return xJsonRes



