/*
自助申请流程的js
 */

$(function () {
    $("#start_invoke").off("onclick").on("click", function () {
       var application_id = $("#selected_appplication").val();
       var auditing_id = $("#auditing_id").val();
       if (confirm("确定要发送更新申请吗?")){
           $.post("/self_invoke/", {"application_id": application_id, "action": "web_check", "auditing_id": auditing_id}, function (result) {
              alert(result);
           });
       }

    });
});