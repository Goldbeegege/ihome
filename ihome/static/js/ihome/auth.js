function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    $.ajax({
        url:"/init_auth",
        success:function(ret){
            if (!ret.error){
                if (ret.data){
                    let realNameTag = $("<p id='real-name' class='form-control-static' style='display: inline-block;margin-left:10px;'></p>");
                    let idCardTag = $("<p id='id-card' class='form-control-static' style='display: inline-block;margin-left:10px;'></p>");
                    realNameTag.html(ret.data.real_name);
                    idCardTag.html(ret.data.id_card);
                    $("#real-name").remove();
                    $("#id-card").remove();
                    $("label[for='id-card']").append(idCardTag);
                    $("label[for='real-name']").append(realNameTag);
                    $("#save").remove();
                    $("#error-msg").remove();
                }
            }
        }
    });

    $("#real-name").focus(function(){
        $("#real-name-err").hide();
    });
    $("#id-card").focus(function(){
        $("#id-card-err").hide();
    });
   $("#save").click(function(e){
        e.preventDefault();
        $("#auth-form").ajaxSubmit({
            url:"/auth",
            type:"post",
            headers:{
                       "X-CSRFtoken":getCookie("csrf_token")
                   },
            success:function(ret){
                if (ret.error){
                    if(ret.msg === "all"){
                        $("#real-name-err").show().children("span").html(ret.error);
                        $("#id-card-err").show().children("span").html(ret.error);
                    }
                    $("#"+ret.msg+"-err").show().children("span").html(ret.error);
                }
            }
        });
   })
});

