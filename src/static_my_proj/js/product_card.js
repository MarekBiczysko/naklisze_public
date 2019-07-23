//<script type="text/javascript" src="{% url 'jscatalog' %}"></script> to translate inside js (use in template)

$(window).on('load', function(){

 //Scrolled body in products card
    var $descriptionItems = $(".product-card-body");
    var shouldBeHeight = 230;
    $.each($descriptionItems, function(index, obj){

        var item = $(this);
        var actualHeight = item[0].scrollHeight;

        if (actualHeight > shouldBeHeight){
            item.css("height", shouldBeHeight);
            item.mCustomScrollbar({
                theme:"minimal-dark"
            });
        }
    });

});