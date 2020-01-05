$(document).ready(function(){
    $.ajax({
        url:"/my_house",
        success:function(ret){
            if (ret.error){
                if(ret.msg === 302){
                    location.href="/login?url="
                }
                $(".auth-warn").show();
                $("#houses-list").hide();
            }else{
                $(".auth-warn").hide();
                $(".new-house").show();
                let house_temp = template("house-info",{houses:ret.data.houses});
                $("#houses-list").append(house_temp);
                if(!ret.data.pages){
                    $("nav").hide();
                    return;
                }
                let paginator = $(".pagination");
                $(paginator).attr("current_page",ret.data.page_info.current_page);
                let page_temp = template("page-num",{data:ret.data});
                $(paginator).append(page_temp);
                $("nav ul").children("li").each(function(k,v){
                    let pageNum = $(v).children("span").html();
                    if (parseInt(pageNum) === ret.data.page_info.current_page){
                        $(v).addClass("active")
                    }else{
                        $(v).removeClass("active")
                    }
                })
            }
        }
    });

    $(".pagination").on("click","li",function(){
        let page = $(this).children("span").html();
        reg = /\d+/;
        let current_page = $(this).parent().attr("current_page");
        if (reg.test(page)){
            if(page === current_page){
                return
            }
            $(this).parent().attr("current_page",page)
        }else{
            let tool = $(this).children("span").attr("aria-label");
            if(tool==="Previous"){
                if (current_page === $(this).attr("start_page")){
                    return;
                }
                $(this).parent().attr("current_page",parseInt(current_page)-1)
            }else if(tool==="Next"){
                if($(this).attr("endPage") === current_page){
                    return;
                }
                $(this).parent().attr("current_page",parseInt(current_page)+1)

            }
        }
        $.ajax({
            url:"/my_house?page="+$(this).parent().attr("current_page"),
            success:function(ret){
                if (!ret.error){
                    let house_temp = template("house-info",{houses:ret.data.houses});
                    $("#houses-list").empty().append(house_temp);
                    let paginator = $(".pagination");
                    $(paginator).attr("current_page",ret.data.page_info.current_page);
                    let page_temp = template("page-num",{data:ret.data});
                    $(paginator).empty().append(page_temp);
                    $("nav ul").children("li").each(function(k,v){
                        let pageNum = $(v).children("span").html();
                        if (parseInt(pageNum) === ret.data.page_info.current_page){
                            $(v).addClass("active")
                        }else{
                            $(v).removeClass("active")
                        }
                    })
                }else if(ret.msg===302){
                    location.href="/login"
                }

            }
        })

    })
});