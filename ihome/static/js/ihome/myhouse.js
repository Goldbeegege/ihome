$(document).ready(function(){
    $.ajax({
        url:"/my_house",
        success:function(ret){
            if (ret.error){
                $(".auth-warn").show();
                $("#houses-list").hide();
            }else{
                $(".auth-warn").hide();
                $(".new-house").show();
                let temp = template("house-info",{houses:ret.data});
                $("#houses-list").append(temp)
            }
        }
    });
    
});