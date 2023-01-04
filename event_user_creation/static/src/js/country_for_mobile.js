
$(document).ready(function(){
    var country_id = $('.country_id_new')
    var sel_country = $('.sel_country')
    for(i=0; i<=country_id.length; i++){
        var id = $(country_id[i]).attr('id')
        var sel_country_id = $(sel_country[i]).attr('id')
        var c_id = $('#'+id).val()
        console.log(c_id,id,sel_country_id)
        $("#"+sel_country_id+" option[value='" + c_id + "']").attr("selected","selected");
    }
});
