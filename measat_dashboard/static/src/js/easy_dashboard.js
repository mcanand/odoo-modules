odoo.define('measat_dashboard.easy_dashboard', function(require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');

    var session = require('web.session');
    var utils = require('web.utils');
    var _t = core._t;
    var QWeb = core.qweb;
    var AbstractAction = require('web.AbstractAction');
    var rpc = require('web.rpc');
    console.log('hai');
    var utils = require('web.utils');



    var HrDashboard = AbstractAction.extend({
        template: "easy_dashboard",
        events: {
            'click .neworders': 'neworders',
            'click .approved_orders': 'approved_orders',
            'click .shipped_orders': 'shipped_orders',
            'click .approved_pdts': 'approved_pdts',
            'click .pending_pdts': 'pending_pdts',
            'click .rejected_pdts': 'rejected_pdts',
            'click .payment_requested': 'payment_requested',
            'click .payment_approved': 'payment_approved',
        },
        init: function(parent, context) {
            this._super(parent, context);
            this.login_employee = true;
            this._super(parent, context);
        },

        start: function() {
            var self = this;
            for (var i in self.breadcrumbs) {
                self.breadcrumbs[i].title = "Dashboard";
            }
            this._rpc({
                model: 'res.users',
                method: 'get_measat_dashboard',
                args: [],
            }).then(function(result) {
                console.log('result', result);
                self.login_employee = result[0];
                $('.o_hr_dashboard').html(QWeb.render('ManagerDashboard', {
                    widget: self
                }));
                // if(self.login_employee.dashboard_access == 'admin'){
                console.log("admin");
                $('.o_hr_dashboard').prepend(QWeb.render('LoginEmployeeDetails', {
                    widget: self
                }));
                self.draw_bar_chart_manager();
                self.draw_bar_chart_manager_product();
            });
            return this._super().then(function() {
                self.$el.parent().addClass('oe_background_grey');
            });
        },

        draw_bar_chart_manager: function(e) {
            var self = this;
            var ctx = this.$el.find('#myBarChartManager')
            var color_list = []
            var color = '#';
            this._rpc({
                model: 'res.users',
                method: 'get_sales_employee',
                args: [],
           }).then(function(arrays) {
                var data = {
                    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"],
                    datasets: [
                    {
                        label: "",
                        backgroundColor: ["red","blue","green","teal","yellow","orange","brown","pink","violet","gray","aqua","lime"],
                        data: arrays[2]
                    },

                    ]

                };


                var config = {
                    type: 'bar',
                    data: data,

                    options: {
                        responsive: true,
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: '12 Months Sale Performance'
                        },
                        scales: {
                            yAxes: [{
                                display: true,
                                stacked: true,
                                ticks: {
                                    suggestedMin: 0, // minimum will be 0, unless there is a lower value.
                                    // OR //
                                    beginAtZero: true // minimum value will be 0.
                                }
                            }],
                            xAxes: [{
                                display: true,
                                stacked: true,

                            }]
                        }
                    }
                }
                var myChart = new Chart(ctx, config);
            });


        },
           getRandomColor: function () {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    },
        draw_bar_chart_manager_product: function(e) {
            var self = this;
            var ctx = this.$el.find('#myBarChartManagerProduct')
            var color_list = []
            var color = '#';
              var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
            this._rpc({
                model: 'res.users',
                method: 'get_sales_distributor',
                args: [],
            }).then(function(array) {
                var data = {
                labels: array[1],
                datasets: [
                {
                label:"",
                data: array[0],
                backgroundColor:bg_color_list,
                              },
                    ]

                };


                var config = {
                    type: 'bar',
                    data: data,

                    options: {
                        responsive: true,
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Total Sales by Distributor'
                        },
                        scales: {
                            yAxes: [{
                                display: true,
                                stacked: true,
                                ticks: {
                                    suggestedMin: 0, // minimum will be 0, unless there is a lower value.
                                    // OR //
                                    beginAtZero: true // minimum value will be 0.
                                }
                            }],
                            xAxes: [{
                                display: true,
                                stacked: true,

                            }]
                        }
                    }
                }
                var myChart = new Chart(ctx, config);
            });


        },


    });

    core.action_registry.add('hr_dashboard_tag', HrDashboard);
    return HrDashboard;
});
