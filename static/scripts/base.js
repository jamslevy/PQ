jQuery.fn.extend({
	preserveDefaultText: function(defaultValue, replaceValue)
	{
		$(this).focus(function()
		{
			if(typeof(replaceValue) == 'undefined')
				replaceValue = '';  
			if($(this).val() == defaultValue)
				$(this).val(replaceValue);
		});

		$(this).blur(function(){  
			if(typeof(replaceValue) == 'undefined')
				replaceValue = '';  
			if($(this).val() == replaceValue)
				$(this).val(defaultValue);
		});
		return this;
	}
});
 
$(document).ready(function()
{
	var viewWidth = $('#viewport').width();
	var viewHeight = $('#viewport').height();
	$('#viewport .layer.near').css({width: (viewWidth * 1.4), height: (viewHeight*1.3)});
	$('#viewport .layer.mid').css({width: (viewWidth * 1.15), height: (viewHeight*1.05)});
	$('#viewport .layer.far').css({width: (viewWidth * 1.04), height: (viewHeight*1.01)});
	jQuery('#viewport').jparallax({});
	$('#viewport').css({overflow: "hidden"});
	
	

	}).focus(function()
	{
		// prevents crawling ants
		$(this).blur();
	}).mousedown(function()
	{
			$(this).addClass('down');
	}).mouseup(function()
	{
		$(this).removeClass('down');
	});

 
 