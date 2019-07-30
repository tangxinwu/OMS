/*
快捷入口js
 */

$(function () {

    $(".col-sm-2 .btn-large").off("onclick").on("click", function(){
        var host = $(this).attr("name");
        $.post("/shortcut/", {"host": host}, function(result){
            var vm_status = result.split("power")[1];
            alert(host + "电源状态为:" + vm_status );
            if (vm_status == "off"){
                if (confirm(host + "电源已经关闭，是否要开启电源？")){
                    $.post("/shortcut/", {"host": host, action: "poweron"}, function(result){
                        alert(result);
                    });
                }else{
                    return false;
                }
            }
            if (confirm("是否下载连接文件（rdp文件）？")){
                window.location.href="/static/RDP_files/" + host + ".rdp"
            }
        });

    });
});


