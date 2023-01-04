odoo.define('gio_obstgemuese_theme.newsletter', function (require) {
"use strict";

var core = require('web.core');
var publicWidget = require('web.public.widget');
const {ReCaptcha} = require('google_recaptcha.ReCaptchaV3');

var _t = core._t;

publicWidget.registry.newsletter_subscribe = publicWidget.Widget.extend({
    selector: ".news_letter_row",
    disabledInEditableMode: false,
    read_events: {
        'click .js_subscribe_btn': '_onSubscribeClick',
    },

    init: function () {
        this._super(...arguments);
        this._recaptcha = new ReCaptcha();
    },
    start: function () {
        var def = this._super.apply(this, arguments);
        if (this.editableMode) {
            // Since there is an editor option to choose whether "Thanks" button
            // should be visible or not, we should not vary its visibility here.
            return def;
        }
        const always = this._updateView.bind(this);
        return Promise.all([def, this._rpc({
            route: '/website_mass_mailing/is_subscriber',
            params: {
                'list_id': 1,
            },
        }).then(always).guardedCatch(always)]);
    },
     _updateView(data) {
        const isSubscriber = data.is_subscriber;
        const subscribeBtnEl = this.$target[0].querySelector('.js_subscribe_btn');
        const thanksBtnEl = this.$target[0].querySelector('.js_subscribed_btn');
        const emailInputEl = this.$target[0].querySelector('input.js_subscribe_email');

        subscribeBtnEl.disabled = isSubscriber;
        emailInputEl.value = data.email || '';
        emailInputEl.disabled = isSubscriber;
        // Compat: remove d-none for DBs that have the button saved with it.
//        this.$target[0].classList.remove('d-none');
//
//        subscribeBtnEl.classList.toggle('d-none', !!isSubscriber);
//        thanksBtnEl.classList.toggle('d-none', !isSubscriber);
    },

    _onSubscribeClick: async function () {
        var self = this;
        var $email = this.$(".js_subscribe_email:visible");
        var cargobike = $('.cargobike_check').is(":checked")
        var performance = $('.performance_check').is(":checked")
        if ($email.length && !$email.val().match(/.+@.+/)) {
            this.$target.addClass('o_has_error').find('.form-control').addClass('is-invalid');
            return false;
        }
        this.$target.removeClass('o_has_error').find('.form-control').removeClass('is-invalid');
        const tokenObj = await this._recaptcha.getToken('website_mass_mailing_subscribe');
        if (tokenObj.error) {
            self.displayNotification({
                type: 'danger',
                title: _t("Error"),
                message: tokenObj.error,
                sticky: true,
            });
            return false;
        }
        this._rpc({
            route: '/website_mass_mailing/subscribe',
            params: {
                'list_id': 1,
                'cargobike':cargobike,
                'performance':performance,
                'email': $email.length ? $email.val() : false,
                recaptcha_token_response: tokenObj.token,
            },
        }).then(function (result) {
            let toastType = result.toast_type;
            if (toastType === 'success') {
                self.$(".js_subscribe_btn").prop('disabled', !!result);
                self.$('input.js_subscribe_email').prop('disabled', !!result);
                self.$('.js_newsletter_message').html('subscribed')
                const $popup = self.$target.closest('.o_newsletter_modal');
                if ($popup.length) {
                    $popup.modal('hide');
                }
            }
            self.displayNotification({
                type: toastType,
                title: toastType === 'success' ? _t('Success') : _t('Error'),
                message: result.toast_content,
                sticky: true,
            });
        });
    },
});
});
