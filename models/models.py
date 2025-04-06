from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _find_mail_template(self):
        """Override to use our custom template"""
        self.ensure_one()
        if self.state in ('draft', 'sent'):
            return self.env.ref('custom_quotation_send.mail_template_custom_quotation')
        return super()._find_mail_template()

    def action_quotation_send(self):
        """Override to ensure portal access for all recipients"""
        self.ensure_one()
        # Subscribe all followers to ensure they get portal access
        self.message_subscribe(partner_ids=self.message_partner_ids.ids)
        return super().action_quotation_send()

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def default_get(self, fields):
        """Override to set proper email headers"""
        res = super().default_get(fields)
        if self._context.get('default_model') == 'sale.order' and self._context.get('default_res_id'):
            order = self.env['sale.order'].browse(self._context['default_res_id'])
            if order.state in ('draft', 'sent'):
                res['email_from'] = order.user_id.email_formatted or order.company_id.email_formatted
        return res