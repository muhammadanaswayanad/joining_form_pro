{
    'name': 'Joining Form Pro',
    'version': '17.0.1.0.0',
    'summary': 'Advanced Joining Form for Public Users',
    'description': """
        This module provides a public-accessible form for candidates to submit their joining details.
        HR team can review submissions, approve them and create employees with user accounts.
    """,
    'category': 'Human Resources',
    'author': 'Odoo Developer',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['hr', 'portal', 'mail', 'hr_recruitment', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/joining_form_views.xml',
        'views/joining_form_templates.xml',
        'views/menu_views.xml',
        'wizard/create_employee_user_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'joining_form_pro/static/src/js/joining_form.js',
            'joining_form_pro/static/src/css/joining_form.css',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
