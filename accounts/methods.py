import logging
# Log a message each time this module get loaded.
logging.info('Loading %s', __name__)
import cgi
from .model.user import Profile, QuizTaker, ProfilePicture
from model.account import Account, Award, SponsorPledge, Sponsorship
import random
from google.appengine.ext import db




def registered(user_key):
    this_user = Profile.get_by_key_name(user_key)
    if this_user: return this_user
    else: return False
    
    



def register_user(user_key, nickname, fullname, email):
    profile_path = nickname.lower()
    profile_path = profile_path.replace(' ','_')
    photo = default_photo()
    new_user = Profile.get_or_insert(key_name = user_key,
                          unique_identifier = user_key, # redundancy
                          nickname = nickname,
                          fullname = fullname,
                          profile_path = profile_path,
                          photo = photo,
                          )
                          
    if email: new_user.email = email
    new_user.put()
    return new_user 



def register_qt(user_key, nickname):
    new_qt = QuizTaker.get_or_insert(key_name = user_key,
                                     unique_identifier = user_key, # redundancy
                                     nickname = nickname,
                                     )
    new_qt.put()
    return new_qt                                   
    

def register_account(user_key, nickname):
    new_account = Account.get_or_insert(key_name = user_key,
                                     unique_identifier = user_key, # redundancy
                                     nickname = nickname # redundancy 
                                     )
    new_account.put()
    return new_account                                   
    
        

def default_photo():
	photos = ProfilePicture.gql("WHERE type = :1", "pq").fetch(10)
	photo = random.sample(photos, 1) 
	return photo[0]






class Awards():
	
	# Analyze proficiency levels and topiclevels, give awards to quiztakers. 

     # Eventually, a quiztaker attribute will have to mark whether its been processed.
    
	EXCELLENCE_PROFICIENCY_THRESHOLD = 0.1
	FLUENCY_PROFICIENCY_THRESHOLD = .55	
	EXCELLENCE_TOPIC_THRESHOLD = 60 #90
	FLUENCY_TOPIC_THRESHOLD = 35  #55
	
	def check_all(self, qt=False): # specify qt for a single person
		self.save_awards = [] # for batch datastore trip
		if not qt: quiz_takers = QuizTaker.all().fetch(1000) # TODO: do more than 1000, with version check.
		else: quiz_takers = [qt]
		for qt in quiz_takers:
			self.check_taker(qt)
		db.put(self.save_awards)
		return len(self.save_awards)
			
	def check_taker(self, qt):			
	  # Re-Initialize Values 
	  from collections import defaultdict
	  self.fluency = defaultdict(list)
	  self.excellence = defaultdict(list)
	  self.awarded_proficiencies = {}
	  self.topics_in_proficiency = defaultdict(list)
	  for level in qt.topic_levels:
		self.topics_in_proficiency[level.topic.proficiency.key()].append(level.topic.key())
		self.add_topic_fluency(level)
		self.add_topic_excellence(level)
	  self.check_proficiency_excellence()
	  self.check_proficiency_fluency()
	  self.upgrade_awards(qt)
	  return


	def add_topic_fluency(self, level):
		# topic_level should be replaced by percentile	
	  if level.topic_level > self.FLUENCY_TOPIC_THRESHOLD: 
	      self.fluency[level.topic.proficiency.key()].append({level.topic.key() : level.topic_level}) 
	      return True
	  else: return False	


	def add_topic_excellence(self, level):	
	  if level.topic_level > self.EXCELLENCE_TOPIC_THRESHOLD: 
	      self.excellence[level.topic.proficiency.key()].append({level.topic.key() : level.topic_level}) 
	      return True
	  else: return False

	def check_proficiency_excellence(self):
		for proficiency, topics in self.topics_in_proficiency.items():
			logging.info('ratio of excellent scores to total length of topics - %s',float(float(len(self.excellence[proficiency])) / float(len(topics))) )
			if float(float(len(self.excellence[proficiency])) / float(len(topics))) > self.EXCELLENCE_PROFICIENCY_THRESHOLD: self.awarded_proficiencies[proficiency] = "excellence"

	def check_proficiency_fluency(self):
		for proficiency, topics in self.topics_in_proficiency.items():
			if float(float(len(self.fluency[proficiency])) / float(len(topics))) > self.FLUENCY_PROFICIENCY_THRESHOLD: self.awarded_proficiencies[proficiency] = "fluency"
	  	  

	def upgrade_awards(self, qt):
		for proficiency, type in self.awarded_proficiencies.items():
			logging.info('upgrading awards for user %s and proficiency %s', qt.unique_identifier, proficiency)
			#topic_list = self.topics_in_proficiency[proficiency]   - Only Needed if we need all the topics in the proficiency
			if type == "fluency": rankings = self.fluency[proficiency]
			if type == "excellence": rankings = self.excellence[proficiency]
			this_account = Account.get_by_key_name(qt.unique_identifier)
			this_profile = Profile.get_by_key_name(qt.unique_identifier)
			if not this_account: 
			    this_account = register_account(qt.unique_identifier)
			award_topics = [] 
			award_levels = []
			for rank_dict in rankings:
				for topic, level in rank_dict.items():
					award_topics.append(topic)
					award_levels.append(level)
					
			# make sure that awards are not duplicated - can we avoid the loop in general? 
			award_key_name = str(this_profile.unique_identifier) + str(proficiency.name) + str(type)
			new_award = Award.get_or_insert(key_name = award_key_name,
			                   type = type,
			                   topics = award_topics,
			                   levels = award_levels,
			                   proficiency = proficiency,
			                   winner = this_profile )
			self.save_awards.append(new_award)

	





class Sponsorships():


	def check_all(self, qt=False):
		self.save_sponsorships = [] # for batch datastore trip
		awards = Award.all().fetch(1000)
		for award in awards:
			self.check_award(award)
		db.put(self.save_sponsorships)
		return len(self.save_sponsorships)
			
	def check_award(self,award):
		give_sponsorship = {}
		for pledge in award.winner.sponsorships_pledged_to_me:
			# eventually allow for corporate sponsor checks.    # This should use zip().
			if award.winner.unique_identifier == pledge.sponsor.unique_identifier: continue #can't sponsor yourself. TODO: this should be done before now!
			give_sponsorship[pledge] = True
			# check to make sure it hasn't been awarded yet. 
			existing_sponsorships = pledge.sponsorships.fetch(1000)
			if existing_sponsorships: 
			    if award.winner in existing_sponsorships: give_sponsorship[pledge] = False 
			if give_sponsorship[pledge] == True: self.give_sponsorship(pledge, award)				
		return
		
		


	def give_sponsorship(self, pledge, award):
		logging.info('saving new sponsorship')
		new_sponsorship = Sponsorship(sponsor = pledge.sponsor,
		                              recipient = award.winner,
		                              package = pledge.package,
		                              sponsor_type = pledge.sponsor_type,
		                              award_type = award.type,
		                              award = award,
		                              pledge = pledge )
		self.save_sponsorships.append(new_sponsorship)
		self.notify_sponsor(pledge.sponsor)
		return


	def notify_sponsor(self,sponsor):
		pass#print "I will email", sponsor, "after checking my RSS feeds"
			
	# Based on awards that have been given, activate scholarships. 







class SponsorPledge():

  def submit(self, args):
  	session = Session()
  	from .model.account import Account
  	from .model.user import Profile
  	sponsor_type = "personal" # or corporate
  	package = args[0]
  	award_type = args[1]
  	raw_target = [args[2]] # for more than one user. TODO: Front-end.
  	target = []
  	activated = []
  	single_target = False
  	for u in raw_target: 
  	    t = Profile.get(u)
  	    if len(raw_target) > 1: single_target = t
  	    target.append(t.key())
  	    activated.append(False)
  	from model.account import SponsorPledge
  	new_pledge = SponsorPledge(#key_name?
  	                           sponsor = session['user'],
  	                           sponsor_type = sponsor_type,
  	                           package = package,
  	                           award_type = award_type,
  	                           target = target,
  	                           type = type,
  	                           activated = activated)
  	
  	# if only a single person is receiving the pledge
  	if single_target:
  		new_pledge.single_target = single_target
  	# if any subject was chosen
  	if args[3] != "any_subject":
  		from model.proficiency import Proficiency
  		new_pledge.proficiency = Proficiency.get(args[3])
  		
  	db.put(new_pledge)
  	return "True"
