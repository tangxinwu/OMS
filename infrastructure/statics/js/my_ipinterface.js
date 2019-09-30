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

    $(".item").off("onclick").on("click", function () {
       let host = $(this).text();
       let wan_items = $("#wan_zone div");
       let lan_items = $("#lan_zone div");
       $.each(wan_items, function (k,v) {
          if (v.innerText == host){
              v.className = "item_selected";
          }else {
              v.className = "item";
          }

       });
       $.each(lan_items, function (k,v) {
          if (v.innerText == host){
              v.className = "item_selected";
          }else {
              v.className = "item";
          }

       });
       $.get("/ip_interface/?host=" + host, function (result) {
           window.open (result,'_blank','height=500,width=800,toolbar=no,menubar=no,scrollbars=no,resizable=no,location=no,status=no');

       });
    });
});