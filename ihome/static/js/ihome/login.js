function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#username").focus(function(){
        $("#username-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
    });
})

$("#btn-submit").click(function () {
    console.log("ok")
    let username = $("#username").val();
    let password = $("#password").val();
    if (!username) {
        $("#username-err span").html("请填写用户名");
        $("#username-err").show();
        return;
    }
    if (!password) {
        $("#password-err span").html("请填写密码!");
        $("#password-err").show();
        return;
    };
    $.ajax({
        url: "/session",
        type: "post",
        data:JSON.stringify({
            username:username,
            password:password,
        }),
        contentType: "application/json",
        // dataType:"json",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        success: function (data) {
            if (data["msg"]== "0"){
                $("#username-err").show().children("span").html(data["error"]);
                $("#password-err").show().children("span").html(data["error"]);
            }else if(data["msg"] == "all"){
                $("#password-err").hide().children("span").html("")
                $("#username-err").show().children("span").html(data["error"]);
            }else{
                location.href="/"
            }
        }
    })
})