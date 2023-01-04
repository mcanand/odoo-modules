odoo.define('gio_obstgemuese_theme.contactus', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var PortalSidebar = require('portal.PortalSidebar');
var ajax = require("web.ajax");
var core = require('web.core');
var newsletter = require('gio_obstgemuese_theme.newsletter');
console.log(publicWidget)

publicWidget.registry.contactus = publicWidget.Widget.extend({
    selector: '.contact_wrap',
    events:{

    },
    start:function(){
        this.initMap()
        window.initMap = initMap;
    },
    initMap:function() {
          const uluru = { lat: -25.344, lng: 131.031 };
          const map = new google.maps.Map(document.getElementById("g_map"), {
            zoom: 12,
            center: uluru,
            zoomControl: false,
            mapTypeControl: false,
            scaleControl: false,
            streetViewControl: false,
            rotateControl: false,
            fullscreenControl: false
          });
          const marker = new google.maps.Marker({
            position: uluru,
            map: map,
          });
    },
    });
    $(document).ready(function () {
//        $('#registration').load('/shop/address');

        $('.nav-tabs > li a[title]').tooltip();

    //Wizard
        $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
            var target = $(e.target);
            if (target.parent().hasClass('disabled')) {
                return false;
            }
        });

        $(".next-step").click(function (e) {
            var active = $('.wizard .nav-tabs li.active');
            active.next().removeClass('disabled');
            nextTab(active);
        });
        $(".prev-step").click(function (e) {
            var active = $('.wizard .nav-tabs li.active');
            prevTab(active);

        });
    });

    function nextTab(elem) {
        $(elem).next().find('a[data-toggle="tab"]').click();
    }
    function prevTab(elem) {
        $(elem).prev().find('a[data-toggle="tab"]').click();
    }

    $('.nav-tabs').on('click', 'li', function() {
        $('.nav-tabs li.active').removeClass('active');
        $(this).addClass('active');
    });
});
