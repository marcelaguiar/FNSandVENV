$(document).ready(load_from_db);


function load_from_db(){
    $.ajax({
        type: "GET",
        url: "/top_training_partners/",
        dataType: "html", //what you expect the url to return
        success: function(response){
            $("#yee").html(response);
        }
    });
}