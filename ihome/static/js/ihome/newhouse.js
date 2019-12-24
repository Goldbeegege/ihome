function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $.ajax({
        url:"/area_info",
        success:function(ret){
            $("#area-id").empty();
            let data = ret.data;
            for(let area_id in data){
                let option = $("<option value='" + data[area_id].id +"'>"+ data[area_id].name+"</option>");
                $(option).appendTo("#area-id");
            }
        }
    })
});