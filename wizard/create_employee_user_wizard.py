from odoo import models, fields, api, _
from odoo.exceptions import UserError
import random
import string
import logging

_logger = logging.getLogger(__name__)

def generate_random_password(length=10):
    """Generate a random password with letters, digits and special characters."""
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    return ''.join(random.choice(chars) for _ in range(length))


class CreateEmployeeUserWizard(models.TransientModel):
    _name = 'create.employee.user.wizard'
    _description = 'Create Employee and User Wizard'
    
    joining_form_id = fields.Many2one('joining.form', string='Joining Form', required=True)
    
    # Employee Information
    name = fields.Char(string='Name', required=True)
    personal_mobile = fields.Char(string='Personal Mobile')
    personal_email = fields.Char(string='Personal Email')
    department_id = fields.Many2one('hr.department', string='Department')
    job_title = fields.Char(string='Job Title')
    
    # User Information
    create_user = fields.Boolean(string='Create User Account', default=True)
    official_email = fields.Char(string='Official Email', help='Email to be used for the employee\'s user account')
    password = fields.Char(string='Password', default=lambda self: generate_random_password())
    
    # Result fields
    user_created = fields.Boolean(string='User Created', readonly=True)
    employee_created = fields.Boolean(string='Employee Created', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Created Employee', readonly=True)
    user_id = fields.Many2one('res.users', string='Created User', readonly=True)
    company_url = fields.Char(string='Company URL', compute='_compute_company_url')
    
    @api.onchange('joining_form_id')
    def _onchange_joining_form_id(self):
        if self.joining_form_id:
            form = self.joining_form_id
            self.name = form.name
            self.personal_mobile = form.personal_number
            self.personal_email = form.email_id
            self.department_id = form.department_id
            self.job_title = form.designation
            
    @api.depends('user_id')
    def _compute_company_url(self):
        """Compute the company website URL for login information."""
        for record in self:
            if record.user_id and record.user_id.company_id:
                record.company_url = record.user_id.company_id.website or self.env.company.website or self.env.get('web.base.url', '')
            else:
                record.company_url = self.env.company.website or self.env.get('web.base.url', '')
    
    def action_create_employee(self):
        """Create employee and optionally user from joining form data."""
        self.ensure_one()
        
        if not self.joining_form_id:
            raise UserError(_("No joining form selected."))
        
        joining_form = self.joining_form_id
        
        # Create employee
        employee_vals = {
            'name': self.name,
            'mobile_phone': self.personal_mobile,
            'private_email': self.personal_email,
            'department_id': self.department_id.id if self.department_id else False,
            'job_title': self.job_title,
            'gender': joining_form.gender,
            'birthday': joining_form.date_of_birth,
            'marital': joining_form.marital_status,
            'address_home_id': self.env['res.partner'].sudo().create({
                'name': self.name,
                'phone': self.personal_mobile,
                'email': self.personal_email,
                'street': joining_form.address,
                # In Odoo 17, 'contact' is the standard type for individuals
                'type': 'contact',
            }).id,
        }
        
        # Add emergency contact if provided
        if joining_form.emergency_contact_name:
            emergency_contact = self.env['res.partner'].sudo().create({
                'name': joining_form.emergency_contact_name,
                'phone': joining_form.emergency_contact_mobile,
                'email': joining_form.emergency_contact_email,
                'street': joining_form.emergency_contact_address,
                # In Odoo 17, 'contact' is the standard type for individuals
                'type': 'contact',
            })
            employee_vals['emergency_contact'] = joining_form.emergency_contact_name
            employee_vals['emergency_phone'] = joining_form.emergency_contact_mobile
        
        employee = self.env['hr.employee'].sudo().create(employee_vals)
        self.employee_created = True
        self.employee_id = employee.id
        
        # Create user if requested
        if self.create_user and self.official_email:
            user_vals = {
                'name': self.name,
                'login': self.official_email,
                'password': self.password,
                'email': self.official_email,
                'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
            }
            user = self.env['res.users'].sudo().create(user_vals)
            employee.user_id = user.id
            self.user_created = True
            self.user_id = user.id
        
        # Update the joining form
        update_vals = {
            'employee_id': employee.id,
            'state': 'employee_created',
        }
        
        # Only update user_id if a user was created
        if self.user_created and self.user_id:
            update_vals['user_id'] = self.user_id.id
            
        joining_form.write(update_vals)
        
        # Return view with results
        return {
            'name': _('Employee Created'),
            'type': 'ir.actions.act_window',
            'res_model': 'create.employee.user.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {'form_view_initial_mode': 'edit'},
        }
