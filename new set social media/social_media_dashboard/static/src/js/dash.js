//odoo.define('social_media_dashboard.dash', function (require) {
//'use strict';

    $( document ).ready(function() {
       $(".o_cp_bottom").hide();
       $('.tabcontent').css({'display':'none'})
       $('#Overview').css({'display':'block'})
       line()
       audience_chart()
    });
    $(".tablinks ").click(function(event){
       var id = $(event.target).html()
       $('.tabcontent').css({'display':'none'})
       $('#'+id).css({'display':'block'})
    });
    function line(){
        var dash_name = $('.dash_name span').html()
        if (dash_name == 'Facebook'){
               var color = '#3b5998'
               $('.fa_report_dash').css({'color': color})
               var reach = 10000
               var perc = '30%'
        }
        else if(dash_name == 'Instagram'){
               var color = '#c11645'
               $('.fa_report_dash').css({'color': color})
               var reach = 10000
               var perc = '30%'
        }
        var xl = [10,40,30,5,30,90,70,80,20,10,30,40,50]
        var lbl = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

        const ctx = document.getElementById('myChart').getContext('2d');
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
                    display: true,
                    text: [dash_name+' Page Reach',reach,perc],
                    fontSize: 20,
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

    }
    function audience_chart(){
        var dash_name = $('.dash_name span').html()
        if (dash_name == 'facebook'){
               var color = '#3b5998'
               $('.fa_report_dash').css({'color': color})
               var reach = 10000
               var perc = '30%'
        }
        else if(dash_name == 'instagram'){
               var color = '#c11645'
               $('.fa_report_dash').css({'color': color})
               var reach = 10000
               var perc = '30%'
        }

        var xl = [10,40,30,5,30,90,70,80,20,10,30,40,50]
        var lbl = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

        const chart = document.getElementById('Audience_chart').getContext('2d');
        const myChart = new Chart(chart, {
            type: 'bar',
            data: {
                labels: lbl,
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
        })

    }


//});
