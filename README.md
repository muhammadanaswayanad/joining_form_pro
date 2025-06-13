# Joining Form Pro

## Overview
Joining Form Pro is a comprehensive Odoo 17 module designed to streamline the employee onboarding process. It provides a public-facing form where candidates can submit their joining information, which HR managers can then review, approve, and use to create employee records and user accounts.

## Features

### Public Joining Form
- Publicly accessible form at `/joining/form` requiring no login
- Comprehensive data collection including:
  - Personal information
  - Government IDs & documents
  - Banking details
  - Education qualifications
  - Work experience
  - Skills & certifications
  - Social media profiles
  - Emergency contacts
  - Family information
  - Document uploads (resume, photo, ID cards, bank documents)

### HR Management System
- Complete workflow management with multiple stages:
  - Draft (New Submission)
  - Under Review
  - Approved
  - Employee Created
  - Rejected
- Automatic notifications to the HR team upon new submissions
- Advanced filtering and grouping capabilities
- Chatter integration for communication and activity tracking

### Employee & User Creation
- One-click wizard to convert approved forms into employee records
- Optional automatic user account creation with:
  - Company email assignment
  - Secure password generation
  - Role/group assignment
- Direct links to created employee and user records

### Security
- Granular access control with record rules:
  - HR managers have full access
  - Employees can only view their own forms
  - Public users can submit but not view records
- Protected sensitive information

### Portal Integration
- Employees can view their joining form data in their portal
- Self-service access to submission details

## Technical Details

> **Important Note**: This module is built for Odoo 17.0 which has removed support for the traditional `attrs` attribute in view definitions. Instead, we use the direct attribute syntax (e.g., `invisible="state != 'draft'"` instead of `attrs="{'invisible': [('state', 'not in', ['draft'])]}"`) throughout the views.

### Module Structure
```
joining_form_pro/
├── __init__.py                    # Root module loader
├── __manifest__.py                # Module manifest
├── models/                        # Data models
│   ├── __init__.py                # Models loader
│   └── joining_form.py            # Main model definition
├── controllers/                   # Web controllers
│   ├── __init__.py                # Controllers loader
│   └── main.py                    # Form submission controllers
├── views/                         # UI definitions
│   ├── joining_form_views.xml     # Backend views
│   ├── joining_form_templates.xml # Public form templates
│   └── menu_views.xml             # Menu structure
├── wizard/                        # Wizard models
│   ├── __init__.py                # Wizard loader
│   ├── create_employee_user_wizard.py     # Employee creation wizard model
│   └── create_employee_user_views.xml     # Wizard view
├── security/                      # Access control
│   ├── ir.model.access.csv        # Access rights
│   └── security.xml               # Record rules
└── static/                        # Frontend assets
    └── src/
        ├── css/                   # Stylesheets
        │   └── joining_form.css
        ├── js/                    # JavaScript
        │   └── joining_form.js
        └── img/                   # Images
            └── icon.png
```

### Key Models

#### joining.form
Main model that stores all candidate information, with states for tracking the approval process.

**Key fields:**
- Personal information fields (name, contact details, etc.)
- Government ID fields (Aadhaar, PAN, etc.)
- Education and employment history
- Document attachments (resume, photo, etc.)
- State field for workflow management

**Methods:**
- State transition methods (approval, rejection, etc.)
- Wizard launcher for employee creation

#### create.employee.user.wizard
Transient model for creating employee records and user accounts from joining form data.

**Key features:**
- Data mapping from joining form to employee record
- Contact creation for employee address book
- User account creation with secure password generation
- Employee-user linkage

### Controllers

#### JoiningFormController
Handles public form rendering and submission processing.

**Key routes:**
- `/joining/form` - Renders the public form
- `/joining/form/submit` - Processes form submissions
- `/joining/form/success` - Thank you page

#### JoiningFormCustomerPortal
Extends the portal to show joining form data to employees.

### Security Configuration

#### Access Rights (ir.model.access.csv)
- HR Managers: Full CRUD access to joining forms and wizard
- Regular Users: Read-only access to joining forms
- Public Users: Create-only access to joining forms (submission)
- Portal Users: Read-only access to their own forms

#### Record Rules (security.xml)
- HR Managers can see all forms
- Employees can only see their own forms
- Portal users can only see forms linked to their employee record

## Extending the Module

### Adding New Fields

1. Add the field to the `joining.form` model in `models/joining_form.py`
2. Update the form view in `views/joining_form_views.xml`
3. Add the field to the public template in `views/joining_form_templates.xml`
4. Update the controller's submission handler in `controllers/main.py`
5. If needed, add the field to the employee creation wizard in `wizard/create_employee_user_wizard.py`

### Adding New Features

#### Document Management
- Consider adding document management features using Odoo's document module
- Implement OCR functionality for document verification

#### Approval Workflows
- Add multi-level approval workflows with specific roles
- Implement conditional approvals based on department or position

#### Integration Points
- Integrate with recruitment process (hr_recruitment)
- Connect to contract management (hr_contract)
- Link to payroll for automatic salary setup

#### Analytics
- Add reporting dashboards for HR analytics
- Track conversion rates from submission to employee creation

### Performance Considerations

#### For Scaling
- Implement attachment compression for large documents
- Add caching for frequently accessed data
- Consider using cron jobs for background processing of large batches

#### Database Optimization
- Add indexes for frequently searched fields
- Implement archiving mechanism for old records
- Set up regular database maintenance

## API Usage

### Form Submission API
The module does not expose an API by default, but you can extend the controllers to add JSON API endpoints:

Example implementation:
```python
@http.route(['/api/v1/joining/submit'], type='json', auth='public', methods=['POST'], csrf=False)
def api_submit_joining_form(self, **post):
    # Process API submission
    # Return success/failure response
```

### Integration with External Systems
- Add API endpoints for integration with external recruitment platforms
- Implement webhooks for event notifications

## Deployment Recommendations

### Production Setup
- Ensure proper security headers for the public form
- Set up rate limiting to prevent form submission abuse
- Configure proper backup strategy for uploaded documents

### Maintenance
- Regular updates to keep compatible with Odoo core updates
- Periodic security reviews of public form endpoints
- Monitoring of database size due to document attachments

## Future Roadmap

### Short-term Enhancements
- Mobile-friendly form with responsive design improvements
- Multi-step form with save & continue functionality
- Email verification flow for candidates

### Medium-term Features
- Background verification integration
- Digital signature for offer acceptance
- Document expiration tracking and reminders

### Long-term Vision
- Full employee lifecycle management
- Integration with training & development
- Performance management linkage

## Troubleshooting Common Issues

### Form Submission Errors
- Check file size limits for uploads
- Verify email configuration for notifications
- Inspect server logs for detailed error messages

### Employee Creation Issues
- Ensure required fields are properly mapped
- Check for duplicate email addresses in users
- Verify HR manager has proper permissions

## Contributing Guidelines

### Code Style
- Follow Odoo coding standards
- Use proper docstrings for all methods
- Implement appropriate test cases

### Pull Request Process
1. Create feature branches for new features
2. Include documentation updates with code changes
3. Ensure all tests pass before submission

## License
LGPL-3

---

*This module was initially developed in June 2025 for Odoo 17.*
