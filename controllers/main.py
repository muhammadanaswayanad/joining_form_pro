from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import base64
import logging

_logger = logging.getLogger(__name__)

class JoiningFormController(http.Controller):
    
    @http.route(['/joining/form'], type='http', auth='public', website=True)
    def joining_form_public(self, **kw):
        departments = request.env['hr.department'].sudo().search([])
        branches = request.env['employee.branch'].sudo().search([])
        work_locations = request.env['hr.work.location'].sudo().search([])
        values = {
            'departments': departments,
            'branches': branches,
            'work_locations': work_locations
        }
        return request.render("joining_form_pro.joining_form_template", values)
    
    @http.route(['/joining/form/submit'], type='http', auth='public', website=True, method=['POST'])
    def joining_form_submit(self, **post):
        # Create binary data for uploaded files
        resume = post.get('resume', False)
        photo = post.get('photo', False)
        aadhaar_card = post.get('aadhaar_card', False)
        pan_card = post.get('pan_card', False)
        bank_passbook = post.get('bank_passbook', False)
        
        # Create form values from post data
        form_vals = {
            'name': post.get('name'),
            'personal_number': post.get('personal_number'),
            'branch_id': int(post.get('branch_id')) if post.get('branch_id') else False,
            'email_id': post.get('email_id'),
            'department_id': int(post.get('department_id')) if post.get('department_id') else False,
            'designation': post.get('designation'),
            'date_of_joining': post.get('date_of_joining') or False,
            'address': post.get('address'),
            'gender': post.get('gender'),
            'date_of_birth': post.get('date_of_birth') or False,
            'marital_status': post.get('marital_status'),
            'spouse_name': post.get('spouse_name'),
            'children_count': int(post.get('children_count', '0') or '0'),
            'pf_uan_number': post.get('pf_uan_number'),
            'esi_ip_number': post.get('esi_ip_number'),
            'blood_group': post.get('blood_group'),
            'skills': post.get('skills'),
            'certification': post.get('certification'),
            'hobbies': post.get('hobbies'),
            'is_social_media_active': post.get('is_social_media_active'),
            'instagram_url': post.get('instagram_url'),
            'facebook_url': post.get('facebook_url'),
            'linkedin_url': post.get('linkedin_url'),
            'has_anchoring_exp': post.get('has_anchoring_exp'),
            'bank_name': post.get('bank_name'),
            'bank_account_number': post.get('bank_account_number'),
            'bank_branch': post.get('bank_branch'),
            'ifsc_code': post.get('ifsc_code'),
            'micr_code': post.get('micr_code'),
            'aadhaar_number': post.get('aadhaar_number'),
            'pan_number': post.get('pan_number'),
            'work_location_id': int(post.get('work_location_id')) if post.get('work_location_id') else False,
            'work_place': post.get('work_place'),
            'edu_college_name': post.get('edu_college_name'),
            'edu_type': post.get('edu_type'),
            'edu_degree': post.get('edu_degree'),
            'edu_specialization': post.get('edu_specialization'),
            'edu_passout_date': post.get('edu_passout_date'),
            'prev_company_name': post.get('prev_company_name'),
            'prev_company_location': post.get('prev_company_location'),
            'prev_designation': post.get('prev_designation'),
            'prev_tenure': post.get('prev_tenure'),
            'total_experience': post.get('total_experience'),
            'emergency_contact_name': post.get('emergency_contact_name'),
            'emergency_contact_relation': post.get('emergency_contact_relation'),
            'emergency_contact_mobile': post.get('emergency_contact_mobile'),
            'emergency_contact_email': post.get('emergency_contact_email'),
            'emergency_contact_address': post.get('emergency_contact_address'),
            'emergency_allergies': post.get('emergency_allergies'),
            'nominee_name': post.get('nominee_name'),
            'nominee_relation': post.get('nominee_relation'),
            'nominee_id_proof': post.get('nominee_id_proof'),
            'submitted_from_public': True,
        }
        
        # Process file uploads if present
        if resume:
            form_vals.update({
                'resume': base64.b64encode(resume.read()),
                'resume_filename': resume.filename
            })
        
        if photo:
            form_vals.update({
                'photo': base64.b64encode(photo.read()),
                'photo_filename': photo.filename
            })
            
        if aadhaar_card:
            form_vals.update({
                'aadhaar_card': base64.b64encode(aadhaar_card.read()),
                'aadhaar_card_filename': aadhaar_card.filename
            })
        
        if pan_card:
            form_vals.update({
                'pan_card': base64.b64encode(pan_card.read()),
                'pan_card_filename': pan_card.filename
            })
            
        if bank_passbook:
            form_vals.update({
                'bank_passbook': base64.b64encode(bank_passbook.read()),
                'bank_passbook_filename': bank_passbook.filename
            })
            
        # Create the joining form submission
        try:
            joining_form = request.env['joining.form'].sudo().create(form_vals)
            # Send notification email to HR team
            hr_group = request.env.ref('hr.group_hr_manager')
            hr_users = hr_group.users
            if hr_users:
                joining_form.sudo().message_subscribe(partner_ids=hr_users.mapped('partner_id').ids)
                joining_form.sudo().message_post(
                    body=_('New joining form submitted by %s') % form_vals.get('name'),
                    subject=_('New Joining Form Submission')
                )
            return request.render("joining_form_pro.joining_form_thank_you", {})
        except Exception as e:
            _logger.error("Error creating joining form: %s", str(e))
            values = {
                'error_message': _('An error occurred. Please try again or contact support.'),
                'departments': request.env['hr.department'].sudo().search([])
            }
            return request.render("joining_form_pro.joining_form_template", values)
    
    @http.route(['/joining/form/success'], type='http', auth='public', website=True)
    def joining_form_success(self, **kw):
        return request.render("joining_form_pro.joining_form_thank_you", {})


class JoiningFormCustomerPortal(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'joining_form_count' in counters:
            values['joining_form_count'] = request.env['joining.form'].search_count([
                ('employee_id.user_id', '=', request.env.user.id)
            ])
        return values
    
    @http.route(['/my/joining-form'], type='http', auth='user', website=True)
    def portal_my_joining_form(self, **kw):
        joining_forms = request.env['joining.form'].search([
            ('employee_id.user_id', '=', request.env.user.id)
        ])
        values = {
            'joining_forms': joining_forms,
            'page_name': 'joining_form',
        }
        return request.render("joining_form_pro.portal_my_joining_forms", values)
