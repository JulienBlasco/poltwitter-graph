$(document).ready(function(){
    $('input').not('[type="submit"]').addClass("form-control")
    $('input[type="submit"]').addClass("btn btn-default").css({"text-shadow": "none", "font-weight": "bold"})
})