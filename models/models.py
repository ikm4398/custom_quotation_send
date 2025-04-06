from odoo import models, api, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _find_mail_template(self):
        """Override to use our custom template"""
        self.ensure_one()
        if self.state in ('draft', 'sent'):
            return self.env.ref('custom_quotation_send.mail_template_custom_quotation')
        return super()._find_mail_template()

    def action_quotation_send(self):
        """Override to auto-add recipients and ensure Sign & Pay"""
        self.ensure_one()
        
        # Auto-add default recipients (partner + followers, excluding admin)
        default_recipients = self.partner_id | self.message_partner_ids
        admin_user = self.env.ref('base.user_admin')
        if admin_user.partner_id in default_recipients:
            default_recipients -= admin_user.partner_id
            
        self.message_subscribe(partner_ids=default_recipients.ids)
        
        # Get valid email_from (skip admin if needed)
        email_from = False
        if self.user_id.email and self.user_id != admin_user:
            email_from = self.user_id.email_formatted
        elif self.company_id.email:
            email_from = self.company_id.email_formatted

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_model': 'sale.order',
                'default_res_id': self.id,
                'default_use_template': True,
                'default_template_id': self.env.ref('custom_quotation_send.mail_template_custom_quotation').id,
                'default_partner_ids': default_recipients.ids,
                'default_email_from': email_from,
                'force_sign_and_pay': True,
                'mark_so_as_sent': True,
            },
        }

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def default_get(self, fields):
        """Set default recipients and email_from"""
        res = super().default_get(fields)
        if self._context.get('default_model') == 'sale.order':
            res['partner_ids'] = self._context.get('default_partner_ids', [])
            if 'default_email_from' in self._context:
                res['email_from'] = self._context['default_email_from']
        return res
