odoo.define('gio_obstgemuese_website.registration', function (require) {
"use strict";

var config = require('web.config');
var core = require('web.core');
const dom = require('web.dom');
var Dialog = require('web.Dialog');
var utils = require('web.utils');
var publicWidget = require('web.public.widget');
const session = require('web.session');
const {ReCaptcha} = require('google_recaptcha.ReCaptchaV3');

var _t = core._t;


publicWidget.registry.registration = publicWidget.Widget.extend({
    selector: "#reg-container",
    disabledInEditableMode: false,
    read_events: {
        'click #shippingaddress': '_onClickShippingAddress',
        'input #login' :'_validateLogin',
        'input #password':'_validatePwd',
        'input #Salutation':'_validateSalutation',
        'input #name' : '_validateFirstName',
        'input #lastname' : '_validateLastName',
        'input #signuplogin':'_validateSignupLogin',
        'input #signuppassword':'_validateSignupPassword',
        'input #street':'_validateStreet',
        'input #postcode':'_validatePostcode',
        'input #location':'_validateLocation',
        'input #country':'_validateCountry',
        'input #shippingSalutation':'_validateShippingSalutation',
        'input #shippingname': '_validateShippingFname',
        'input #shippinglastname': '_validateShippingLname',
        'input #shippingstreet' : '_validateShippingStreet',
        'input #shippingpostcode':'_validateShippingPostCode',
        'input #shippinglocation' : '_validateShippingLocation',
        'input #shippingcountry':'_validateShippingCountry',

    },

    _onClickShippingAddress: async function () {
       let shippingaddress = document.getElementById("showshippingaddress");
       shippingaddress.classList.toggle('hide-shipping')
    },
    _validateLogin: async function(){
        const $signupEmail = $('#login').val()
        if ($signupEmail.length <= 0){
             document.getElementById("loginEmailValidationError").innerHTML ="This field is required";
        }
        else if(!$signupEmail.match(/.+@.+/)){
            document.getElementById("loginEmailValidationError").innerHTML ="Please enter a valid email id";
        }
        else{
            document.getElementById("loginEmailValidationError").innerHTML ="";
        }
    },
    _validatePwd: async function(){
        let pwd = $('#password');
        if(pwd.val().length <= 0) {
           document.getElementById("loginPwdValidationError").innerHTML ="This field is required";
        }
        else if(pwd.val().length <= 8){
            document.getElementById("loginPwdValidationError").innerHTML ="Please enter atleast 8 characters";
        }
        else{
            document.getElementById("loginPwdValidationError").innerHTML ="";
        }

    },
    _validateSalutation:async function(){
        let salutation = $('#Salutation')
        if(salutation.val().length <= 0){
            document.getElementById("signupSalutationValidationError").innerHTML ="This field is required";
        }
        else{
            document.getElementById("signupSalutationValidationError").innerHTML ="";
        }
    },
    _validateFirstName : async function(){
        let fname = $('#name')
        if(fname.val().length <= 0){
            document.getElementById("signupFnameValidationError").innerHTML ="This field is required";
        }
        else{
            document.getElementById("signupFnameValidationError").innerHTML ="";
        }
    },
    _validateLastName:async function(){
        let lname = $('#lastname')
        if(lname.val().length <= 0){
            document.getElementById("signupLnameValidationError").innerHTML ="This field is required";
        }
        else{
            document.getElementById("signupLnameValidationError").innerHTML ="";
        }
    },
    _validateSignupLogin : async function(){
        const $signupEmail = $('#signuplogin').val()
        console.log($signupEmail)
        const $errormsg=$('#signupEmailValidationError');
        if ($signupEmail.length <= 0){
             document.getElementById("signupEmailValidationError").innerHTML ="This field is required";
        }
        else if(!$signupEmail.match(/.+@.+/)){
            document.getElementById("signupEmailValidationError").innerHTML ="Please enter a valid email id";
        }
        else{
            document.getElementById("signupEmailValidationError").innerHTML ="";
        }

    },
    _validateSignupPassword : async function(){
        let pwd = $('#signuppassword');
        if(pwd.val().length <= 0) {
           document.getElementById("signupPwdValidationError").innerHTML ="This field is required";
        }
        else if(pwd.val().length <= 8){
            document.getElementById("signupPwdValidationError").innerHTML ="Please enter atleast 8 characters";
        }
        else{
            document.getElementById("signupPwdValidationError").innerHTML ="";
          }
    },
    _validateStreet : async function(){
     let street = $('#street')
        if(street.val().length <= 0){
            document.getElementById("signupStreetValidationError").innerHTML ="This field is required";
        }
        else{
            document.getElementById("signupStreetValidationError").innerHTML ="";
        }
    },
    _validatePostcode : async function(){
        let postcode = $('#postcode')
        if(postcode.val().length <= 0){
            document.getElementById("signupPostCodeValidationError").innerHTML ="This field is required";
        }
        else{
            document.getElementById("signupPostCodeValidationError").innerHTML ="";
        }
    },

    _validateLocation : async function(){
         let location = $('#location')
        if(location.val().length <= 0){
            document.getElementById("signupLocationValidationError").innerHTML ="This field is required";
        }
        else{
            document.getElementById("signupLocationValidationError").innerHTML ="";
        }
    },

    _validateCountry : async function(){
        let country = $('#country')
        if(country.val().length <= 0){
            document.getElementById("signupCountryValidationError").innerHTML ="This field is required";
        }
        else{
            document.getElementById("signupCountryValidationError").innerHTML ="";
        }
    },

    _validateShippingSalutation : async function(){
         let salutation = $('#shippingSalutation')
        if(salutation.val().length <= 0){
            document.getElementById("shippingSalutationValidationError").innerHTML ="This field is required";
        }
        else{
            document.getElementById("shippingSalutationValidationError").innerHTML ="";
        }
    },

    _validateShippingFname : async function(){
        let fname = $('#shippingname')
        if(fname.val().length <= 0){
            document.getElementById("shippingFNameValidationError").innerHTML ="This field is required";
        }
        else{
            document.getElementById("shippingFNameValidationError").innerHTML ="";
        }
    },

    _validateShippingLname : async function(){
        let lname = $('#shippinglastname')
        if(lname.val().length <= 0){
            document.getElementById("shippingLnameValidationError").innerHTML ="This field is required";
        }
        else{
            document.getElementById("shippingLnameValidationError").innerHTML ="";
        }
    },

    _validateShippingStreet : async function(){
        let street = $('#shippingstreet')
        if(street.val().length <= 0){
            document.getElementById("shippingStreetValidationError").innerHTML ="This field is required";
        }
        else{
            document.getElementById("shippingStreetValidationError").innerHTML ="";
        }
    },

    _validateShippingPostCode : async function(){
        let postcode = $('#shippingpostcode')
        if(postcode.val().length <= 0){
            document.getElementById("shippingPostCodeValidationError").innerHTML ="This field is required";
        }
        else{
            document.getElementById("shippingPostCodeValidationError").innerHTML ="";
        }
    },

    _validateShippingLocation : async function(){
        let location = $('#shippinglocation')
        if(location.val().length <= 0){
            document.getElementById("shippingLocationValidationError").innerHTML ="This field is required";
        }
        else{
            document.getElementById("shippingLocationValidationError").innerHTML ="";
        }
    },

    _validateShippingCountry : async function(){
        let country = $('#shippingcountry')
        if(country.val().length <= 0){
            document.getElementById("shippingCountryValidationError").innerHTML ="This field is required";
        }
        else{
            document.getElementById("shippingCountryValidationError").innerHTML ="";
        }
    }

});
});
