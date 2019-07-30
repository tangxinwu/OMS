//登陆界面

$(function () {
   $("#login_submit").off("onclick").on("click", function () {
       var login_name = $("#login_name").val();
       var login_password = $("#login_password").val();
       if (login_password.replace(" ", "") == "" || login_name.replace(" ", "") == ""){
           alert("用户名和密码不能为空！");
           return false;
       }
       $.post("/login/",{"login_name":login_name, "login_password":login_password}, function (result) {
          if (result == "succ"){
              window.location.href = "/ip_interface/"
          }else {
              alert("登陆失败！")
          }
       });
   }) ;
});