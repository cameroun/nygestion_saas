
/*************************
      Predefined Variables
*************************/ 
var IMPACTO = {};

 (function($){
  "use strict";

/*************************
      Predefined Variables
*************************/ 
 
  var $window = $(window),
  $document = $(document),
  $body = $('body'),
  $bar = $('.bar'),
  $header = $('header');


 /*************************
        Check if function exists
*************************/ 
     $.fn.exists = function () {
        return this.length > 0;
    };


 /*************************
       counter
*************************/  
 IMPACTO.counters = function () {
     var $counter = $('.counter');
          if ($counter.exists()) {
              $counter.each(function () {
                  var $elem = $(this);
                       $elem.appear(function () {                       
                          $elem.find('.timer').countTo();
                       });   
              });
          }
  };


/*************************
       owl-carousel 
*************************/
 IMPACTO.carousel = function () {
    $(".owl-carousel").each(function () {
        var $this = $(this),
            $items = ($this.data('items')) ? $this.data('items') : 1,
            $loop = ($this.attr('data-loop')) ? $this.data('loop') : true,
            $navdots = ($this.data('nav-dots')) ? $this.data('nav-dots') : false,
            $navarrow = ($this.data('nav-arrow')) ? $this.data('nav-arrow') : false,
            $autoplay = ($this.attr('data-autoplay')) ? $this.data('autoplay') : true,
            $space = ($this.attr('data-space')) ? $this.data('space') : 30;		    
           
            $(this).owlCarousel({
				        loop: false,
                mouseDrag: false,
                touchDrag: false,
                pullDrag: false,
                items: $items,
                responsive: {
                  0:{items: $this.data('xx-items') ? $this.data('xx-items') : 1},
                  499:{items: $this.data('xs-items') ? $this.data('xs-items') : 1},
                  768:{items: $this.data('sm-items') ? $this.data('sm-items') : 2},
                  980:{items: $this.data('md-items') ? $this.data('md-items') : 3},
                  1200:{items: $items}
                },

                dots: $navdots,
                margin:$space,
                nav: $navarrow,
                navText:["<i class='fa fa-angle-left fa-2x'></i>","<i class='fa fa-angle-right fa-2x'></i>"],
                autoplay: false,
                autoplayHoverPause: true   
           });           
    });
}

/*************************
       Magnific Popup
************************/
IMPACTO.mediaPopups = function () {
    if ($(".popup-img").exists()) {
          $('.popup-img').magnificPopup({
              type: 'image',
              tLoading: 'Loading image #%curr%...',
              mainClass: 'mfp-img-mobile',
              gallery: {
                  enabled: true,
                  navigateByImgClick: true,
                  preload: [0,1] // Will preload 0 - before current, and 1 after the current image
              },
              image: {
                  tError: '<a href="%url%">The image #%curr%</a> could not be loaded.',
                  titleSrc: function(item) {
                      return item.el.attr('title') + '<small>by Marsel Van Oosten</small>';
                  }
             }
         }); 
      }
      if ($(".popup-youtube, .popup-vimeo, .popup-gmaps").exists()) {
           $('.popup-youtube, .popup-vimeo, .popup-gmaps').magnificPopup({
                disableOn: 700,
                type: 'iframe',
                mainClass: 'mfp-fade',
                removalDelay: 160,
                preloader: false,
                fixedContentPos: false
          });
      }
  }

/*************************
       Progressbar
*************************/  
IMPACTO.progressBar = function () {
   var $progressBar = $('.progress-bar');
    if ($progressBar.exists()) {
        $progressBar.each(function (i, elem) {
            var $elem = $(this),
                percent = $elem.attr('data-percent') || "100",
                delay = $elem.attr('data-delay') || "100",
                type = $elem.attr('data-type') || "%";
            if (!$elem.hasClass('progress-animated')) {
                $elem.css({
                    'width': '0%'
                });
            }
        var progressBarRun = function () {
            $elem.animate({
                'width': percent + '%'
            }, 'easeInOutCirc').addClass('progress-animated');
             $elem.delay(delay).append('<span class="progress-type animated fadeIn">' + type + '</span><span class="progress-number animated fadeIn">' + percent + '</span>');
        };
        $(elem).appear(function () {
                setTimeout(function () {
                    progressBarRun();
                }, delay);
            });
        });
      }
};

 

/*************************
         Masonry
*************************/
IMPACTO.masonry = function () {
    var $masonry = $('.masonry-main .masonry'),
      $itemElement = '.masonry-main .masonry-item';
      if ($masonry.exists()) {
        $masonry.isotope({
          resizable: true,
          itemSelector: $itemElement,
          masonry: {
            gutterWidth: 10
          }
        });
     }  
}


/*************************
         Isotope
*************************/
IMPACTO.Isotope = function () {
       var $isotope = $(".isotope"),
          $itemElement = '.grid-item',
          $filters = $('.isotope-filters');      
        if ($isotope.exists()) {
            $isotope.isotope({
            resizable: true,
            itemSelector: $itemElement,
              masonry: {
                gutterWidth: 10
              }
            });     
       $filters.on( 'click', 'button', function() {
         var $val = $(this).attr('data-filter');
             $isotope.isotope({ filter: $val });       
             $filters.find('.active').removeClass('active');
             $(this).addClass('active');
      });     
    }

}

/*************************
  Search Box
*************************/
IMPACTO.searchbox = function (e) {
    $('a[href="#search-but"]').on("click", function(event) {
      event.preventDefault();
      $("#search-box").addClass("open");
      $('#search-box > form > input.search-input').focus();
    });
  $("#search-box, #search-box button.close").on("click keyup", function(event) {
    if (
      event.target == this ||
      event.target.className == "close" ||
      event.keyCode == 27
    ) {
      $(this).removeClass("open");
    }
  });
  $("#search-box form").submit(function(event) {
      $("#search-box").removeClass("open");
   // return false;
  });
}

/****************************************************
     IMPACTO Window load and functions
****************************************************/
  //Window load functions
    $window.load(function () {
      IMPACTO.masonry(),
      IMPACTO.Isotope(),	
      IMPACTO.carousel(),	 
		  IMPACTO.progressBar();
    });

 //Document ready functions
    $document.ready(function () {         
        IMPACTO.counters(), 
        IMPACTO.mediaPopups(),
        IMPACTO.searchbox();
    });
})(jQuery);
