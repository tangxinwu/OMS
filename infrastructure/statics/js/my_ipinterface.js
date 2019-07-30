$(function () {
    $("#search_button").off("onclick").on("click", function () {
       var ip_objects = $(".main div");
       var search_content = $("#search_content").val();
       $.each(ip_objects, function () {
           var this_content = $(this).text();
           if (this_content.indexOf(search_content) == -1){
               $(this).hide();
           }else {
               $(this).show();
           }
       });
    });

});