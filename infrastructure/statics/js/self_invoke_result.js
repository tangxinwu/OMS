/*
自助申请流程结果界面的js
 */

$(function () {
    $("#go_search").off("onclick").on("click", function () {
        let search_token = $("#token_content").val();
        // 限制为空的情况
        if (search_token == ""){
            alert("搜索结果不能为空!");
            return false;
        }
        $.post("/self_invoke_result/", {"search_token": search_token}, function (result) {
            //返回了没有找到的结果
            if (result == "FAILD"){
               alert("没有找到相关的审批内容 请查证后再重试!");
               return false;
           };
            let real_result = JSON.parse(result);
            console.log(real_result);
            //检测状态如果是已拒绝和已处理 不显示审批和拒绝按钮
            if (real_result["isdeal"] == 0) {
                $("#agreed_button").show();
                $("#deny_button").show();
            }
            if (real_result["isdeal"] == 1) {
                $("#agreed_button").hide();
                $("#deny_button").hide();
            }
            if (real_result["isdeal"] == 2) {
                $("#agreed_button").hide();
                $("#deny_button").hide();
            }
            // 写入标签
            $("#myModalLabel").empty();
            $("#myModalLabel").append(real_result["InVokedApplicationId"] + "||" + real_result["InvokedToken"]);
            //写入表格内容
            $("#Auditing_content").empty();
            $("#Auditing_content").append(
                "<td>" + real_result["InVokedApplication"] + "</td>" +
                "<td>" + real_result["AuditingUserName"] + "</td>" +
                "<td>" + real_result["deal_status"] + "</td>"
            );
            $("#myModal").modal();
        });
    });

    //审批同意按钮
    $("#agreed_button").off("onclick").on("click", function () {
            let application_id_token = $("#myModalLabel").text();
            $.post("/self_invoke_result/", {"application_id_token": application_id_token, "auditing_action": "agreed"}, function (result) {
                alert(result);
            });
    });

    //审批拒绝按钮
    $("#deny_button").off("onclick").on("click", function () {
            let application_id_token = $("#myModalLabel").text();
            $.post("/self_invoke_result/", {"application_id_token": application_id_token, "auditing_action": "deny"}, function (result) {
                alert(result);
            });
    });
});