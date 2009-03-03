import logging
from utils import webapp
from google.appengine.ext import db
import string, re
from google.appengine.api import urlfetch
import urllib
from utils import simplejson
from utils.utils import ROOT_PATH
from utils.gql_encoder import GqlEncoder, encode
from .model.quiz import QuizItem, RawQuizItem,  ContentPage
from .model.proficiency import ProficiencyTopic, Proficiency
import views
from induction import RawItemInduction
from dev.methods import dump_data


class RPCMethods(webapp.RequestHandler):
  """ Defines AJAX methods.
  NOTE: Do not allow reload(sys); sys.setdefaultencoding('utf-8')
remote callers access to private/protected "_*" methods.
  """


######## MODEL METHODS ##########  


  def add_proficiency(self, *args):
	save_p = Proficiency(name = args[0])
	save_p.put()
  	return self.dump_data(["proficiencies"]) 


  def add_topic(self, *args):
  	this_proficiency = Proficiency.get(args[1])
	save_topic = ProficiencyTopic(name = args[0], proficiency = this_proficiency)
	save_topic.put()
  	return self.dump_data(["proficiency_topics"])  
  	



######## INDUCTION METHODS ##########  
        
  def SubmitContentUrl(self, *args):
      induce_url = RawItemInduction()
      #JSON Serialize save_url
      # Induction:
      # 1. Perform semantic analysis
      # 2. Retrieve answer candidates
      # 3. Attempt to create raw quiz items.
      return encode(induce_url.get(args))




######## QUIZBUILDER METHODS ##########  

  def RetrieveTopics(self, *args):   # todo: should be nested list of proficiencies and topics.
      return_topics = []
      topics = ProficiencyTopic.all()
      return encode(topics.fetch(9))

  def RetrieveProficiencies(self, *args):   # todo: should be nested list of proficiencies and topics.
      return_proficiencies = []
      #proficiencies = Proficiency.all()
      proficiencies = Proficiency.gql("WHERE name IN :1", ["Smart Grid", "Energy Efficiency", "Recovery.Gov", "Cars 2.0"]).fetch(1000)  # remove after refactoring quiztaker
      return encode([proficiency.name for proficiency in proficiencies]) # temporary offset


  def GetRawItemsForTopic(self, *args):  
      raw_quiz_items = []
      this_topic = ProficiencyTopic.gql("WHERE name = :1 ORDER BY date DESC", args[0])
      #these_items = RawQuizItem().gql("WHERE topic = :1", this_topic.get())
      try: return encode(this_topic.get().pages.get().raw_items.fetch(10))  # get 10 at a time...todo: lazy rpc-loader.
      except: return simplejson.dumps([])

  def GetRawItemsForProficiency(self, *args):  
      this_proficiency = Proficiency.get_by_key_name(args[0]) # try get_or_insert if Proficiency is key
      prof_pages = this_proficiency.pages.fetch(10)
      raw_items = []
      for p in prof_pages:
          these_items = RawQuizItem.gql("WHERE page = :1 AND moderated = False", p ) # only get unmoderated items
          items = these_items.fetch(1000)
          raw_items += items
      try: return encode(raw_items)  # get 10 at a time...todo: lazy rpc-loader.
      except: return simplejson.dumps([])

  def GetTopicsForProficiency(self, *args):  
      topics = []
      this_proficiency = Proficiency.gql("WHERE name = :1 ORDER BY date DESC", args[0]) # try get_or_insert if Proficiency is key
      topics = ProficiencyTopic.gql("WHERE proficiency = :1 ORDER BY date DESC", this_proficiency.get().key())
      try: return encode(topics.fetch(10))  # get 10 at a time...todo: lazy rpc-loader.
      except: return simplejson.dumps([])
      


  def SetItemModStatus(self, *args):   # set moderation status for raw item
      this_item = db.get(args[0])
      if args[1] == "false": this_item.moderated = False
      if args[1] == "true": this_item.moderated = True
      this_item.put()
      return encode(this_item)


  def SubmitQuizItem(self, *args):
		new_quiz_item = QuizItem()
		new_quiz_item.index = string.lower(args[0])
		lc_answers = [string.lower(answer) for answer in args[1]]
		new_quiz_item.answers = lc_answers
		this_proficiency = Proficiency.gql("WHERE name = :1", args[5])
		this_topic = ProficiencyTopic.get_or_insert(key_name=args[2], name=args[2], proficiency=this_proficiency.get())
		this_topic.put()
		new_quiz_item.topic = this_topic.key()
		new_quiz_item.proficiency = this_topic.proficiency.key()
		# And args[2] 
		# new_quiz_item.proficiency = str(args[5])  # Should be Proficiency   - needs to be calculated. should be proficiency key. 
		new_quiz_item.content =  args[3].replace('title="Click to edit..."', '')
		new_quiz_item.content =  new_quiz_item.content.replace('^f"', '<div class=\"focus\">')    # add focus div. 
		new_quiz_item.content =  new_quiz_item.content.replace('f$"', '</div>')
		new_quiz_item.content =  new_quiz_item.content.replace(' style="opacity: 1;"', '')
		blank_span = re.compile('<span id="blank">.*</span>')  #delete whatever is in span.blank!
		new_quiz_item.content =  blank_span.sub('<span style=\"opacity: 1;\" id=\"blank\"></span>', new_quiz_item.content)
		new_quiz_item.content =  new_quiz_item.content.replace('</div><div class="content">', '')
		new_quiz_item.content =  new_quiz_item.content.replace('</div><div class="post_content">', '')
		new_quiz_item.content =  new_quiz_item.content.replace('<div class="pre_content">', '')
		new_quiz_item.content =  new_quiz_item.content.replace('<div class="content">', '')
		new_quiz_item.content =  new_quiz_item.content.replace('\n', ' ')
		new_quiz_item.content =  new_quiz_item.content.rstrip('</div>')

		new_quiz_item.difficulty = 0 # Default?
		new_quiz_item.content_url = args[4]
		new_quiz_item.theme = new_quiz_item.get_theme(args[4])
		new_quiz_item.put()
		return str(new_quiz_item.key())
      
  def NewQuizItem(self, *args): # Just for ubiquity, for now.
      		save = []
      		new_quiz_item = QuizItem()
      		new_quiz_item.content =  args[0]
      		# lowering everything right now....TODO: Case convention! 
      		new_quiz_item.index = string.lower(args[1])
      		all_answers = [string.lower(answer) for answer in eval(args[2])]
      		all_answers.append(new_quiz_item.index)
      		new_quiz_item.answers = all_answers
      		# TODO: Can a new quiz subject be made here? Yay or nay?
      		this_proficiency = Proficiency.get_by_key_name(args[3])
      		# topic key_names usually are proficiency_topic -- are these going to be tags instead?
      		this_topic = ProficiencyTopic.get_by_key_name(args[3] + "_" + args[4])
      		if this_topic is None: 
      		    logging.info('creating new topic %s in quiz subject %s' % (args[4], args[3]) )
      		    this_topic = ProficiencyTopic(key_name = args[3] + "_" + args[4], name=args[4], proficiency=this_proficiency)
      		    save.append(this_topic)
      		new_quiz_item.topic = this_topic
      		new_quiz_item.proficiency = this_proficiency
      		new_quiz_item.content_url = args[5]
      		new_quiz_item.theme = new_quiz_item.get_theme(args[5])
      		save.append(new_quiz_item)
      		logging.info('making new quiz item with content: %s, answers: %s, quiz subject: %s, topic: %s, and url: %s' %
      		            (new_quiz_item.content, new_quiz_item.answers, new_quiz_item.proficiency.name, new_quiz_item.topic.name,
      		             new_quiz_item.content_url))
      		return save
      		db.put(save)
      		return str(new_quiz_item.key())
      		      




  def Jeditable(self, *args):   # set moderation status for raw item
      return args[0]




######## OPENCALAIS HELPER METHOD ##########

  def hund(self, *args):  # Workaround for 100,000 character limit for SemanticProxy.
		#page = 'http://' + str(args[0].replace('http%3A//',''))
		webpage = urlfetch.fetch(args[0])
		soup = BeautifulSoup(webpage.content)
		the_text = soup.findAll(text=True)[0:1000]
		all_text = []
		print ""
		for t in the_text:
			all_text.append(t.encode('utf-8'))
		print(string.join(all_text)[0:99999])
		#print soup.contents[1].findAll(text=True)
		#print str(page.contents)	

        
       





      	
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
    
    
    
    


class RPCPostHandler(webapp.RequestHandler):
  """ Allows the functions defined in the RPCMethods class to be RPCed."""
  def __init__(self):
    webapp.RequestHandler.__init__(self)
    self.methods = RPCMethods()
 
  def post(self):
    args = simplejson.loads(self.request.body)
    func, args = args[0], args[1:]
   
    if func[0] == '_':
      self.error(403) # access denied
      return
     
    func = getattr(self.methods, func, None)
    if not func:
      self.error(404) # file not found
      return

    result = func(*args)
    self.response.out.write(simplejson.dumps(result))
        




class QuizEditorPost(webapp.RequestHandler): 

    def get(self):    
      	if self.request.get('action') == "LoadAnswers": return self.response.out.write( self.LoadAnswers() )
      	
      	    
    def post(self):    
      	if self.request.get('action') == "NewTopic": return self.response.out.write( self.NewTopic() )
      	if self.request.get('action') == "LoadAnswers": return self.response.out.write( self.LoadAnswers() )
      	if self.request.get('action') == "SubmitItem": return self.response.out.write( self.SubmitItem() )	

    def NewTopic(self):   # set moderation status for raw item
        this_subject = Proficiency.gql("WHERE name = :1", self.request.get('subject_name')).get()
        new_topic = ProficiencyTopic(name = self.request.get('topic_name'), proficiency = this_subject)
        db.put(new_topic)
        from utils.webapp import template
        from utils.utils import tpl_path
        template_values = {"subject": this_subject, "new_topic":new_topic}
        path = tpl_path('quizbuilder/item_topic.html')
        return template.render(path, template_values)

    def LoadAnswers(self):     
		correct_answer = self.request.get('correct_answer')
		item_text = self.request.get('item_text')
		from quizbuilder.answers import Answers
		answers = Answers()
		from utils.webapp import template
		from utils.utils import tpl_path        
		template_values = {"answers": answers.load(correct_answer, item_text)}
		path = tpl_path('quizbuilder/answer_template.html')
		return template.render(path, template_values)





                
    def SubmitItem(self):   
        if len( self.request.get('item_key') ) < 1:
        	this_item = QuizItem()
        else: 
            this_item = QuizItem.get(self.request.get('item_key'))
        from model.proficiency import Proficiency, ProficiencyTopic
        this_proficiency = Proficiency.gql("WHERE name = :1", self.request.get('subject_name') ).get()
        # Approval
        this_item.pending_proficiency = this_proficiency
        this_item.topic = ProficiencyTopic.gql("WHERE name = :1 AND proficiency = :2", self.request.get('topic_name'), this_proficiency).get()
        this_item.index = self.request.get('correct_answer')
        this_item.answers = self.request.get('answers').split(",") 
        logging.info(this_item.answers)
        this_item.content = self.request.get('item_text')
        db.put(this_item)
        logging.info('saving new quiz item with subject %s and index %s' % (self.request.get('subject_name'), self.request.get('correct_answer') ))
        from utils.webapp import template
        from utils.utils import tpl_path        
        template_values = {"subject": this_proficiency}
        path = tpl_path('quizbuilder/quiz_item_template.html')
        return template.render(path, template_values)

                
