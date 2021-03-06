import logging
from utils import webapp
from google.appengine.ext import db
import string, re
from google.appengine.api import urlfetch
import urllib
from utils import simplejson
from utils.utils import ROOT_PATH, tpl_path
from utils.gql_encoder import GqlEncoder, encode
from .model.quiz import QuizItem, RawQuizItem,  ContentPage
from .model.proficiency import ProficiencyTopic, Proficiency
import views
from induction import RawItemInduction
from dev.methods import dump_data


EDITOR_PATH = "editor/"

class XMLRPCMethods(webapp.RequestHandler): # deprecated
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
  	this_subject = Proficiency.get(args[1])
	save_topic = ProficiencyTopic(name = args[0], proficiency = this_subject)
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




######## EDITOR METHODS ##########  

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
      this_subject = Proficiency.get_by_key_name(args[0]) # try get_or_insert if Proficiency is key
      prof_pages = this_subject.pages.fetch(10)
      raw_items = []
      for p in prof_pages:
          these_items = RawQuizItem.gql("WHERE page = :1 AND moderated = False", p ) # only get unmoderated items
          items = these_items.fetch(1000)
          raw_items += items
      try: return encode(raw_items)  # get 10 at a time...todo: lazy rpc-loader.
      except: return simplejson.dumps([])

  def GetTopicsForProficiency(self, *args):  
      topics = []
      this_subject = Proficiency.gql("WHERE name = :1 ORDER BY date DESC", args[0]) # try get_or_insert if Proficiency is key
      topics = ProficiencyTopic.gql("WHERE proficiency = :1 ORDER BY date DESC", this_subject.get().key())
      try: return encode(topics.fetch(10))  # get 10 at a time...todo: lazy rpc-loader.
      except: return simplejson.dumps([])
      


  def SetItemModStatus(self, *args):   # set moderation status for raw item
      this_item = db.get(args[0])
      if args[1] == "false": this_item.moderated = False
      if args[1] == "true": this_item.moderated = True
      this_item.put()
      return encode(this_item)




  def Jeditable(self, *args):   # set moderation status for raw item
      return args[0]





      	
class RPCHandler(webapp.RequestHandler):
  # AJAX Handler
  def __init__(self):
    webapp.RequestHandler.__init__(self)
    self.methods = XMLRPCMethods()

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

	def get(self):    
		from utils.random import jsonp
		if self.request.get('action') == "LoadUbiquityAnswers": return self.response.out.write( jsonp(self.request.get("callback"),self.LoadUbiquityAnswers()) )
		if self.request.get('action') == "SubmitItem": return self.response.out.write( jsonp(self.request.get("callback"), self.SubmitItem() ) )	
					
	def post(self): 
	
		#TEMP
		# editing subjects
		if len(self.request.path.split('/subject_img/')) > 1: return self.response.out.write(self.upload_subject_img() )
		if self.request.get('action') == 'refresh_subjects': return self.response.out.write( self.refresh_subjects()  ) 		
		if self.request.get('action') == 'subject_blurb': return self.response.out.write(simplejson.dumps(  self.update_subject_blurb()  )) 
		if self.request.get('action') == 'change_rights': return self.response.out.write(self.change_rights() ) 
		if self.request.get('action') == 'add_link': return self.response.out.write(self.add_link() ) 
		if self.request.get('action') == 'remove_link': return self.response.out.write(self.remove_link() ) 
		if self.request.get('action') == 'change_video': return self.response.out.write(self.change_video() )
		if self.request.get('action') == 'delete_subject_image': return self.response.out.write(self.delete_subject_image() ) 						   
		if self.request.get('action') == 'create_new_subject': return self.response.out.write(self.create_new_subject() ) 	
		if self.request.get('action') == 'join_subject': return self.response.out.write(self.join_subject() ) 	
		if self.request.get('action') == 'send_invite': return self.response.out.write(self.send_invite() ) 
		
				
		# editing quiz items
		if self.request.get('action') == "NewTopic": return self.response.out.write( self.NewTopic() )
		if self.request.get('action') == "LoadAnswers": return self.response.out.write( self.LoadAnswers() )

		if self.request.get('action') == "SubmitItem": return self.response.out.write( self.SubmitItem() )	

		if self.request.get('action') == "GetBillUpdates": return self.response.out.write( self.GetBillUpdates() )	


	######################

	#Editing Subjects

	#####################


	def refresh_subjects(self):	
		from utils.appengine_utilities.sessions import Session
		self.session = Session()	
		from utils.webapp import template
		path = tpl_path(EDITOR_PATH +'subject_container.html')
		from editor.methods import get_subjects_for_user     
		offset = int(self.request.get('offset'))
		new_subjects = get_subjects_for_user(self.session['user'], offset=offset)
		if len(new_subjects) < 5: new_offset = 0
		else: new_offset = offset + 5
		template_values = { 'subjects' : new_subjects, 'offset': new_offset}
		return template.render(path, template_values)	
		
	def update_subject_blurb(self):
	  from model.proficiency import Proficiency
	  subject_name = self.request.get('subject_name')
	  this_subject = Proficiency.get_by_key_name(subject_name)
	  if this_subject is None: 
		  logging.error('no subject found when saving blurb for subject_name %s ', subject_name)
		  return "no subject found"
	  this_subject.blurb = self.request.get('new_blurb')
	  db.put(this_subject)
	  return "OK"
	  
	def upload_subject_img(self):
	  subject_name = self.request.path.split('/subject_img/')[1].replace('%20',' ')
	  from model.proficiency import Proficiency
	  this_subject = Proficiency.get_by_key_name(subject_name)
	  new_image = this_subject.new_image(self.request.get('subject_img'))
	  db.put([this_subject, new_image])
	  logging.info('saved new image for subject %s' % (this_subject.name))
	  from utils.webapp import template
	  path = tpl_path(EDITOR_PATH +'load_subject_images.html')
	  template_values = {'s': {"subject": this_subject, "is_member": "admin" }} # Only admins can upload photos, for now. 
	  return template.render(path, template_values)
		   
	  
	def delete_subject_image(self):
		from model.proficiency import Proficiency, SubjectImage
		subject_name = self.request.get('subject_name')
		this_subject = Proficiency.get_by_key_name(subject_name) 
		this_img = SubjectImage.get( self.request.get('img_key') )
		logging.info('removed img for subject %s', this_subject.name )
		db.delete(this_img)
		db.put(this_subject)		
		from utils.webapp import template
		path = tpl_path(EDITOR_PATH +'load_subject_images.html')
		template_values = {'s': {"subject": this_subject, "is_member": "admin" }} # Only admins can edit links, for now. 
		return template.render(path, template_values)	
		
	def change_rights(self):
		from utils.appengine_utilities.sessions import Session
		self.session = Session()
		from model.proficiency import Proficiency
		from model.user import SubjectMember
		subject_name = self.request.get('subject_name')
		this_subject = Proficiency.get_by_key_name(subject_name) 
		this_change = self.request.get('rights_action')
		this_membership = SubjectMember.gql("WHERE subject = :1 AND user = :2", this_subject, self.session['user']).get()
		if this_change == "make_admin":
			logging.info('make admin')
			this_membership.is_admin = True
		if this_change == "remove_admin":
			this_membership.is_admin = False
		db.put([this_subject,this_membership])
		logging.info('user %s has had admin status set to %s for subject %s' % (self.session['user'].unique_identifier, str(this_membership.is_admin), this_subject.name))
		from utils.webapp import template
		path = tpl_path(EDITOR_PATH +'subject/admin_rights.html')
		template_values = {'s': {"subject": this_subject}}
		return template.render(path, template_values)	
				


	def add_link(self):
		from model.proficiency import Proficiency, Link 
		subject_name = self.request.get('subject_name')
		this_subject = Proficiency.get_by_key_name(subject_name) 
		try: new_link = Link(key_name = subject_name + "_" + self.request.get('link_url'),
		                  url = self.request.get('link_url'), 
		                 title = self.request.get('link_title'), 
		                 subject = this_subject )
		except BadValueError: return "error"
		db.put([this_subject,new_link])
		logging.info('new link with url %s and title %s for subject %s' % (this_subject.name, str(new_link.url), new_link.title ) )
		from utils.webapp import template
		path = tpl_path(EDITOR_PATH +'subject/links_list.html')
		template_values = {'s': {"subject": this_subject, "is_member": "admin" }} # Only admins can edit links, for now. 
		return template.render(path, template_values)	
				
	def remove_link(self):
		from model.proficiency import Proficiency, Link 
		subject_name = self.request.get('subject_name')
		this_subject = Proficiency.get_by_key_name(subject_name) 
		this_link = Link.get( self.request.get('link_key') )
		logging.info('removed link: %s', this_link.url )
		db.delete(this_link)		
		db.put(this_subject)	
		from utils.webapp import template
		path = tpl_path(EDITOR_PATH +'subject/links_list.html')
		template_values = {'s': {"subject": this_subject, "is_member": "admin" }} # Only admins can edit links, for now. 
		return template.render(path, template_values)	
				

	def change_video(self):
		from model.proficiency import Proficiency
		subject_name = self.request.get('subject_name')
		this_subject = Proficiency.get_by_key_name(subject_name) 
		if "p=" not in self.request.get('new_video_url'):
			logging.info('video url %s is not recognizable as video playlist link', self.request.get('new_video_url'))
			return "error"
		video_code = self.request.get('new_video_url').split("p=")[1]
		this_subject.video_html = video_code
		logging.info('changed video for subject %s to %s' % (this_subject.name,video_code) )
		db.put(this_subject)		
		from utils.webapp import template
		path = tpl_path(EDITOR_PATH +'subject/video_object.html')
		template_values = {'s': {"subject": this_subject, "is_member": "admin" }} # Only admins can edit links, for now. 
		return template.render(path, template_values)	



	def create_new_subject(self):
		from utils.appengine_utilities.sessions import Session
		self.session = Session()	
		from model.proficiency import Proficiency		
		existing_subject = Proficiency.gql("WHERE name = :1", self.request.get('subject_name') ).get()
		if existing_subject is not None: 
		    logging.warning("user %s attempted to create duplicate subject with name %s" %(self.session['user'].unique_identifier, self.request.get('subject_name')) )
		    return "exists"
		this_subject = Proficiency(key_name = self.request.get('subject_name'), name = self.request.get('subject_name'))
		from model.user import SubjectMember
		this_membership = SubjectMember(keyname = self.session['user'].unique_identifier + "_" + this_subject.name, 
		                                user = self.session['user'], 
		                                subject = this_subject, 
		                                status = "public",
		                                is_admin = True)
		                                
		logging.info('user %s created subject %s'% (self.session['user'].unique_identifier, this_subject.name) )
		db.put([this_subject, this_membership])		
		from utils.webapp import template
		path = tpl_path(EDITOR_PATH +'subject_container.html')
		from editor.methods import get_subjects_for_user     
		template_values = { 'subjects' : get_subjects_for_user(self.session['user'])}
		return template.render(path, template_values)	
		


	def join_subject(self):
		from utils.appengine_utilities.sessions import Session
		self.session = Session()	
		from model.proficiency import Proficiency	
		this_subject = Proficiency.gql("WHERE name = :1", self.request.get('subject_name') ).get()
		from model.user import SubjectMember
		admin_status = False
		from google.appengine.api import users
		user = users.get_current_user()
		if user: admin_status = True
		this_membership = SubjectMember(keyname = self.session['user'].unique_identifier + "_" + this_subject.name, user = self.session['user'], subject = this_subject, is_admin = admin_status)
		logging.info('user %s joined subject %s'% (self.session['user'].unique_identifier, this_subject.name) )
		db.put([this_membership])		
		from utils.webapp import template
		path = tpl_path(EDITOR_PATH +'load_member_section.html')
		template_values = {'s': {"subject": this_subject, "is_member": "contributor" }} # Only admins can edit links, for now. 
		return template.render(path, template_values)	

	def send_invite(self):
		from utils.appengine_utilities.sessions import Session
		self.session = Session()		
		from editor.methods import send_invite
		send_invite(self.session['user'], self.request.get('subject_name'), self.request.get('email_address'))	
		return "OK"		
		
																

	######################

	#Editing Quiz Items 

	#####################

	def NewTopic(self):   # set moderation status for raw item
		this_subject = Proficiency.gql("WHERE name = :1", self.request.get('subject_name')).get()
		new_topic = ProficiencyTopic(name = self.request.get('topic_name'), proficiency = this_subject)
		db.put([this_subject, new_topic])
		if self.request.get('no_template'): return "OK"
		from utils.webapp import template
		from utils.utils import tpl_path
		template_values = {"subject": this_subject, "new_topic":new_topic}
		path = tpl_path(EDITOR_PATH + 'item_topic.html')
		return template.render(path, template_values)

	def LoadAnswers(self):     
		correct_answer = self.request.get('correct_answer')
		item_text = self.request.get('item_text')
		from editor.answers import Answers
		answers = Answers()
		from utils.webapp import template
		from utils.utils import tpl_path        
		template_values = {"answers": answers.load(correct_answer, item_text)}
		path = tpl_path(EDITOR_PATH + 'answer_template.html')
		return template.render(path, template_values)

	def LoadUbiquityAnswers(self):     
		correct_answer = self.request.get('correct_answer')
		item_text = self.request.get('item_text')
		from editor.answers import Answers
		answers = Answers()
		return simplejson.dumps(answers.load(correct_answer, item_text));

				
	# see if it can access self.user['user'] and if its a new item, save author
	def SubmitItem(self):   
		from model.proficiency import Proficiency, ProficiencyTopic
		this_subject = Proficiency.gql("WHERE name = :1", self.request.get('subject_name') ).get()
		logging.info('submitting item')
		from utils.appengine_utilities.sessions import Session
		session = Session()
		if len( self.request.get('item_key') ) < 1:
			this_item = QuizItem(pending_proficiency = this_subject)
			if session['user']: this_item.author= session['user']
		else: 
			this_item = QuizItem.get(self.request.get('item_key'))         	
		if self.request.get('item_status') == "approved":
			this_item.active = True
			this_item.pending_proficiency = None
			this_item.proficiency = this_subject        	
		if self.request.get('item_status') == "not_approved":
			this_item.active = False
			this_item.pending_proficiency = this_subject  
			this_item.proficiency = None        		
		this_item.topic = ProficiencyTopic.get( self.request.get('topic_key') )
		this_item.index = self.request.get('correct_answer')
		this_item.answers = [a.strip("'") for a in self.request.get('answers').split(",")] 
		this_item.content = self.request.get('item_text')
		save = [ this_subject, this_item]
		#if session['user']: save.append(session['user'])
		db.put( save )
		logging.info('saving new quiz item %s with subject %s and index %s' % (this_item.__dict__, self.request.get('subject_name'), self.request.get('correct_answer') ))
		if self.request.get('ubiquity'): return "OK"
		from utils.webapp import template
		from utils.utils import tpl_path        
		from editor.methods import get_membership, get_user_items		
		template_values = {"subject": this_subject, 
						   'subject_membership': get_membership(session['user'], this_subject),
						   'user_items': get_user_items(session['user'], this_subject), }
		path = tpl_path(EDITOR_PATH + 'quiz_item_editor_template.html')
		return template.render(path, template_values)

				







