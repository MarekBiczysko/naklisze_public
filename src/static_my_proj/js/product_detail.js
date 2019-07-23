//<script type="text/javascript" src="{% url 'jscatalog' %}"></script> to translate inside js (use in template)

$(window).on('load', function(){

    /* <<< PRODUCT GALLERY*/
    // product detail view gallery
    var prodGallery = $('#prodGallery');
    prodGallery.carousel({interval: 100000});

    // Load big version for first main product image
    var $firstImage = prodGallery.find('.carousel-item.active').find('img');
    $firstImage.fadeOut('slow', function () {
        $firstImage.attr('src', $firstImage.attr('data-full-img'));
        $firstImage.fadeIn('slow');
        });

    // Load big version for next active product image
    prodGallery.on('slide.bs.carousel', function (e) {
      var $nextImage = $('[data-slide-number='+e.to+']').children();
      $nextImage.fadeOut('slow', function () {
      $nextImage.attr('src', $nextImage.attr('data-full-img'));
      $nextImage.fadeIn('slow');
      });
    });

    // handles the product images carousel thumbnails
    $('[id^=carousel-selector-]').click( function(){
      var id_selector = $(this).attr("id");
      var id = id_selector.substr(id_selector.length -1);
      id = parseInt(id);
      $('#prodGallery').carousel(id);
      $('[id^=carousel-selector-]').removeClass('img_selected');
      $(this).addClass('img_selected');
    });

    // when the product images carousel slides, auto update
    prodGallery.on('slid.bs.carousel', function (e) {
      var $activeSlide = $('.carousel-item.active');
      var id = $activeSlide.data('slide-number');
      id = parseInt(id);
      $('[id^=carousel-selector-]').removeClass('img_selected');
      $('[id=carousel-selector-'+id+']').addClass('img_selected');
    });

    // full product images screen image on dimmed bg
    $('.prodImgSmall').click(function(){
    var img_src = $(this).attr("data-full-img");
    $('.prodImgBig').attr("src",img_src);
    $('.navbar').hide();
    $('body>*:not(#overlay):not(#overlayContent)').addClass('blur');
    $("#overlay").show();
    $("#overlayContent").show();
    });

    $(".prodImgBig").click(function(){
    $(".prodImgBig").attr("src", "");
    $('body>*').removeClass('blur');
    $("#overlay").hide();
    $("#overlayContent").hide();
    $('.navbar').show();
    });
    /*PRODUCT GALLERY>>>*/


    // sticked product detail page accordion panel with price
    $('.collapse').on('hide.bs.collapse show.bs.collapse', function (e) {
        console.log($(e.target).hasClass('stickedCard'));
        if ($(e.target).hasClass('stickedCard')) {
            e.preventDefault();
        }
    });

});