//登陆界面
//为了使界面更好看引入的 sweetalert

//回车直接登录
function on_return() {
   if(window.event.keyCode == 13){
        $("#login_submit").click();
   }
};

$(function () {
   $("#login_submit").off("onclick").on("click", function () {
       var login_name = $("#login_name").val();
       var login_password = $("#login_password").val();
       if (login_password.replace(" ", "") == "" || login_name.replace(" ", "") == ""){
           swal("出错啦!", "用户名和密码不能为空!", "error");
           return false;
       }
       $.post("/login/",{"login_name":login_name, "login_password":login_password}, function (result) {
          if (result == "succ"){
              window.location.href = "/ip_interface/"
          }else {
              swal("出错啦!", "登录失败,确认用户名和密码是否正确!", "error");
          }
       });
   }) ;



});