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
            
            // Only proceed if we're on the right model
            if (this.modelName !== 'create.employee.user.wizard') {
                return;
            }
            
            var record = this.model.get(this.handle);
            
            if (record && record.data) {
                var userName = record.data.name || '';
                var loginUrl = record.data.company_url || '';
                var username = record.data.official_email || '';
                var password = record.data.password || '';
                
                var credentialText = userName + '\n' + loginUrl + '\n\n' + 
                                    'Username: ' + username + '\n' + 
                                    'Password: ' + password;
                
                // Use modern clipboard API with fallback
                try {
                    // Modern approach using the Clipboard API
                    navigator.clipboard.writeText(credentialText).then(function() {
                        self._showCopySuccess();
                    }).catch(function(err) {
                        // Fallback to the old execCommand method
                        self._fallbackCopyTextToClipboard(credentialText);
                    });
                } catch (err) {
                    // If Clipboard API is not available, use fallback
                    self._fallbackCopyTextToClipboard(credentialText);
                }
            }
        },
        
        /**
         * Fallback method to copy text to clipboard using execCommand
         * @private
         * @param {String} text - Text to copy to clipboard
         */
        _fallbackCopyTextToClipboard: function(text) {
            var self = this;
            var textArea = document.createElement("textarea");
            
            // Style the textarea to be invisible
            textArea.style.position = 'fixed';
            textArea.style.top = '0';
            textArea.style.left = '0';
            textArea.style.width = '2em';
            textArea.style.height = '2em';
            textArea.style.padding = '0';
            textArea.style.border = 'none';
            textArea.style.outline = 'none';
            textArea.style.boxShadow = 'none';
            textArea.style.background = 'transparent';
            
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                var successful = document.execCommand('copy');
                if (successful) {
                    self._showCopySuccess();
                } else {
                    self._showCopyError();
                }
            } catch (err) {
                self._showCopyError();
            }
            
            document.body.removeChild(textArea);
        },
        
        /**
         * Show success notification
         * @private
         */
        _showCopySuccess: function() {
            this.displayNotification({
                type: 'success',
                title: _t('Success'),
                message: _t('Credentials copied to clipboard'),
                sticky: false,
                className: 'o_success'
            });
            
            // Visual feedback on the button
            var $button = this.$('.copy-credentials-btn');
            var originalText = $button.html();
            
            $button.html('<i class="fa fa-check mr-1"/> Copied!');
            $button.addClass('btn-success').removeClass('btn-primary');
            
            setTimeout(function() {
                $button.html(originalText);
                $button.addClass('btn-primary').removeClass('btn-success');
            }, 2000);
        },
        
        /**
         * Show error notification
         * @private
         */
        _showCopyError: function() {
            this.displayNotification({
                type: 'danger',
                title: _t('Error'),
                message: _t('Could not copy credentials to clipboard. Please try selecting and copying manually.'),
                sticky: true
            });
        }
    });
});
