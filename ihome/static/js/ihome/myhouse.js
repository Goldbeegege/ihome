$(document).ready(function(){
    $.ajax({
        url:"/my_house",
        success:function(ret){
            if (ret.error){
                $(".auth-warn").show();
            }else{
                $(".auth-warn").hide();
            }
        }
    });
    
});