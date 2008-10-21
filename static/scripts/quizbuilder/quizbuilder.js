


jQuery(function($) {
	
	
// Setup RPC methods
var server = {};
var item_count = 0;

InstallFunction(server, 'RetrieveProficiencies');

InstallFunction(server, 'GetRawItemsForProficiency');





wrong_answers = [];
answer_in_array = [];




$('.proficiency_name').preserveDefaultText('proficiency');
$('.url_name').preserveDefaultText('url');


server.RetrieveProficiencies("all", AfterRetrieveProficiencies);  // Create list of proficiencies 


function AfterRetrieveProficiencies(response){  

var proficiencies = parseJSON(response);

 $.each(proficiencies, function(p, proficiency){
 
 // Add proficiency to list -- todo: nested list organized by proficiencies
 	
$('div#proficiencies').append('<input type="checkbox" id="' + p + '" name="proficiency" value="' + proficiency.name + '" unchecked ><span>' + proficiency.name + '</span><br/>')

.find('input[@name="proficiency"]').click(function(){
$('input[@name="proficiency"]').setValue($(this).attr("value"));    });

proficiency_sum = p + 1;
return proficiency_sum;
});

$('input[@name="proficiency"]').setValue(proficiencies[0].name);  // select first option as default


$('#submit_proficiency').click(function () {

        for (j = 0; j < proficiency_sum; j++) {
if (eval('document.select_proficiency.proficiency[' + j + '].checked') == true) {
    var proficiency = eval('document.select_proficiency.proficiency[' + j + '].value'); }}

    server.GetRawItemsForProficiency(proficiency, AfterGetRawItemsForProficiency);
    
    
$('form#select_proficiency').hide();
$('div#loading_items').show();
    
});


}



function AfterGetRawItemsForProficiency(response){ BuildQuizEditor(response); }


 

});

