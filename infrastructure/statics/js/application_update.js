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
            row_content += "<td><i class='icon-book' onclick='update_description(this)' style='cursor: pointer'></i></td>"
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
};

//查看对应行的版本更新说明
function update_description(obj){
    let project_name = obj.parentNode.parentNode.childNodes[1].innerText;
    let tags_name = obj.parentNode.parentNode.childNodes[3].innerText;
    if (tags_name == ""){
        swal("出错啦!", "按照分支更新的在更新记录中查看更新内容！", "error");
        return false;
    };
    if (tags_name == "waiting" || project_name == "PROCESSING"){
        swal("出错啦!", "正在更新中，稍后再试！", "error");
        return false;
    };
    $.get("/version_tags_check/?query_type="+ tags_name + "&project_name=" + project_name, function (result) {
       swal({
                title: "更新说明：",
                text: result,
            });
    });
};

$(function () {
    //更新按钮
   $("#update").off("onclick").on("click", function () {
        $("#update_result").empty();
        let application_id = $("#applications").val();
        let application_tags = $("#tags").val();
        if (application_id == ""){
            swal("出错啦!", "请选择更新选项!", "error");
            return false;
        }
		 swal({
			title: "您确定要更新吗？",
			text: "您确定要更新这个项目？",
			type: "warning",
			showCancelButton: true,
			closeOnConfirm: false,
			confirmButtonText: "是的，我要更新",
			confirmButtonColor: "#ec6c62"
			}, function() {
				$.post("/version_update/", {"application_id": application_id,"application_tags":application_tags} ,function (result) {
                        $("#update_result").append(result);
                        refresh_log();
                        swal("操作成功!", "已成功发送更新请求！", "success");
        });
			});


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

   // 刷新所选项目的tags
    $("#applications").off("onchange").on("change", function () {
       let applications_value = $("#applications").val()
       if (applications_value == ""){
          return false;
      };
       $.get("/version_tags_check/?query_type=all_tags&project_name=" + applications_value, function (result) {
          if (result == ""){
            $("#tags").empty();
            $("#tags").append("<option value=''>" + "没有对应的tag，下一步将使用分支直接更新" + "</option>")
          }else {
            let tags_list = result.split("||");
            $("#tags").empty();
            $("#tags").append("<option value=''>" + "不使用tags更新" + "</option>");
            $.each(tags_list, function (k,v) {
               $("#tags").append("<option value='"+ v + "'>" + v + "</option>");
            });
          };
       });
    });



   //定时刷新更新日志
    setInterval(refresh_log, 3000);

});
