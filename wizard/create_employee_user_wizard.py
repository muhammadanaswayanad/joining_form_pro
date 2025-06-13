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
    
    def _field_exists(self, model, field_name):
        """Check if a field exists in a model"""
        try:
            exists = field_name in self.env[model]._fields
            _logger.info(f"Checking if field '{field_name}' exists in model '{model}': {exists}")
            return exists
        except Exception as e:
            _logger.error(f"Error checking if field '{field_name}' exists in '{model}': {str(e)}")
            return False
    
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
        
        # Create employee with compatible fields
        employee_vals = {
            'name': self.name,
        }
        
        # Create a partner for the employee contact information
        partner_vals = {
            'name': self.name,
            'phone': self.personal_mobile,
            'email': self.personal_email,
            'street': joining_form.address,
        }
        
        # Check if 'type' field exists to avoid errors in Odoo 17
        if self._field_exists('res.partner', 'type'):
            partner_vals['type'] = 'contact'
        
        _logger.info(f"Creating partner with values: {partner_vals}")
        partner = self.env['res.partner'].sudo().create(partner_vals)
        
        # Add fields only if they exist in the hr.employee model
        field_mapping = {
            'mobile_phone': self.personal_mobile,
            'work_phone': self.personal_mobile,  # Alternative if mobile_phone doesn't exist
            'private_email': self.personal_email,
            'work_email': self.personal_email,  # Alternative if private_email doesn't exist
            'department_id': self.department_id.id if self.department_id else False,
            'job_title': self.job_title,
            'gender': joining_form.gender,
            'birthday': joining_form.date_of_birth,
            'marital': joining_form.marital_status,
        }
        
        for field, value in field_mapping.items():
            if self._field_exists('hr.employee', field) and value:
                employee_vals[field] = value
        
        # Handle employee's partner association differently for Odoo 17
        _logger.info("Checking for private address field in hr.employee model...")
        
        # In Odoo 17, the employee's private address can be set after creation
        # We will determine which field to use and set it after the employee is created
        has_address_home_id = self._field_exists('hr.employee', 'address_home_id')
        has_address_id = self._field_exists('hr.employee', 'address_id') 
        has_partner_id = self._field_exists('hr.employee', 'partner_id')
        
        _logger.info(f"Private address field existence - address_home_id: {has_address_home_id}, address_id: {has_address_id}, partner_id: {has_partner_id}")
            
        # Handle emergency contact if provided
        if joining_form.emergency_contact_name:
            emergency_contact_vals = {
                'name': joining_form.emergency_contact_name,
                'phone': joining_form.emergency_contact_mobile,
                'email': joining_form.emergency_contact_email,
                'street': joining_form.emergency_contact_address,
            }
            
            # Check if 'type' field exists to avoid errors in Odoo 17
            if self._field_exists('res.partner', 'type'):
                emergency_contact_vals['type'] = 'contact'
            
            _logger.info(f"Creating emergency contact partner with values: {emergency_contact_vals}")
            emergency_contact = self.env['res.partner'].sudo().create(emergency_contact_vals)
            
            # Only add emergency fields if they exist
            if self._field_exists('hr.employee', 'emergency_contact'):
                employee_vals['emergency_contact'] = joining_form.emergency_contact_name
            if self._field_exists('hr.employee', 'emergency_phone'):
                employee_vals['emergency_phone'] = joining_form.emergency_contact_mobile
        
        # Log the values being used to create the employee
        _logger.info(f"Creating employee with values: {employee_vals}")
        
        # Create the employee
        try:
            employee = self.env['hr.employee'].sudo().create(employee_vals)
            self.employee_created = True
            self.employee_id = employee.id
            _logger.info(f"Employee created successfully with ID: {employee.id}")
            
            # Now that we have the employee, try to set the private address
            if has_address_home_id:
                try:
                    employee.write({'address_home_id': partner.id})
                    _logger.info("Successfully set address_home_id")
                except Exception as e:
                    _logger.warning(f"Could not set address_home_id: {str(e)}")
            elif has_address_id:
                try:
                    employee.write({'address_id': partner.id})
                    _logger.info("Successfully set address_id")
                except Exception as e:
                    _logger.warning(f"Could not set address_id: {str(e)}")
            elif has_partner_id:
                try:
                    employee.write({'partner_id': partner.id})
                    _logger.info("Successfully set partner_id")
                except Exception as e:
                    _logger.warning(f"Could not set partner_id: {str(e)}")
            else:
                _logger.warning("Could not find a compatible private address field on the employee model")
                
        except Exception as e:
            _logger.error(f"Error creating employee: {str(e)}")
            raise UserError(_("Error creating employee: %s") % str(e))
        
        # Create user if requested
        if self.create_user and self.official_email:
            try:
                user_vals = {
                    'name': self.name,
                    'login': self.official_email,
                    'password': self.password,
                    'email': self.official_email,
                    'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
                }
                _logger.info(f"Creating user with values: {user_vals}")
                user = self.env['res.users'].sudo().create(user_vals)
                
                # Link the employee to the user
                try:
                    employee.write({'user_id': user.id})
                    _logger.info(f"Linked employee {employee.id} to user {user.id}")
                except Exception as e:
                    _logger.warning(f"Could not link employee to user: {str(e)}")
                    
                self.user_created = True
                self.user_id = user.id
                _logger.info(f"User created successfully with ID: {user.id}")
            except Exception as e:
                _logger.error(f"Error creating user: {str(e)}")
                # Don't raise an exception here, as we've already created the employee
                # Just log the error and continue
                self.user_created = False
        
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
