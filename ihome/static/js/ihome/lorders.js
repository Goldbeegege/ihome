//模态框居中的控制
function centerModals() {
    $('.modal').each(function (i) {   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top - 30);  //修正原先已经有的30个像素
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function dynamic_html(tag,status){
    $(tag).find(".order-text>ul>li").eq(-1).children().html(status).css({"color":"blue"});
    $(".completed-orders-list").append(tag);
    $(tag).find(".order-operate").remove();
    if ($(".orders-list").children().length === 0) {
        $(".orders-list").remove()
    }
}

$(document).ready(function () {
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);
    $(".orders-list").on("click", ".order-accept",function () {
        let orderId = $(this).parents("li").attr("order-id");
        $(".modal-accept").attr("order-id", orderId).click(function() {
            $("#accept-modal").modal("hide");
            $.ajax({
                url: "/status",
                type:"put",
                data:{
                    order_id:$(this).attr("order-id")
                },
                headers:{
                    "X-CSRFtoken":getCookie("csrf_token")
                },
                success:function(ret){
                    if(!ret.error){
                        let liTag = $("li[order-id='" + ret.data.order_id + "']");
                        dynamic_html(liTag,"已接单")
                    }
                }
            });
        })
    });
    $(".orders-list").on("click", ".order-reject", function () {
        let orderId = $(this).parents("li").attr("order-id");
        $(".modal-reject").attr("order-id", orderId).click(function () {
            let rejectInput = $("#reject-reason");
            let rejectReson = $(rejectInput).val();
            if (!rejectReson) {
                $(rejectInput).parent().addClass("has-error");
                $("#error-msg").html("请填写理由").css({"color": "red"});
            } else {
                $("#reject-modal").modal("hide");
                $(rejectInput).val("");
                $("#error-msg").html("");
                $(rejectInput).parent().removeClass("has-error");
                $.ajax({
                    url: "/status",
                    type: "post",
                    data: {
                        order_id: $(this).attr("order-id"),
                        comment: rejectReson,
                    },
                    headers: {
                        "X-CSRFtoken": getCookie("csrf_token")
                    },
                    success: function (ret) {
                        if (!ret.error) {
                            $("#tip").show();
                            setTimeout(function () {
                                $("#tip").fadeOut();
                            }, 1000);
                            let liTag = $("li[order-id='" + ret.data.order_id + "']");
                            dynamic_html(liTag,"已拒单");
                            if (rejectReson.length > 10) {
                                $(liTag).find(".order-text>ul").append("<li>拒单原因：<a href='javascript:;' order-id='" + ret.data.order_id + "'>查看详情</a></li>");
                                return;
                            }
                            $(liTag).find(".order-text>ul").append("<li>拒单原因：" + rejectReson + "</li>");
                        } else {
                            alert(ret.error)
                        }
                    }
                })
            }

        });

    });
    $.ajax({
        url: "/order_info?type=1",
        success: function (ret) {
            if (ret.data) {
                let temp = template("order-li", {orders: ret.data});
                let orderLi = $(".orders-list");
                $(orderLi).append(temp);
                let completed_temp = template("completed-order-li", {orders: ret.data});
                $(".completed-orders-list").append(completed_temp);
                if($(orderLi).children().length === 0){
                    $(orderLi).remove();
                }
            }
        }
    });
});