function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(document).ready(function(){
    $.ajax({
        url:"/area_info",
        success:function(ret){
            let data = ret.data;
            // for(let area_id in data){
            //     let option = $("<option value='" + data[area_id].id +"'>"+ data[area_id].name+"</option>");
            //     $(option).appendTo("#area-id");
            // }
            let temp = template("area_info",{area_li:data});
            $("#area-id").html(temp)
        }
    });
    $("#form-house-info").submit(function(e){
        e.preventDefault();
        let data = {};
        let fl = [];
        $(this).serializeArray().map(function(item){
            if (item.name === "facility"){
                fl.push(item.value)
            }
            data[item.name] = item.value
        });
        data["facility"] = fl;
        $.ajax({
            url:"/public_new_house",
            type:"post",
            data:data,
            headers:{
                "X-CSRFtoken":getCookie("csrf_token")
            },
            success:function(ret){
                if (!ret.error){
                    $("#form-house-info").hide();
                    $("#form-house-image").show();
                    $("#house-id").val(ret.data.house_id);
                }else{
                    alert(ret.error)
                }
            }
        })
    });
    $("#form-house-image").submit(function(e){
        e.preventDefault();
        if (data.length === 0 ){
            alert("请选择图片");
            return false
        }
        $(".popup_con").fadeIn();
        let formData = new FormData();
        for(let img in data){
            formData.append("file"+img,data[img])
        }
        formData.append("house_id",$("#house-id").val());
        $.ajax({
            url:"/upload_house_image",
            type:"post",
            data:formData,
            headers:{
                "X-CSRFtoken":getCookie("csrf_token")
            },
            success:function(ret){
                if(!ret.error){
                    $(".popup_con").fadeOut();
                    $("#tip").fadeIn();
                    setTimeout(function(){
                        $("#tip").fadeOut();
                        location.href = "/myhouse";
                    },1000);

                }else{
                    alert(ret.error)
                }
            },
            processData:false,
            contentType:false,
        });
    });

    let data = [];
    $("#house-image").change(function () {
        let fileObj = this.files;
        for(let i=0; fileObj.length >i;i++){
            let fileRader = new FileReader();
            let file =fileObj[i];
            if (data.length >= 8){
                alert("图片最多只能上传6张");
                return
            }
            data.push(file);
            console.log(file);
            fileRader.readAsDataURL(file);//通过dom对象获取文件
            //文件加载需要时间
            fileRader.onload = function () {
                let divTag = $("<div style='width:25%;height:90px;display:inline-block;position:relative'><i class='fa fa-minus-circle delete' style='color:red;position:absolute;right:0;top:0'></i></div>");
                let imageTag = $("<img src='' class='img-responsive img-thumbnail' style='height:100%;width:100%'>");
                divTag.append(imageTag);
                imageTag.attr("src",fileRader.result);
                $(divTag).appendTo("#house_image_group");
            };
        }
    });
    $("#house_image_group").on("click",".delete",function(){
        $(this).parent().remove();
    })
});