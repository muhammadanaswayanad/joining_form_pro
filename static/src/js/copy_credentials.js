odoo.define('joining_form_pro.copy_credentials', function (require) {
    'use strict';

    var core = require('web.core');
    var _t = core._t;
    var FormController = require('web.FormController');

    FormController.include({
        events: _.extend({}, FormController.prototype.events, {
            'click .copy-credentials-btn': '_onCopyCredentialsClick',
        }),

        /**
         * Copy the employee credentials to clipboard
         * @private
         * @param {MouseEvent} ev
         */
        _onCopyCredentialsClick: function (ev) {
            ev.preventDefault();
            var self = this;
            var record = this.model.get(this.handle);
            
            if (record.data) {
                var userName = record.data.name || '';
                var loginUrl = record.data.company_url || '';
                var username = record.data.official_email || '';
                var password = record.data.password || '';
                
                var credentialText = userName + '\n' + loginUrl + '\n\n' + 
                                    'Username: ' + username + '\n' + 
                                    'Password: ' + password;
                
                navigator.clipboard.writeText(credentialText).then(function() {
                    self.displayNotification({
                        type: 'info',
                        title: _t('Success'),
                        message: _t('Credentials copied to clipboard'),
                    });
                }).catch(function(err) {
                    self.displayNotification({
                        type: 'warning',
                        title: _t('Error'),
                        message: _t('Could not copy credentials: ') + err,
                    });
                });
            }
        },
    });
});
