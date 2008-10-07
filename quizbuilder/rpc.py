import logging
# Log a message each time this module get loaded.
logging.info('Loading %s', __name__)
from google.appengine.ext import webapp
from google.appengine.ext import db
from model import *
import views
import simplejson
from .utils import jsonparser as parser


class RPCHandler(webapp.RequestHandler):
  # AJAX Handler
  def __init__(self):
    webapp.RequestHandler.__init__(self)
    self.methods = RPCMethods()

 
  def get(self):
    func = None
   
    action = self.request.get('action')
    if action:
      if action[0] == '_':
        self.error(403) # access denied
        return
      else:
        func = getattr(self.methods, action, None)
   
    if not func:
      self.error(404) # file not found
      return
     
    args = ()
    while True:
      key = 'arg%d' % len(args)
      val = self.request.get(key)
      if val:
        args += (simplejson.loads(val),)
      else:
        break
    result = func(*args)
    self.response.out.write(simplejson.dumps(result))
    


class RPCMethods(webapp.RequestHandler):
  """ Defines AJAX methods.
  NOTE: Do not allow remote callers access to private/protected "_*" methods.
  """

  def ds(self, *args):
    qt = QuizTaker(email = "a@a.com")
    qt.put()
    quiztakers = QuizTaker.all()
    for t in quiztakers:
        if t.filter.get():  # Check if filter exists for this quiz taker
           try:
               print t.filters   #fake
           except AttributeError:
               pass
           f = t.filter.get()
           f.mean = 0
           f.put()
           self.runOperation(t, f)

        else:
            f = QuizTakerFilter(quiz_taker = t)
            f.put() # Create new filter
            f = self.runOperation(t, f)
        #f.put()
    
        
    
  def runOperation(self, t, f):
    print t.filter.get().mean
    print f.quiz_taker.filter.get().mean
    print f.quiz_taker.scores
    print f.quiz_taker.itemscores.get()

            
  
  
        
  def SubmitContentUrl(self, *args):
      save_url = views.RawItemInduction()
      #JSON Serialize save_url
      raw_items = []
      for this_raw_item in save_url.get(args):
          raw_item = {}
          raw_item['pre_content'] = this_raw_item.pre_content
          raw_item['content'] = this_raw_item.content
          raw_item['post_content'] = this_raw_item.post_content
          raw_item['answer_candidates'] = this_raw_item.answer_candidates
          raw_item['index'] = str(this_raw_item.index)
          raw_item['url'] = str(this_raw_item.page.url)
          raw_item['topic'] = str(this_raw_item.page.topic.name)
          raw_items.append(raw_item)
      
      # this parser needs to do character escaping 
      json_response = simplejson.dumps(raw_items) 
      return json_response

    
  def SubmitQuizItem(self, *args):

      new_quiz_item = QuizItem()
      new_quiz_item.slug = [str(args[0]), str(args[1])]
      new_quiz_item.index = str(args[2])
      new_quiz_item.answers = args[3] # And args[2] 
      new_quiz_item.category = str(args[4])       # different datastore? Not currently in model 
      new_quiz_item.proficiency = str(args[5])  # Should be Proficiency
      new_quiz_item.content = str(args[6])
      new_quiz_item.difficulty = 0 # Default?
      #new_quiz_item.put()
      return "saved quiz item" 
