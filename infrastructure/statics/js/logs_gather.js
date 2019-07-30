/*
检查日志
 */


$(function () {
   $("#log_file_list h4").off("onclick").on("click", function () {
       alert("test");
       alert($(this).text());
   });


   $("#check_logs").off("onclick").on("click", function () {
        $(".cover").show()
        $("#checklogs_result").empty();
        $("#log_file_list").empty();
        var logs_id = $("#logs").val();
        var lines = $("#log_lines").val();
        var filter_keywords = $("#filter_keywords").val();
        if (logs_id == "" || lines == ""){
            alert("请确保log类型和返回的行数正确！");
            $(".cover").hide();
            return false;
        }
        if (confirm("确定要检查日志吗？")){
            //显示标题
            $("#myModalLabel").empty();
            $("#myModalLabel").append(logs_id + "||" + lines + "||" + filter_keywords);
            $("#myModal").modal();
            $.post("/logs_gather/", {"logs_id": logs_id, "lines": lines} ,function (result) {
                $.each(result.split("<br>"), function (k,v) {
                    $("#log_file_list").append("<h4 onclick='var obj=this;check_log_file(obj)' style='cursor: pointer;'>" + v + "</h4><br>");
                });

               $(".cover").hide();
        });

        }else {
            $(".cover").hide();
        }

   }) ;




});

/*
发送包括logfiles参数的完整post
这个函数讲写入文件内容
*/

function check_log_file(obj) {
    var label = $("#myModalLabel").text();
    var logfile = $(obj).text();
    var logs_id = label.split("||")[0];
    var lines = label.split("||")[1];
    var filter_words = label.split("||")[2]
    $("#checklogs_result").empty();
    $("#myModal").modal("hide");
    $.post("/logs_gather/", {"logs_id":logs_id, "lines":lines, "logfile":logfile, "filter_words":filter_words}, function (result) {
        $("#checklogs_result").append(result);


    });
}