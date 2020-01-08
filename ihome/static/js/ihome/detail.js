function hrefBack() {
    history.go(-1);
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}
$(document).ready(function(){
    $.ajax({
        url:"/get_house_image?house_id="+decodeQuery().id,
        success:function(ret){
            if(!ret.error){
                let temp = template("silde-li",{urls:ret.data});
                $(".swiper-wrapper").append(temp);
                let mySwiper = new Swiper ('.swiper-container', {
                    loop: true,
                    autoplay: 2000,
                    autoplayDisableOnInteraction: false,
                    pagination: '.swiper-pagination',
                    paginationType: 'fraction'
                });
            }
        }
    });
    $.ajax({
        url:"/public_house_info?house_id="+decodeQuery().id,
        success:function(ret){
            if (!ret.error){
                if (ret.msg === 1){
                    $(".book-house").hide();
                }else{
                    $(".book-house").show();
                }
                let priceTag = $("<div class='house-price'>￥<span>"+ret.data.price+"</span>/晚</div>");
                $(".swiper-container").append(priceTag);
                let temp = template("basic-info",{data:ret.data});
                $(".house-info").before(temp)
            }
        }
    });
    $.ajax({
        url:"/comments?house_id="+decodeQuery().id,
        success:function(ret){
            if(ret.data){
                let temp = template("comment-list",{orders:ret.data});
                $(".house-comment-list").append(temp)
            }
        }
    });
    $(".book-house").attr("href","/booking?house_id="+decodeQuery().id)
});