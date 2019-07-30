/*
更新线上的版本
 */

//刷新日志函数
function refresh_log() {
   //自动刷新最近的5个log记录
    $.post("/check_log/", {"action":"check"}, function (result) {
       var all_logs_json = JSON.parse(result);
       $("#task_table").empty();
       $.each(all_logs_json, function (k,v) {

          var row_content = "<td onclick='task_detail(this)'>" + k +"</td>";
          $.each(v,function (k,v) {
             row_content += "<td>" + v + "</td>"
          });
          var new_row = "<tr>"+ row_content + "</tr>";
          $("#task_table").append(new_row);

       });
    });

}

//查看具体任务信息

function task_detail(obj){
    var task_id = obj.innerText;
    $.post("/check_log/", {"action": "detail_check", "task_id":task_id},function (result) {
        var last_result = JSON.parse(result);
        var display_result = last_result["message"];
        if (display_result.indexOf("{") != 0){
            display_result = eval(display_result);
        }
        $("#myModal").modal();
        $("#task-detail").empty();
        $("#task-detail").append(display_result);

    });
}


$(function () {
    //更新按钮
   $("#update").off("onclick").on("click", function () {
        $(".cover").show();
        $("#update_result").empty();
        var application_id = $("#applications").val();
        if (application_id == ""){
            alert("请选择更新选项！");
            $(".cover").hide();
            return false;
        }
        if (confirm("确定要更新吗？")){
            $.post("/version_update/", {"application_id": application_id} ,function (result) {

               $("#update_result").append(result);
               refresh_log();
               $(".cover").hide();
        });

        }else {
            $(".cover").hide();
        }

   }) ;

   // 过滤操作选项
   $("#keywords_content").off("onchange").on("change", function () {

      var keywords_content = $("#keywords_content").val();
      if (keywords_content == ""){
          return false;
      }
      var application_list_objects = $("#applications option");
      $.each(application_list_objects, function (k,v) {
         var this_content = $(this).text();
           if (this_content.indexOf(keywords_content) == -1){
               $(this).hide();
           }else {
               $(this).show();
           }
      });
   });



   //定时刷新更新日志
    setInterval(refresh_log, 3000);

});
