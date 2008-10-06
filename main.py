
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0


""" Plopquiz Demo




"""





from views import *
from utils import *
from dev import *
import quizbuilder



    
    
def main():
  logging.getLogger().setLevel(logging.DEBUG)
  
  application = webapp.WSGIApplication(
                                       [
                                        ('/demo/?',
                                         PQDemo),
                                        ('/preview/ad_embed/?',
                                         PQDemo),                                         
                                         ('/intro/?',
                                         PQIntro),
                                        ('/rpc/?',
                                         RPCHandler),                                                                                                                     
                                        ('/viewscore/?',
                                         ViewScore),
                                        ('/quiz_complete/?',
                                         QuizComplete),                                         
                                        ('/view_quiz/?',
                                         ViewQuiz), 
                                        ('/view_quiz/close/?',
                                         ViewNone),                                         
                                        ('/quiz/?',
                                         QuizItemTemplate),                                         
                                        ('/?',
                                         PQHome),  
                                        ('/refresh_data/?',
                                         RefreshData),
                                        ('/dump_data/?',
                                         DumpData),                                          
                                        ('/create_scores/?',
                                         CreateScoreStubs),
                                        ('/view_scores/?',
                                         ViewScoreStubs),
                                        ('/set_proficiencies/?',
                                         Set_Proficiencies),
                                        ('/set_difficulties/?',
                                         Set_Difficulties),
                                        ('/quizbuilder/?',
                                         QuizBuilder),
                                         ('/dev/?(.*)/?', 
                                         URIRouter),
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)



if __name__ == "__main__":
  main()
