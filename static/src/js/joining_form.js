odoo.define('joining_form_pro.form', function (require) {
    'use strict';
    
    const publicWidget = require('web.public.widget');
    
    publicWidget.registry.JoiningFormWidget = publicWidget.Widget.extend({
        selector: '#wrap:has(form[action="/joining/form/submit"])',
        events: {
            'change #marital_status': '_onChangeMaritalStatus',
            'change input[name="is_social_media_active"]': '_onChangeSocialMedia',
        },
        
        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);
            
            // Add a slight delay to ensure the DOM has fully loaded
            setTimeout(() => {
                this._onChangeMaritalStatus();
                this._onChangeSocialMedia();
                console.log("Widget initialized marital status and social media");
            }, 200);
            
            return def;
        },
        
        /**
         * Show/Hide spouse fields based on marital status
         * @private
         */
        _onChangeMaritalStatus: function () {
            var maritalStatus = this.$('#marital_status').val();
            var spouseFields = this.$('.spouse_field');
            
            if (maritalStatus === 'married') {
                spouseFields.show();
            } else {
                spouseFields.hide();
                // Reset spouse fields when not married
                this.$('#spouse_name').val('');
                this.$('#children_count').val('0');
            }
        },
        
        /**
         * Show/Hide social media URL fields
         * @private
         */
        _onChangeSocialMedia: function () {
            var isSocialActive = $("input[name='is_social_media_active']:checked").val();
            var socialUrlFields = this.$('.social_media_urls');
            
            if (isSocialActive === 'yes') {
                socialUrlFields.show();
            } else {
                socialUrlFields.hide();
            }
        },
    });
});
