/*go task 操作的js
 */

// 检查config 内容
function task_check(obj) {
       var all_td_objs = $(obj).children();
       var ip = all_td_objs[0].innerText.split("||")[1];
       var path = all_td_objs[1].innerText;
       $("#myModal_select_config").modal();
       // $("#config_content").empty();
       $("#myModalLabel_select_config").empty();
       $("#myModalLabel_select_config").append(ip + "||" + path);
       // 生成选择文件下拉菜单
       $("#select_config_file").empty();
       var config_list = [
                          "amqp.json",
                          "config.json",
                          "task.json",
                          "redis.json"
                         ];
       for (var i in config_list){
           $("#select_config_file").append("<option id='"+ config_list[i] + "'>" + config_list[i] + "</option>");

       };
       //生成选择文件下拉菜单结束


};

$(function () {
    //刷新页面的同时刷新gotask状态
    $.post("/go-task/", {"action": "check_all_status"}, function(result){
       console.log(result);
    })


    //修改config内容
    $("#modify_config").off("onclick").on("click", function () {
       var config_content = $("#config_content").val();
       var ip = $("#myModalLabel").text().split("||")[0];
       var path = $("#myModalLabel").text().split("||")[1];
       var config_name = $("#myModalLabel").text().split("||")[2];

       if (confirm("确定要修改配置文件" + config_name + "在" + ip + "上吗？")){

           $(".cover").show(); // 遮罩层开启
           $.post("/go-task/", {"action":"modify",
                                "config_content": config_content,
                                "ip":ip,
                                "path":path,
                                "config_name": config_name}, function (result) {
              alert(result);
              $("#myModal").modal("hide");
              $(".cover").hide(); // 遮罩层结束
              // 刷新界面
              window.location.href = "/go-task/";
           });

       }

    });

    //重启go-task进程
    $("#restart_task").off("onclick").on("click", function () {
       var ip = $("#myModalLabel").text().split("||")[0];
       var path = $("#myModalLabel").text().split("||")[1];
       $(".cover").show(); // 遮罩层开启
       $.post("/go-task/", {"action":"restart","ip":ip, "path":path}, function (result) {

           alert(result);

           $("#myModal").modal("hide");
          $(".cover").hide(); // 遮罩层开启
          // 刷新界面
          window.location.href = "/go-task/";
       });
    });


    //停止go-task进程
    $("#stop_task").off("onclick").on("click", function () {
       var ip = $("#myModalLabel").text().split("||")[0];
       var path = $("#myModalLabel").text().split("||")[1];
       $(".cover").show(); // 遮罩层开启
       $.post("/go-task/", {"action":"stop","ip":ip, "path":path}, function (result) {
          $(".cover").show(); // 遮罩层结束
          $("#myModal").modal("hide");
          alert(result);

          // 刷新界面
          window.location.href = "/go-task/";
       });
    });

    //选择完文件名后，跳转显示xxx.json界面
    $("#select_config_next").off("onclick").on("click", function () {

       var ip = $("#myModalLabel_select_config").text().split("||")[0];
       var path = $("#myModalLabel_select_config").text().split("||")[1];
       var config_name = $("#select_config_file").val();
       if (config_name == ""){
           alert("文件名不能为空,请重新选择！");
           return false;
       };
       $("#myModalLabel").empty();
       $("#myModalLabel").append(ip + "||" + path + "||" + config_name);
       $("#myModal_select_config").modal("hide");


       $(".cover").show(); // 获取文件遮罩层开启
       $.post("/go-task/", {"action": "check", "ip": ip, "path": path, "config_name": config_name},function (result) {
            var real_result = JSON.parse(result);
            $("#config_content").empty();
            $(".cover").hide();  // 关闭获取文件遮罩层结束
            $("#myModal").modal();
            $("#config_content").append(real_result["config_content"]);
       });
    });

    //在textarea中禁止tab选择元素 而输入tab到文本区域
    $("textarea").on(
        'keydown',
        function(e) {
            if (e.keyCode == 9) {
                e.preventDefault();
                var indent = '    ';
                var start = this.selectionStart;
                var end = this.selectionEnd;
                var selected = window.getSelection().toString();
                selected = indent + selected.replace(/\n/g, '\n' + indent);
                this.value = this.value.substring(0, start) + selected
                        + this.value.substring(end);
                this.setSelectionRange(start + indent.length, start
                        + selected.length);
            }
        })
});

