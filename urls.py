def url_routes(map):
	
	#Hompeage
	map.connect('', controller = 'quiztaker.views:PQHome')
	map.connect('preview/homepage', controller = 'homepage.views:ViewHomepage')
	map.connect('preview', controller = 'homepage.views:ExitPage')

    #Login
	map.connect('login', controller = 'accounts.views:Login')
	map.connect('login/response', controller = 'accounts.views:LoginResponse')
	map.connect('logout', controller = 'accounts.views:Logout')
	
	#Profiles
	map.connect('profile/*username', controller = 'profiles.views:ViewProfile')
	map.connect('edit_profile', controller = 'profiles.views:EditProfile')
	map.connect('register', controller = 'profiles.views:EditProfile')
	
	#Store
	map.connect('preview/proficiency', controller = 'store.views:ChooseProficiency')
	map.connect('sponsor/*user', controller = 'store.views:Sponsorship')
	
	#Preview
	map.connect('preview/profile', controller = 'profiles.views:PreviewViewProfile')
	map.connect('preview/employer/profile', controller = 'profiles.views:ViewEmployerProfile')
	map.connect('preview/employer/profile/browse', controller = 'profiles.views:BrowseProfiles')
	map.connect('preview/employer/load_profile', controller = 'profiles.views:LoadUserProfile')

	#Demo
	map.connect('demo', controller = 'quiztaker.views:PQDemo')
	map.connect('preview/ad_embed', controller = 'quiztaker.views:PQDemo')
	map.connect('st_quiz', controller = 'quiztaker.views:ViewSnaptalentQuiz')
	map.connect('st_quiz/close', controller = 'quiztaker.views:ViewNone')	
	
	# Taking Quizzes
	map.connect('quiz/*quiz', controller = 'quiztaker.views:TakeQuiz')
	map.connect('widget', controller = 'quiztaker.views:Widget')	
	map.connect('quiz_item', controller = 'quiztaker.views:QuizItemTemplate')		
	map.connect('intro', controller = 'quiztaker.views:PQIntro')
	map.connect('quiz_complete', controller = 'quiztaker.views:QuizComplete')
	map.connect('quiz_frame', controller = 'quiztaker.views:QuizFrame')

	map.connect('js/quiz/:quiz_topic', controller = 'widget.handler:QuizJS')
	map.connect('css/quiz', controller = 'widget.handler:QuizCSS')
		

	# Induction & Building Quizzes
	map.connect('quizbuilder', controller = 'quizbuilder.views:QuizBuilder')
	map.connect('quizbuilder/induction', controller = 'quizbuilder.views:InductionInterface')		
	map.connect('quizbuilder/item', controller = 'quizbuilder.views:RawItemTemplate')

	# RPC Handlers
	map.connect('quiztaker/rpc', controller = 'quiztaker.rpc:RPCHandler')
	map.connect('quizbuilder/rpc/post', controller = 'quizbuilder.rpc:RPCPostHandler')	
	map.connect('quizbuilder/rpc', controller = 'quizbuilder.rpc:RPCHandler')		
	map.connect('employer/rpc', controller = 'employer.rpc:RPCHandler')		
	map.connect('accounts/rpc', controller = 'accounts.rpc:RPCHandler')	
	map.connect('profiles/rpc', controller = 'profiles.rpc:RPCHandler')		
	map.connect('dev/rpc', controller = 'dev.rpc:RPCHandler')			
	map.connect('profiles/picture_upload', controller = 'profiles.rpc:PictureUpload')	
	
	
	# Induction & Building Quizzes
	map.connect('dev/admin', controller = 'dev.views:Admin')
	map.connect('dev/filter', controller = 'ranking.views:Filter')
	map.connect('ranking/graph', controller = 'ranking.views:Graph')		
	map.connect('debug', controller = 'dev.views:Debug')
	
			   										
																														 
	#Utils
	map.connect('image/*img', controller = 'profiles.views:Image')
	map.connect('js/base', controller = 'homepage.views:BaseJS')
	map.connect('Redirect', 'redirect/*path', controller = 'accounts.views:Redirect')	
	map.connect('404 error', '*url/:not_found', controller = 'utils.utils:NotFoundPageHandler')
	map.connect('404 error', '*url', controller = 'utils.utils:NotFoundPageHandler')     
