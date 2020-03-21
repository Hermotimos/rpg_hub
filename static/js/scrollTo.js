jQuery(function($)
{
    // reset scroll on page loading
    $.scrollTo(0);
    // when click on element with class .scrollup scroll to 'body' element (=top)
    $('.scrollup').click(function() { $.scrollTo($('body'), 1000); });
}
);

// Show scrollup button when scrolled down > 300px
$(window).scroll(function()
{
    if($(this).scrollTop()>300) $('.scrollup').fadeIn();
    else $('.scrollup').fadeOut();
}
);