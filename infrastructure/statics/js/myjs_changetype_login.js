/*
控制更改样机登陆界面的js
 */

$(function () {
    $("#login").on("off").on("click", function () {
        var email = $("#email").val();
        var password = $("#inputPassword").val();
        var reg = /\w+\@\w+\.\w+/;
        var result = reg.test(email);
        if (result == false){
            alert("邮箱格式不正确！");
            return false;
        };
        $.post("/change_login/", {"email":email, "password":password}, function (result) {
            var real_result = JSON.parse(result);
            if (real_result["login_flag"] == "successful"){
                alert("欢迎回来" + email);
                window.location.href = "/change_type/";
            } else {
                alert("用户名或密码错误！");
            }
        });
    });
});