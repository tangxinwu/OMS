//同步数据库界面
let request_url = "/sync_db/"

$(function () {

    //同步按钮
    $("#sync_db").off("onclick").on("click", function () {
        let src_server = $("#src_db_server").val();
        let src_db = $("#src_db").val();
        let src_table = $("#src_table").val();
        let des_server = $("#des_db_server").val();
        let des_db = $("#des_db").val();
        let des_table = $("#des_table").val();
        // 只允许同步表
        if (src_table == ""){
           swal("出错啦!", "请选择同步的数据库表!", "error");
           return false;
        }
        if (des_server == "" || des_db == ""){
            swal("出错啦!", "请选择目标同步的数据库表!", "error");
            return false;
        }
        let sync_data = {
            "action": "sync",
            "src_server": src_server,
            "src_db": src_db,
            "src_table": src_table,
            "des_server": des_server,
            "des_db": des_db,
            "des_table": des_table
        };
       $.post(request_url, sync_data, function (result) {
          alert(result);
       });
    });

    //导出按钮
    $("#export").off("onclick").on("click", function () {
       let src_server = $("#src_db_server").val();
       let src_db = $("#src_db").val();
       let src_table = $("#src_table").val();
       let notice_info = "";
       let options = "";
       if (src_server == "") {
         swal("出错啦!", "请选择导出的数据库服务器!", "error");
         return false;
       }
       if (src_db == "") {
         swal("出错啦!", "请选择导出的数据库!", "error");
         return false;
       }
       if (src_table == ""){
           notice_info = "您确定要导出数据库" + src_db + "?";
       } else {
           notice_info = "您确定要导出数据库" + src_db + "下的" + src_table + "表吗?"
       }

       let all_options = $("input[name=options]");
       $.each(all_options, function (k,v) {
          if (v.checked == true){
                options += v.id;
          }else {
              console.log("False");
          }
       });
       let export_data = {
           "action": "export",
           "src_server": src_server,
           "src_db": src_db,
           "src_table": src_table,
           "options" : options
       };
         swal({
            title: "您确定？",
            text: notice_info,
            type: "warning",
            showCancelButton: true,
            closeOnConfirm: true,
            confirmButtonText: "是的，我要开始导出",
            confirmButtonColor: "#ec6c62"
            }, function() {
            $(".cover").show();
            $.post(request_url, export_data , function (result) {
                    $(".cover").hide();
                    window.open(result);
                });
                return false;

        });



    });

    //下拉源服务器(src_server)菜单触发
    $("#src_db_server").off("onchange").on("change", function () {
        $("#src_db").empty();
        let src_server_ip = $(this).val();
        if (src_server_ip != "") {
            $.post(request_url, {"action": "db_check", "server_ip": src_server_ip}, function (result) {
                let real_result = JSON.parse(result);

               $.each(real_result, function (k,v) {
                  $.each(v, function (k1, v1) {
                        $("#src_db").append("<option>" + v1 + "</option>");
                  }) ;
               });
            });
        } else {
            alert("不能为空！")
        };
    });

    //下拉目标服务器(des_server)菜单触发
    $("#des_db_server").off("onchange").on("change", function () {
        $("#des_db").empty();
        let des_server_ip = $(this).val();
        if (des_server_ip != "") {
            $.post(request_url, {"action": "db_check", "server_ip": des_server_ip}, function (result) {
              let real_result = JSON.parse(result);

               $.each(real_result, function (k,v) {
                  $.each(v, function (k1, v1) {
                        $("#des_db").append("<option>" + v1 + "</option>");
                  }) ;
               });
            });
        } else {
            alert("不能为空！")
        };
    });

    //下拉选择源数据库的时候的刷新表格事件
    $("#src_db").off("onchange").on("change", function () {
        $("#src_table").empty();
        let server_ip = $("#src_db_server").val();
        let database = $("#src_db").val();
        $.post(request_url, {"action": "table_check", "server_ip": server_ip, "database": database}, function (result) {
            let real_result = JSON.parse(result);
            $("#src_table").append("<option value=''>请选择检查或者同步的表格...</option>")
            $.each(real_result, function (k,v) {
               $.each(v, function (k1, v1) {
                   $("#src_table").append("<option>" + v1 + "</option>")
               }) ;
            });
        });
    });

    //下拉目标数据库的时候的刷新表格事件
    $("#des_db").off("onchange").on("change", function () {
        $("#des_table").empty();
        let server_ip = $("#des_db_server").val();
        let database = $("#des_db").val();
        $.post(request_url, {"action": "table_check", "server_ip": server_ip, "database": database}, function (result) {
            let real_result = JSON.parse(result);
            $("#des_table").append("<option value=''>请选择检查或者同步的表格...</option>")
            $.each(real_result, function (k,v) {
               $.each(v, function (k1, v1) {
                   $("#des_table").append("<option>" + v1 + "</option>")
               }) ;
            });
        });
    });

    //比较按钮事件
    $("#compare").off("onclick").on("click", function () {
       //检测对比前期条件
        let src_server = $("#src_db_server").val();
        let src_db = $("#src_db").val();
        let src_table = $("#src_table").val();
        let des_server = $("#des_db_server").val();
        let des_db = $("#des_db").val();
        let des_table = $("#des_table").val();
        let compare_data = {
            "action": "compare",
            "src_server": src_server,
            "src_db": src_db,
            "src_table": src_table,
            "des_server": des_server,
            "des_db": des_db,
            "des_table": des_table
        };
        if (src_server == "" || des_server == ""){
            swal("出错啦!", "请保证对比的数据库服务器都已经选择!", "error");
            return false;
        };
        if (src_db == "" || des_db == ""){
            swal("出错啦!", "请保证对比的数据库都已经选择!", "error");
            return false;
        };
        if (src_table == "" && des_table == ""){
		 swal({
			title: "您确定？",
			text: "您确定要查看对比"+ src_db + "和" + des_db + "?",
			type: "warning",
			showCancelButton: true,
			closeOnConfirm: true,
			confirmButtonText: "是的，我要开始对比",
			confirmButtonColor: "#ec6c62"
			}, function() {
		    $(".cover").show();
            $.post(request_url, compare_data , function (result) {
                    window.open("/display_report/");
                    $(".cover").hide();
                });
                return false;
        });



        } else if (src_table == "" || des_table == ""){
          swal("出错啦!", "对比的表格不能为空!", "error");
          return false;
        } else {
            $(".cover").show();
            $.post(request_url, compare_data , function (result) {
                window.open("/display_report/");
                $(".cover").hide();
            });
        };
    });
});