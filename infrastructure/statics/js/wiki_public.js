/*
发布wiki的js文件
 */

$(function () {
   $("#check_follow_users").off("onclick").on("click", function () {
      var document_data = $("#document_data").val();
      var user_data = $("#user_data").val();
      $.post("/wiki_public/", {"action": "follow_document", "document_data": document_data, "user_data": user_data}, function (result) {
         alert(result);
      });
   });

});