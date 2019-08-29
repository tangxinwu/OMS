/*
自助申请流程的js
 */

$(function () {
    $("#start_invoke").off("onclick").on("click", function () {
       var application_id = $("#selected_appplication").val();
       var auditing_id = $("#auditing_id").val();
		 swal({
			title: "您确定要更新吗？",
			text: "您确定要更新这个项目？",
			type: "warning",
			showCancelButton: true,
			closeOnConfirm: false,
			confirmButtonText: "是的，我要更新",
			confirmButtonColor: "#ec6c62"
			}, function() {
                   $.post("/self_invoke/", {"application_id": application_id, "action": "web_check", "auditing_id": auditing_id}, function (result) {
                        if (result == "非法传值"){
                        	swal("OMG", result + " 请检查更新的项目是否选中!", "error");
						} else {
                        	swal("操作成功!", result, "success");
						};

                   });
			});
    });
});