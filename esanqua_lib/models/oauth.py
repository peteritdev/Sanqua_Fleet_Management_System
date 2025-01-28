import json
import requests
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

class eSanQuaOAuth(models.TransientModel):
    _name = 'esanqua.oauth'

    def login(self):
        xConfig = self.env['ir.config_parameter'].sudo()
        xUsername = xConfig.get_param('esanqua.username', False)
        xPassword = xConfig.get_param('esanqua.password', False)
        xBaseUrl = xConfig.get_param('esanqua.oauth_baseurl', False)

        xHeaders ={
            'Content-Type': 'application/json',
            'x-application-id': '21',
            'x-device': 'web'
        }

        xBodyPayload = json.dumps({
            'email': xUsername,
            'password': xPassword
        })

        xResponse = requests.request('POST', (xBaseUrl+'/user/login'), headers=xHeaders, data=xBodyPayload)
        # _logger.info(('>>> LOGIN RESULT : %s') % (xResponse.text))
        xJsonRes = json.loads(xResponse.text)
        return xJsonRes





