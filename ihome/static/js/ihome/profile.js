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
    $(".submit_img").attr("disabled","disabled");
    $("#form-avatar").submit(function(e){
       e.preventDefault();
       if (!$("input[name='avatar']").val()){
           alert("请选择图片");
           return
       }
       $("#form-avatar").ajaxSubmit({
           url:"/upload_avatar",
           type:"post",
           headers:{
               "X-CSRFtoken":getCookie("csrf_token")
           },
           success:function(ret){
               if (ret.msg === 1){
                   $("#user-avatar").attr("src","/media");
                   alert("上传成功");
                   $(".submit_img").attr("disabled","disabled")
               }else{
                   alert(ret.error)
               }
           }
       })
    });
    $("#avatar").change(function () {
        $(".submit_img").removeAttr("disabled");
        var fileRader = new FileReader();
        fileRader.readAsDataURL(this.files[0]);//通过dom对象获取文件
        //文件加载需要时间
        fileRader.onload = function () {
            $(".avatar").attr("src", fileRader.result)
        }
    });

    $("#username-change").click(function(e){
        e.preventDefault();
        let usernameTag= $("#username");
        usernameTag.removeAttr("readonly");
        let that = this;
        if (usernameTag.hasClass("changed")){
            $.ajax({
                url:"/change_info?username=" + usernameTag.val(),
                success:function(ret){
                    if (!ret.error) {
                        usernameTag.attr("readonly", "readonly").removeClass("changed").addClass("unchanged");
                        $(that).html("修改");
                        alert("修改成功！")
                    }else{
                        $(".username-error").show().children("span").html(ret.error)
                    }
                }
            })
        }

    });
    $("#username").change(function(){
       $("#username-change").html("保存");
       $(this).removeClass("unchanged").addClass("changed");
    });

    $.ajax({
        url:"/my_info",
        type:"get",
        success:function(ret){
            if (ret.msg === 1){
                let username = ret.data.username;
                let mobile = ret.data.mobile;
                $("#username").val(username);
                if (mobile){
                    $("#mobile").attr("readonly","readonly").next().attr("disabled","disabled");
                }
            }
        }
    })

    // $(".save").click(function(){
    //     if (!$("#usrname").val() && !$("#mobile").val()){
    //         return;
    //     }else{
    //         $.ajax(
    //         )
    //     }
    // });
});
