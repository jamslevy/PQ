
		$(function () {


$('#quiz_subjects').change(function(){

            $(this).data('subject', $(this).find('option').filter(':selected').text())

        });



						$('div#submit_form div#submit').click(function(){  SubmitSettingsEdit();   });
			
			$('div#submit_form div#cancel').click(function(){
			CancelSettingsEdit();
		});
		


// Take a Quiz link
$('a#preview_quiz').click(function(){ 
	$.getScript("/js/quiz/?autostart=True");
});

		
		});


 function SubmitSettingsEdit() {
// get the different pieces of data, and submit them

// TODO: We can use jQuery.serialize() for fast form serialization
$('div.main').hide();$('div.loading').show();

	$.ajax({
		type: "POST", 
		url: '/employer/rpc/post',
		datatype: "json",
		data:
			{
					action: "settings",
					sponsor: this_sponsor, // defined in sponsor_settings.html
					sponsorship_message: $('textarea#sponsor_message').attr('value'),
					quiz_subject: $('#quiz_subjects').data('subject')
			},
		error: function() { AjaxError(); },
		success: function(response) { onEditSuccess(response); }
});			


	                      
}
	


function AjaxError() {

$('div.loading').hide(); $('div.main').show(); 
		$('.form_error').show()
		  .find('a').click(
		  function(){ $('a#contact_dialog').click(); } );
return false;
}

 








	function onEditSuccess(response){

	if (eval(response) != "OK") { // error message.
		return AjaxError(); }
	
	window.location=profile_path;
}
function CancelSettingsEdit(){
$('div.main').hide();$('div.loading').show();	
window.location=profile_path;
}
