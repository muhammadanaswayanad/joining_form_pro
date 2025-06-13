from odoo import models, fields, api, _
import random
import string
import logging

_logger = logging.getLogger(__name__)

MARITAL_STATUS = [
    ('single', 'Single'),
    ('married', 'Married'),
    ('divorced', 'Divorced'),
    ('widowed', 'Widowed')
]

GENDER_SELECTION = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other')
]

BLOOD_GROUPS = [
    ('a+', 'A+'),
    ('a-', 'A-'),
    ('b+', 'B+'),
    ('b-', 'B-'),
    ('o+', 'O+'),
    ('o-', 'O-'),
    ('ab+', 'AB+'),
    ('ab-', 'AB-'),
]

EDUCATION_TYPE = [
    ('full_time', 'Full Time'),
    ('part_time', 'Part Time'),
    ('distance', 'Distance Education')
]

class JoiningForm(models.Model):
    _name = 'joining.form'
    _description = 'Candidate Joining Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'create_date desc'

    # Stages for form processing
    state = fields.Selection([
        ('draft', 'New Submission'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('employee_created', 'Employee Created'),
        ('rejected', 'Rejected')
    ], default='draft', tracking=True, string='Status')

    # Personal Information
    name = fields.Char(string='Full Name', required=True, tracking=True)
    personal_number = fields.Char(string='Personal Number', required=True, tracking=True)
    branch_id = fields.Many2one('employee.branch', string='Branch')
    email_id = fields.Char(string='Email ID', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='Department')
    designation = fields.Char(string='Designation', required=True)
    date_of_joining = fields.Date(string='Date Of Joining')
    address = fields.Text(string='Address', required=True)
    gender = fields.Selection(GENDER_SELECTION, string='Gender')
    date_of_birth = fields.Date(string='Date Of Birth')
    marital_status = fields.Selection(MARITAL_STATUS, string='Marital Status')
    
    # Family Information (conditionally required based on marital status)
    spouse_name = fields.Char(string='Name Of Spouse')
    children_count = fields.Integer(string='Number of Children', default=0)
    
    # Government IDs
    pf_uan_number = fields.Char(string='PF UAN Number')
    esi_ip_number = fields.Char(string='ESI IP Number')
    blood_group = fields.Selection(BLOOD_GROUPS, string='Blood Group')
    aadhaar_number = fields.Char(string='Aadhaar Number')
    pan_number = fields.Char(string='Pan Card Number')
    
    # Skills and Qualifications
    skills = fields.Text(string='Skills')
    certification = fields.Text(string='Certification')
    hobbies = fields.Text(string='Hobbies and Interests')
    
    # Social Media
    is_social_media_active = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Are you active in social media')
    instagram_url = fields.Char(string='Instagram URL')
    facebook_url = fields.Char(string='Facebook URL')
    linkedin_url = fields.Char(string='LinkedIn URL')
    
    # Anchoring Experience
    has_anchoring_exp = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Have you done anchoring')
    
    # Banking Details
    bank_name = fields.Char(string='Bank Name')
    bank_account_number = fields.Char(string='Bank Account Number')
    bank_branch = fields.Char(string='Bank Branch')
    ifsc_code = fields.Char(string='IFSC Code')
    micr_code = fields.Char(string='MICR Code')
    
    # Work Location
    work_location_id = fields.Many2one('hr.work.location', string='Work Location (city)')
    work_place = fields.Char(string='Work Place (office)')
    
    # Education
    edu_college_name = fields.Char(string='College Name')
    edu_type = fields.Selection(EDUCATION_TYPE, string='Education Type')
    edu_degree = fields.Char(string='Degree')
    edu_specialization = fields.Char(string='Specialization')
    edu_passout_date = fields.Char(string='Passed out Month and Year')
    
    # Previous Employment
    prev_company_name = fields.Char(string='Previous Employment Company Name')
    prev_company_location = fields.Char(string='Previous Employment Company Location')
    prev_designation = fields.Char(string='Previous Employment Company Designation')
    prev_tenure = fields.Char(string='Previous Employment Company Tenure')
    total_experience = fields.Char(string='Total Years of Experience')
    
    # Emergency Contact
    emergency_contact_name = fields.Char(string='Emergency Contact Person Name')
    emergency_contact_relation = fields.Char(string='Emergency Contact Person Relationship')
    emergency_contact_mobile = fields.Char(string='Emergency Contact Person Mobile Number')
    emergency_contact_email = fields.Char(string='Emergency Contact Person Email ID')
    emergency_contact_address = fields.Text(string='Emergency Contact Person Correspondence Address')
    emergency_allergies = fields.Text(string='Emergency Details - Any Allergies specifically')
    
    # Nominee Details
    nominee_name = fields.Char(string='Nominee Name')
    nominee_relation = fields.Char(string='Nominee Relationship')
    nominee_id_proof = fields.Char(string='Nominee ID Proof (PAN or Aadhar Number)')
    
    # Attachments
    resume = fields.Binary(string='Resume', attachment=True)
    resume_filename = fields.Char("Resume Filename")
    photo = fields.Binary(string='Photo', attachment=True)
    photo_filename = fields.Char("Photo Filename")
    aadhaar_card = fields.Binary(string='Aadhaar Card', attachment=True)
    aadhaar_card_filename = fields.Char("Aadhaar Card Filename")
    pan_card = fields.Binary(string='PAN Card', attachment=True)
    pan_card_filename = fields.Char("PAN Card Filename")
    bank_passbook = fields.Binary(string='Bank Passbook', attachment=True)
    bank_passbook_filename = fields.Char("Bank Passbook Filename")
    
    # System fields
    employee_id = fields.Many2one('hr.employee', string='Created Employee', readonly=True)
    user_id = fields.Many2one('res.users', string='Created User', readonly=True)
    submitted_from_public = fields.Boolean(string='Submitted from public form', default=False)
    company_id = fields.Many2one('res.company', string='Company', 
                                 default=lambda self: self.env.company,
                                 required=True)
    
    _sql_constraints = [
        ('email_unique', 'unique(email_id)', 'This email is already registered in the system.'),
    ]

    @api.onchange('marital_status')
    def _onchange_marital_status(self):
        if self.marital_status != 'married':
            self.spouse_name = False
            self.children_count = 0
    
    @api.onchange('is_social_media_active')
    def _onchange_social_media_active(self):
        if self.is_social_media_active == 'no':
            self.instagram_url = False
            self.facebook_url = False
            self.linkedin_url = False

    def action_under_review(self):
        self.state = 'under_review'
        
    def action_approve(self):
        self.state = 'approved'

    def action_reject(self):
        self.state = 'rejected'
        
    def action_reset_to_draft(self):
        self.state = 'draft'
    
    def action_create_employee_wizard(self):
        return {
            'name': _('Create Employee and User'),
            'type': 'ir.actions.act_window',
            'res_model': 'create.employee.user.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_joining_form_id': self.id,
                'default_name': self.name,
                'default_personal_mobile': self.personal_number,
                'default_personal_email': self.email_id,
                'default_department_id': self.department_id.id if self.department_id else False,
                'default_job_title': self.designation,
            }
        }
        
    def action_view_employee(self):
        """Open the related employee form view"""
        self.ensure_one()
        if not self.employee_id or not self.employee_id.exists():
            raise UserError(_("No employee record found."))
            
        return {
            'name': _('Employee'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'form',
            'res_id': self.employee_id.id,
            'target': 'current',
        }
        
    def action_view_user(self):
        """Open the related user form view"""
        self.ensure_one()
        if not self.user_id or not self.user_id.exists():
            raise UserError(_("No user record found."))
            
        return {
            'name': _('User'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'form',
            'res_id': self.user_id.id,
            'target': 'current',
        }
