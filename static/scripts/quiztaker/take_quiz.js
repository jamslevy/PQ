
// Server object that will contain the callable methods
var server = {};
var item_count = 0;

// Insert 'Add' as the name of a callable method
InstallFunction(server, 'AddScore', 'quiztaker');
InstallFunction(server, 'Init', 'quiztaker');
InstallFunction(server, 'Register', 'quiztaker');

function SubmitScore(ans, key, vendor) {
	server.AddScore(ans, key, vendor);
}

function doInit() {
        server.Init();
}

function onAddSuccess(response)
{

$.event.trigger('quizclosing');



return;
}


InstallFunction(server, 'NewUser');


function Register(f) {
	server.Register(f.name.value, f.email.value, f.occupation.value, f.work_status.value, f.webpage.value, f.location.value, onAddSuccess);
return;


}


function redirectHome()
{
window.parent.parent.location="http://www.plopquiz.com"
}
