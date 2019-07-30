/*
检查端口
 */


$(function () {
   $("#update").off("onclick").on("click", function () {
        $(".cover").show()
        $("#update_result").empty();
        var application_id = $("#applications").val();
        var sub_dir = $("#sub_dir").val();
        if (application_id == ""){
            alert("请选择更新选项！");
            $(".cover").hide();
            return false;
        }
        if (sub_dir == ""){
            alert("请选择更新的子文件夹！");
            $(".cover").hide();
            return false;
        }
        if (confirm("确定要更新吗？")){
            $.post("/h5_update/", {"application_id": application_id, "sub_dir":sub_dir} ,function (result) {

               $("#update_result").append(result);
               $(".cover").hide();
        });

        }else {
            $(".cover").hide();
        }

   }) ;

   $()
});