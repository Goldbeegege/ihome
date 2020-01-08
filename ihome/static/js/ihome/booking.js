function hrefBack() {
    history.go(-1);
}

let days;
let max_day;
let min_day;
let amount;
let price;

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function showErrorMsg(s=1200,func=undefined) {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },s);
        if(func !== undefined){
            func()
        }
    });
}

$(document).ready(function(){
    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    $(".input-daterange").on("changeDate", function(){
        var startDate = $("#start-date").val();
        var endDate = $("#end-date").val();

        if (startDate && endDate && startDate > endDate) {
            showErrorMsg();
        } else {
            var sd = new Date(startDate);
            var ed = new Date(endDate);
            days = (ed - sd)/(1000*3600*24) + 1;
            var price = $(".house-text>p>span").html();
            var amount = days * parseFloat(price);
            $(".order-amount>span").html(amount.toFixed(2) + "(共"+ days +"晚)");
        }
    });
    $.ajax({
       url:"/book?house_id="+decodeQuery().house_id,
       success:function(ret){
           if(!ret.error){
               let temp = template("house-info",{data:ret.data});
               $(".house-info").append(temp);
               max_day = ret.data.max_days;
               min_day = ret.data.min_days;
               price = ret.data.price;
           }
       }
    });

    $(".submit-btn").click(function(){
        if(days===undefined){
            $(".popup p").html("日期有误，请重新选择！");
            showErrorMsg();
        }
        else if(days<min_day){
            $(".popup p").html("最少入住"+min_day+"晚");
            showErrorMsg();
        }else if(days>max_day){
            $(".popup p").html("最多入住"+max_day+"晚");
            showErrorMsg();
        }else{
            let data = {
                start_date:$("#start-date").val(),
                end_date:$("#end-date").val(),
                amount:days*100*price
            };
            $.ajax({
                url:"/book?house_id="+decodeQuery().house_id,
                data:data,
                type:"post",
                headers:{
                  "X-CSRFtoken":getCookie("csrf_token")
                },
                success:function(ret){
                    if(!ret.error){
                        $(".popup p").html("预定成功！").css({"color":"red","fontSize":"16px","fontWeight":"bold"});
                        showErrorMsg(2000,hrefFunc)
                    }else{
                        $(".popup p").html(ret.error).css({"color":"red","fontSize":"16px","fontWeight":"bold"});
                        showErrorMsg(2000)
                    }
                }
            });
        }

    })
});

function hrefFunc(){
    location.href = "/orders"
}
