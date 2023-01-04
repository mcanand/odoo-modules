odoo.define('social_media_dashboard.easy_dashboard', function(require) {
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


    var SMDashboard = AbstractAction.extend({
        template: "easy_dashboard",
        events: {
            'click .sm_dash_box':'_sm_dash_box',
            'click .tablinks ':'_tablinks',
            'click .results': '_open_results',
            'click .contents': '_open_contents',
            'click .audience': '_open_audience',
        },
        init:function(){
            $('.tabcontent').css({'display':'none'})
        },

        start:function(){
        //render dashboard//
            this.$el.html(QWeb.render('SM_dashpost'));
        // tabindex (making display none)//
            this.$el.find('.tabcontent').css({'display':'none'})
            this.$el.find('#Overview').css({'display':'block'})
            this.$el.find('#defaultOpen').addClass('active')
        // draw charts chart.js//
        this._draw_line_chart()
        this._draw_audience_bar_chart()
        this._result_line_chart()
        this._result_line_chart_visit()
        this._donut_chart()
        this._Audience_chart_bar()



        },



        _tablinks:function(event){
            var id = $(event.target).html()
           $('.tabcontent').css({'display':'none'})
           $('#'+id).css({'display':'block'})
           $('.tablinks').removeClass('active')
           if($(event.target).hasClass('active')==false){
                $(event.target).addClass('active ')
           }

        },

        _open_results:function(){
        console.log($('#Result'))
            $('.tabcontent').css({'display':'none'})
            $('#Result').css({'display':'block'})
            $('.tablinks').removeClass('active')
            $('#Resultbtn').addClass('active ')

        },
        _open_contents:function(){
            $('.tabcontent').css({'display':'none'})
            $('#Content').css({'display':'block'})
            $('.tablinks').removeClass('active')
            $('#Contentbtn').addClass('active ')
        },
        _open_audience:function(){
            $('.tabcontent').css({'display':'none'})
            $('#Audience').css({'display':'block'})
            $('.tablinks').removeClass('active')
            $('#Audiencebtn').addClass('active ')
        },
        _draw_line_chart:function(){

            var dash_name = this.$el.find('.dash_name').html()
            if (dash_name == 'Facebook'){
                   var color = '#3b5998'
                   this.$el.find('.fa_report_dash').css({'color': color})
                   var reach = 10000
                   var perc = '30%'
            }
            else if(dash_name == 'Instagram'){
                   var color = '#c11645'
                   this.$el.find('.fa_report_dash').css({'color': color})
            }
            var xl = [10,40,30,5,30,100,70,80,20,10,30,40,50]
            var lbl = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
            const ctx = this.$el.find('#myChart')[0].getContext('2d');
            const myChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: lbl,
                    datasets: [{
                        label: dash_name +' page reach',
                        data: xl,
                        fill: false,
                        borderColor: color,
                        tension: 0.1
                    }],
                },
                options: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: false,
    //                    text: [dash_name+' Page Reach',reach,perc],
    //                    fontSize: 20,
                    },
                    scales: {
                        xAxes: [{
                            ticks:{
                                display:false
                            },
                            gridLines: {
                                display: false,
                                drawBorder: false,
                            }
                        }],
                        yAxes: [{
                           ticks:{
                                display: false
                           },
                            gridLines: {
                                display: false,
                                drawBorder: false,
                            }
                        }]
                    }
                }
            });
        },
        _draw_audience_bar_chart:function(){
            var dash_name = this.$el.find('.dash_name').html()
        if (dash_name == 'facebook'){
               var color = '#3b5998'
               this.$el.find('.fa_report_dash').css({'color': color})
               var reach = 10000
               var perc = '30%'
        }
        else if(dash_name == 'instagram'){
               var color = '#c11645'
               this.$el.find('.fa_report_dash').css({'color': color})
               var reach = 10000
               var perc = '30%'
        }

        var xl = [15,20,30,50,30,20,10]
        var age = ['1-2','2-3','3-4','4-5','6-7','7-8']

        const chart = this.$el.find('#Audience_chart')[0].getContext('2d');
        const myChart = new Chart(chart, {
            type: 'bar',
            data: {
                labels: age,
                datasets: [{
                    label: dash_name +' Male Audience',
                    data: xl,
                    fill: false,
                    borderColor: color,
                    backgroundColor: 'rgb(65, 155, 215)',
                    tension: 0.1
                },
                {
                    label: dash_name +' Female Audience',
                    data: xl,
                    fill: false,
                    borderColor: color,
                    backgroundColor: 'rgb(240, 95, 105)',
                    tension: 0.1
                }],
            },
            options: {
                legend: {
                    display: false
                },
                title: {
                    display: false,

                },
                scales: {
                    xAxes: [{
                        ticks:{
                            display:true
                        },
                        gridLines: {
                            display: false,
                            drawBorder: false,
                        }
                    }],
                    yAxes: [{
                       ticks:{
                            display: false
                       },
                        gridLines: {
                            display: false,
                            drawBorder: false,
                        }
                    }]
                }
            }
        });
        },
        _result_line_chart:function(){
            var dash_name = this.$el.find('.dash_name').html()
            if (dash_name == 'Facebook'){
                   var color = '#3b5998'
                   this.$el.find('.fa_report_dash').css({'color': color})
                   var reach = 10000
                   var perc = '30%'
            }
            else if(dash_name == 'Instagram'){
                   var color = '#c11645'
                   this.$el.find('.fa_report_dash').css({'color': color})
            }
            var xl = [10,40,30,5,30,100,70,80,20,10,30,40,50]
            var lbl = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
            const ctx = this.$el.find('#result_line_chart')[0].getContext('2d');
            const myChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: lbl,
                    datasets: [{
                        label: dash_name +' page reach',
                        data: xl,
                        fill: false,
                        borderColor: color,
                        tension: 0
                    }],
                },
                options: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: false,
    //                    text: [dash_name+' Page Reach',reach,perc],
    //                    fontSize: 20,
                    },
                    scales: {
                        xAxes: [{
                            ticks:{
                                display:true
                            },
                            gridLines: {
                                display: false,
                                drawBorder: true,
                            }
                        }],
                        yAxes: [{
                           ticks:{
                                display: true
                           },
                            gridLines: {
                                display: true,
                                drawBorder: true,
                            }
                        }]
                    }
                }
            });
        },
        _result_line_chart_visit:function(){
            var dash_name = this.$el.find('.dash_name').html()
            if (dash_name == 'Facebook'){
                   var color = '#3b5998'
                   this.$el.find('.fa_report_dash').css({'color': color})
                   var reach = 10000
                   var perc = '30%'
            }
            else if(dash_name == 'Instagram'){
                   var color = '#c11645'
                   this.$el.find('.fa_report_dash').css({'color': color})
            }
            var xl = [10,40,30,5,30,100,70,80,20,10,30,40,50]
            var lbl = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
            const ctx = this.$el.find('#result_line_chart_visit')[0].getContext('2d');
            const myChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: lbl,
                    datasets: [{
                        label: dash_name +' page reach',
                        data: xl,
                        fill: false,
                        borderColor: color,
                        tension: 0.1
                    }],
                },
                options: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: false,
    //                    text: [dash_name+' Page Reach',reach,perc],
    //                    fontSize: 20,
                    },
                    scales: {
                        xAxes: [{
                            ticks:{
                                display:true
                            },
                            gridLines: {
                                display: false,
                                drawBorder: true,
                            }
                        }],
                        yAxes: [{
                           ticks:{
                                display: true
                           },
                            gridLines: {
                                display: true,
                                drawBorder: false,
                            }
                        }]
                    }
                }
            });
        },
        _donut_chart:function(){
        var dash_name = this.$el.find('.dash_name').html()
            if (dash_name == 'Facebook'){
                   var color = '#3b5998'
                   this.$el.find('.fa_report_dash').css({'color': color})
                   var reach = 10000
                   var perc = '30%'
            }
            else if(dash_name == 'Instagram'){
                   var color = '#c11645'
                   this.$el.find('.fa_report_dash').css({'color': color})
            }
            var xl = [10,40,30,5,30,100,70,80,20,10,30,40,50]
            var lbl = ['Male','Femail']
            const ctx = this.$el.find('#donut_chart')[0].getContext('2d');
            const myChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: [
                        'Male',
                        'Female',

                      ],
                      datasets: [{
                        label: 'My First Dataset',
                        data: [300, 50],
                        backgroundColor: [
                          'rgb(65, 155, 215)',
                          'rgb(240, 95, 105)',
                        ],
                        hoverOffset: 4
                      }]
                      },
                });
        },
        _Audience_chart_bar:function(){
            var dash_name = this.$el.find('.dash_name').html()
            if (dash_name == 'facebook'){
                   var color = '#3b5998'
                   this.$el.find('.fa_report_dash').css({'color': color})
                   var reach = 10000
                   var perc = '30%'
            }
            else if(dash_name == 'instagram'){
                   var color = '#c11645'
                   this.$el.find('.fa_report_dash').css({'color': color})
                   var reach = 10000
                   var perc = '30%'
            }

            var xl = [15,20,30,50,30,20,10]
            var age = ['1-2','2-3','3-4','4-5','6-7','7-8']

            const chart = this.$el.find('#Audience_chart_bar')[0].getContext('2d');
            const myChart = new Chart(chart, {
                type: 'bar',
                data: {
                    labels: age,
                    datasets: [{
                        label: dash_name +' Male Audience',
                        data: xl,
                        fill: false,
                        borderColor: color,
                        backgroundColor: 'rgb(65, 155, 215)',
                        tension: 0.1
                    },
                    {
                        label: dash_name +' Female Audience',
                        data: xl,
                        fill: false,
                        borderColor: color,
                        backgroundColor: 'rgb(240, 95, 105)',
                        tension: 0.1
                    }],
                },
                options: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: false,

                    },
                    scales: {
                        xAxes: [{
                            ticks:{
                                display:true
                            },
                            gridLines: {
                                display: false,
                                drawBorder: false,
                            }
                        }],
                        yAxes: [{
                           ticks:{
                                display: true
                           },
                            gridLines: {
                                display: true,
                                drawBorder: false,
                            }
                        }]
                    }
                }
            });
        },


    });



    core.action_registry.add('dashboard_tag', SMDashboard);
    return SMDashboard;

});
