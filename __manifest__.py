{
    'name': 'Custom Quotation Send',
    'version': '1.0',
    'summary': 'Force Sign & Pay links for all recipients',
    'description': 'Makes all quotation recipients receive Sign & Pay links',
    'author': 'Amulya Sharma',
    'depends': ['sale', 'mail'],
    'data': [
        'views/mail_templates.xml',
    ],
    'installable': True,
    'application': False,
}
