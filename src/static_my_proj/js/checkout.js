//<script type="text/javascript" src="{% url 'jscatalog' %}"></script> to translate inside js (use in template)

$(window).on('load', function(){

    // auto submit shipping type POST on radio button click
    $('.shipping-type-radio').change(function(){
          // find the submit button and click it on the previous action
          //$('#shipping-type-submit').click()
        $('#shippingTypeForm').submit();
          });
});