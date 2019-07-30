/*
转换配置文件的js文件
 */

$(function () {
   $("#transfor").off("onclick").on("click", function () {
      var before_config = $("#before_config").val();
      $.post("/config_transfor/", {"data": before_config}, function (result) {
         $("#after_config").empty();
         $("#after_config").val(result);
      });
   });

});