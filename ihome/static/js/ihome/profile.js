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
    $("#form-avatar").submit(function(e){
       e.preventDefault();
       if (!$("input[name='avatar']").val()){
           alert("请选择图片");
           return
       }
       $("#form-avatar").ajaxSubmit({
           url:"/change_info",
           type:"post",
           headers:{
               "X-CSRFtoken":getCookie("csrf_token")
           },
           success:function(ret){
               if (ret.msg === 1){
                   $("#user-avatar").attr("src","/media/"+ret.data.file_md5);
                   alert("上传成功");
                   $(".submit_img").attr("disabled","disabled")
               }else{
                   alert("请选择图片")
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

    $(".save").click(function(){
        if (!$("#usrname").val() && !$("#mobile").val()){
            return;
        }else{
            $.ajax(
            )
        }
    });
});
