function logout() {
    $.get("/logout", function(data){
        if (1 == data.msg) {
            location.href = "/";
        }
    })
}

$.ajax({
    url:"/my_info",
    success:function(data){
        if(data.error){
            location.href="/"
        }else{
            $("#username").html(data.data.username).attr("user_id",data.data.user_id);
            if (data.data.mobile){
                $("#usermobile").html(data.data.mobile)
            }
        }
    }
});
