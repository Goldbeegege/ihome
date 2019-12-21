// js读取cookie的方法
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 保存图片验证码编号
var imageCodeId = "";

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode() {
    // 形成图片验证码的后端地址， 设置到页面中，让浏览请求验证码图片
    // 1. 生成图片验证码编号
    imageCodeId = generateUUID();
    // 是指图片url
    var url = "/image_code/" + imageCodeId;
    $(".image-code img").attr("src", url);
}

$(document).ready(function() {
    generateImageCode();
    $("#username").blur(function(){
        valide_username($("#username").val())
    });
    $("#imagecode").blur(function () {
        valide_imagecode($("#imagecode").val())
    });
    $("#password").blur(function () {
        valide_password($("#password").val())
    });
    $("#password2").blur(function () {
        valide_password2($("#password2").val())
    });

    $("#username").focus(function(){
        $(this).parent().removeClass("has-error");
        $("#username-err").hide();
    });
    $("#imagecode").focus(function(){
        $(this).parent().removeClass("has-error");
        $("#imagecode-err").hide();
    });
    $("#password").focus(function(){
        $(this).parent().removeClass("has-error");
        $("#password-err").hide();
    });
    $("#password2").focus(function(){
        $(this).parent().removeClass("has-error");
        $("#password2-err").hide();
    });


    // 为表单的提交补充自定义的函数行为 （提交事件e）
    $(".form-register").submit(function(e){
        // 阻止浏览器对于表单的默认自动提交行为
        e.preventDefault();

        var mobile = $("#mobile").val();
        var passwd = $("#password").val();
        var passwd2 = $("#password2").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        // if (!phoneCode) {
        //     $("#phone-code-err span").html("请填写短信验证码！");
        //     $("#phone-code-err").show();
        //     return;
        // }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (passwd != passwd2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }

        // 调用ajax向后端发送注册请求
        var req_data = {
            mobile: mobile,
            // sms_code: phoneCode,
            password: passwd,
            password2: passwd2,
        };
        var req_json = JSON.stringify(req_data);
        $.ajax({
            url: "/api/v1.0/users",
            type: "post",
            data: req_json,
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            }, // 请求头，将csrf_token值放到请求中，方便后端csrf进行验证
            success: function (resp) {
                if (resp.errno == "0") {
                    // 注册成功，跳转到主页
                    location.href = "/index.html";
                } else {
                    alert(resp.errmsg);
                }
            }
        })

    });
});

let showErrorMsg = function(data){
    if (data["msg"] == "all"){
        $("#username-err").show().children("span").html(data["error"]);
        return;
    }
    let value = data["msg"];
    let tag_id = "#" + value + "-err";
    $(tag_id).show().children("span").html(data["error"]);
    $("#imagecode").val("");
    generateImageCode()
}



let valide_username = function (username){
    if (username.length == 0){
        error_info("username","请创建用户名")
        return false;
    }
    let reg = /[0-9a-zA-Z_]{6,12}/;
    let ret = reg.test(username);
    if(!ret){
        error_info("username","用户名由数字字母或下划线组成，长度为6-12个字符");
        return false;
    }
    return true
}

let valide_imagecode = function(imagecode){
    if (imagecode.length == 0){
        error_info("imagecode", "请输入验证码");
        return false;
    }
    return true;
}

let valide_password = function(password){
    if (password.length == 0){
        error_info("password","请输入密码")
        return false;        
    }
    let reg = /.{8,16}/;
    
    let ret = reg.test($("#password").val());
    if (!ret){
        error_info("password", "密码长度为8-16个字符");
        return false;
    };
    return true;
}

let valide_password2 = function(password2){
    if (password2.length == 0){
        error_info("password2", "请确认密码");
        return false;
    }
    if (password2 != $("#password").val()){
        error_info("password2","两次密码输入不一致");
        return false;
    }
    return true;
}

let error_info = function(tag,msg){
    $("#" + tag).parent().addClass("has-error");
    let error_tag = "#" + tag +"-err";
    $(error_tag).show().children("span").html(msg);
}

var handlerPopup = function (captchaObj) {
        // 成功的回调
        captchaObj.onSuccess(function () {
            var validate = captchaObj.getValidate();
            console.log($("#username").val())
            $.ajax({
                url: "/pc-geetest/ajax_validate", // 进行二次验证
                type: "post",
                dataType: "json",
                data: {
                    geetest_challenge: validate.geetest_challenge,
                    geetest_validate: validate.geetest_validate,
                    geetest_seccode: validate.geetest_seccode,
                    username:$("#username").val(),
                    password:$("#password").val(),
                    password2: $("#password2").val(),
                    imagecode:$("#imagecode").val(),
                    imageId:imageCodeId
                },
                headers: {
                    "X-CSRFToken": getCookie("csrf_token")
                },
                success: function (data) {
                    if (data["error"]) {
                        showErrorMsg(data)
                    } else {
                        location.href = "/login"
                    }
                }
            });
        });
        $("#popup-submit").click(function () {
            captchaObj.show();
        });
        // 将验证码加到id为popup-captcha的元素里
        captchaObj.appendTo("#popup-captcha");
        // 更多接口参考：http://www.geetest.com/install/sections/idx-client-sdk.html
    };
// 验证开始需要向网站主后台获取id，challenge，success（是否启用failback）
$.ajax({
    url: "/pc-geetest/register?t=" + (new Date()).getTime(), // 加随机数防止缓存
    type: "get",
    dataType: "json",
    success: function (data) {
        // 使用initGeetest接口
        // 参数1：配置参数
        // 参数2：回调，回调的第一个参数验证码对象，之后可以使用它做appendTo之类的事件
        initGeetest({
            gt: data.gt,
            challenge: data.challenge,
            product: "popup", // 产品形式，包括：float，embed，popup。注意只对PC版验证码有效
            offline: !data.success // 表示用户后台检测极验服务器是否宕机，一般不需要关注
            // 更多配置参数请参见：http://www.geetest.com/install/sections/idx-client-sdk.html#config
        }, handlerPopup);
    }
});