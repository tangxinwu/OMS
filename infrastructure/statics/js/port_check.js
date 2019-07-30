/*
检查端口
 */

$(function () {

   $("#ip_query").off("onclick").on("click", function () {
        var server_name = $("#servers").val();
        if (server_name == ""){
            alert("请选择正确的服务器名字!");
            return false;
        }
        $("#port_display").empty();
        //隐藏保存server_name的
        $("#port_title").empty();
        $.get("/port_check?server_name=" + server_name,function (result) {
            $("#port_title").append(server_name);
           $.each(result.split(","), function (k,v) {
              $("#port_display").append("<div class='serviceCssCommon' onclick='var obj=this;service_oprations(obj)'>"+ v + "</div>");
           });
        });
   }) ;

   $("#restart_service").off("onclick").on("click", function () {
      var service_info = $("#myModalLabel").text();
      $.post("/port_check/", {"server_name":service_info.split("||")[0], "port":service_info.split("||")[1], "action" : "restart"}, function (result) {
         alert(result);
      });
      $("#myModal").modal("hide");
   });

   $("#shutdown_service").off("onclick").on("click", function () {
       var service_info = $("#myModalLabel").text();
      $.post("/port_check/", {"server_name":service_info.split("||")[0], "port":service_info.split("||")[1], "action" : "stop"}, function (result) {
         alert(result);
      });
       $("#myModal").modal("hide");
   });
});


//操作服务的函数

function service_oprations(obj) {
    $("#myModalLabel").empty();
    var port_title = $("#port_title").text();
    $("#myModalLabel").append(port_title + "||" + $(obj).text());
    $("#myModal").modal();
}

