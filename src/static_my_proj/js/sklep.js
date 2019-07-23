//<script type="text/javascript" src="{% url 'jscatalog' %}"></script> to translate inside js (use in template)

$(window).on('load', function(){

    // random bottom carousel
    var carouselBottom = $('#carouselBottom');
    carouselBottom.carousel({pause: "false"});
    var $bottom_car_item = $('.carousel-item.car_bottom');
    var $numberofSlides = $bottom_car_item.length;
    var $currentSlideNr = Math.floor((Math.random() * $numberofSlides));
    var $currentSlide = $bottom_car_item.eq($currentSlideNr);
    var $currentSlideImg = $currentSlide.children();

    $currentSlideImg.attr("src", $currentSlideImg.attr('data-src'));
    $currentSlideImg.removeAttr("data-src");
    $currentSlide.addClass('active');

    carouselBottom.on('slid.bs.carousel', function() {
    var $currentSlideImg = $('.active').find('img');
    $currentSlideImg.attr("src", $currentSlideImg.attr('data-src'));
    $currentSlideImg.removeAttr("data-src");
    });

    // navbar smaller height on scroll
    $(window).on('scroll', function () {

        var navbar = $('.navbar');
        var navbarBrand = $('#navbar-brand');

        if (($(window).scrollTop() >= 5) && !($("#dropdowned").is(":visible"))) { // use any value lower than the navbar height, [20] is an example

            navbar.css({
                'opacity': 0.6,
                'padding-top': '5px',
                'padding-bottom': '5px',
                'transition': '0.5s all'
            });
            navbarBrand.css({
                'top': '10%',
                'transition': '1s all'
            });

        } else {

            navbar.css({
                'opacity': 1,
                'padding-top': '35px',
                'padding-bottom': '35px'
            });
            navbarBrand.css({
                'top': '40%',
                'transition': '1s all'
            });
        }

        $('.nav-link, .navbar').on('click', function() {
        navbar.css({
                'opacity': 1
            });
        });
    });

    // smooth scroll from breadcumb to target elem
    $('.breadcrumb').on('click', function() {
    $('html, body').animate({scrollTop: $(this.hash).offset().top - 250}, 500);
    return false;
    });


    // enable popovers
    $("[data-toggle=popover]").popover();

    // Capslock warning in password forms fields
    var $passwordCapsWarn = $('#password-caps-warning');
    $('#id_password,#id_password2').on('keyup keydown', function (e) {
        if (e.originalEvent.getModifierState('CapsLock')) {
            $passwordCapsWarn.removeClass('d-none');
        } else {
            $passwordCapsWarn.addClass('d-none');
        }
    })

});
