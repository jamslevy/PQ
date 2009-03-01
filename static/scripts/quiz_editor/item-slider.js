

// when the DOM is ready...
function item_sliderInit(wrong_answers) {
    
    var $panels = $('.quizbuilder_wrapper .quiz_items > div');

    var $container = $('.quizbuilder_wrapper .quiz_items');

    // if false, we'll float all the panels left and fix the width 
    // of the container
    var horizontal = true;

    // float the panels left if we're going horizontal
    if (horizontal) {
        $panels.css({
            'float' : 'left',
            'position' : 'relative' // IE fix to ensure overflow is hidden
        });


    }

    // collect the scroll object, at the same time apply the hidden overflow
    // to remove the default scrollbars that will appear
    var $scroll = $('.quizbuilder_wrapper .scroller').css('overflow', 'hidden');

    
    // handle nav selection
    function selectNav() {
        $(this)
            .parents('ul:first')
                .find('a')
                    .removeClass('selected')
                .end()
            .end()
            .removeClass('queue')
            .addClass('selected')
            //.nextAll().slice(0,2).addClass('queue');  add queue class to the next few in the queue
            

    }

    $('.quizbuilder_wrapper > .item_navigation').find('a').click(selectNav);

    // go find the navigation link that has this target and select the nav
    
    // use: $(container).trigger( 'next' );
    
function trigger(item) {
var el = $('.item_navigation').find('a[href="#' + item.id + '"]');
selectNav.call(el);
if ( $(item).data('triggered') == true) return false;
$(item).data('triggered', true);
/*
 * 
 * Load Answers
 * 
 */

$(item).trigger("initiate"); 
loadAnswers($(item));
return;
 
  }

                     

    var scrollOptions = {
        target: $scroll, // the element that has the overflow

        // can be a selector which will be relative to the target
        items: $panels,

        navigation: '.item_navigation a',
        
        cycle: 'false',
        lazy: 'true', // for dynamic content

        // selectors are NOT relative to document, i.e. make sure they're unique
     //   prev: 'img.left', 
     //   next: 'input[@name="submit_item"]',

        // allow the scroll effect to run both directions
        axis: 'x',

        onAfter: trigger, // our final callback
        
        force: true,

        offset: -50,//offset,

        // duration of the sliding effect
        duration: 500,

        // easing - can be used with the easing plugin: 
        // http://gsgd.co.uk/sandbox/jquery/easing/
        //easing: 'swing'
    };

    // apply serialScroll to the slider - we chose this plugin because it 
    // supports// the indexed next and previous scroll along with hooking 
    // in to our navigation.
    $('.quizbuilder_wrapper').serialScroll(scrollOptions);

    // now apply localScroll to hook any other arbitrary links to trigger 
    // the effect
    $.localScroll(scrollOptions);

    // finally, if the URL has a hash, move the slider in to position, 
    // setting the duration to 1 because I don't want it to scroll in the
    // very first page load.  We don't always need this, but it ensures
    // the positioning is absolutely spot on when the pages loads.
  //  scrollOptions.duration = 1;
  //  $.localScroll.hash(scrollOptions);


 
}