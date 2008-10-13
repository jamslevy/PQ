import logging
# Log a message each time this module get loaded.
logging.info('Loading %s', __name__)
import random
import string
import re
from google.appengine.api import urlfetch
import cgi
import wsgiref.handlers
import os
import datetime, time
from .model.quiz import ContentPage, Proficiency, ProficiencyTopic, RawQuizItem
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

from google.appengine.ext.webapp import util
import simplejson

# Relevency Tally for Semantic Tags
from collections import defaultdict
import operator 


from .utils.utils import tpl_path
from .lib.BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, SoupStrainer  # HTML Parsing Library
from .lib import rdfxml



# class for semantic analysis - semanticproxy, class for parsing. 
SEMANTICPROXY_URL = "http://service.semanticproxy.com/processurl/aq9r8pmcbztd4s7s427uw7zg/rdf/" # USE RDF ENDPOINT
SEMANTICPROXY_MICRO_URL = "http://service.semanticproxy.com/processurl/aq9r8pmcbztd4s7s427uw7zg/microformat/" 
TILDE_BASE_URL = "http://tilde.jamslevy.user.dev.freebaseapps.com/"
TILDE_TYPE_LIMIT = 10 # Maximum number of types to query per request topic.
TILDE_TOPIC_LIMIT = 4 # Maximum number of topics per type to list in response. 
TILDE_EXCLUDE = 'music,film' # should be array
TRUNCATE_URL = "http://pqstage.appspot.com/truncate_page/?url=" 

DEFAULT_PAGES = [#"http://en.wikipedia.org/wiki/Inference", 
                 "http://en.wikipedia.org/wiki/Renewable_energy",
                 ]

AC_LIMIT = 31 # Limit of answer choice candidates per quiz item
AC_MIN = 8 # Minimum of answer choices required.

RAW_ITEMS_PER_PAGE = 5 # Limit of quiz items created per page 

RAW_ITEMS_PER_TAG = 2 # Limit of quiz items created per page

QUIZBUILDER_LIMIT = 1

QUIZBUILDER_PATH = 'quizbuilder/'



class RawItemInduction(webapp.RequestHandler):  
 
    def get(self, *args):
        topic = self.save_topic(args[0][1],args[0][2])
        page = self.save_url(args[0][0], topic)  
        build_items = BuildItemsFromPage()
        # two part process
        raw_quiz_items = build_items.get(page)
        if not raw_quiz_items: return []
        saved_items = []
        #len(raw_quiz_items)
        for item in raw_quiz_items[0:5]:
			save_item = self.save_item(item)
			if save_item:
				saved_items.append(save_item)
			else: 
				print "unable to save item: " + str(item)
				continue

        return saved_items 
            
                
        #self.response.out.write(template.render(path, template_values))
            

    def save_url(self, page, this_topic):
        saved_page = ContentPage.get_by_key_name(str([page,this_topic]))
        if saved_page: # check value
            saved_page.delete()
            return saved_page
        else:
            new_page = ContentPage(key_name = str([page,this_topic]), url = page, topic = this_topic ) # make sure page is urlencoded.
            new_page.put()
            return new_page

    def save_topic(self, topic, proficiency):
        saved_topic = ProficiencyTopic.get_by_key_name(str([topic,proficiency]))
        if saved_topic: # check value
            return saved_topic
        else: 
            try:
                this_proficiency = Proficiency.gql("WHERE name = :1", proficiency).get()
                new_topic = ProficiencyTopic(key_name = str([topic,proficiency]), name = topic, proficiency = this_proficiency)
                new_topic.put()
                return new_topic
            except:
                return False
            
                             
    def save_item(self, item):
        try: # encode text
            this_pre_content = db.Text(item['raw_content'][0], encoding='utf-8')
            this_content = db.Text(item['raw_content'][1], encoding='utf-8')
            this_post_content = db.Text(item['raw_content'][2], encoding='utf-8')
        except:
            this_pre_content = db.Text(item['raw_content'][1])
            print "Unable to decode item content"
            logging.error('Unable to decode item content')
            return False
        try:
            new_raw_item = RawQuizItem(page = item['page'],
                                    answer_candidates = item['similar_topics'],
                                    index = item['correct_answer'],
                                    pre_content = this_pre_content,
                                    content = this_content,
                                    post_content = this_post_content,
                                    moderated = False)
            #new_raw_item.put()
            return new_raw_item 
        except:
            print 'Unable to save raw quiz item' 
            logging.error('Unable to save raw quiz item')
            return False
           
                  
class QuizBuilder(webapp.RequestHandler):

    def get(self):

        template_values = {}
        raw_quiz_items = self.load_saved_items()
        template_values["raw_quiz_items"] = raw_quiz_items
        path = tpl_path(QUIZBUILDER_PATH + 'quizbuilder.html')
        self.response.out.write(template.render(path, template_values))


    def load_saved_items(self):
    	raw_quiz_items = []
        these_items = []
        all_items = RawQuizItem.all()
        if self.request.get('topic'): 
            for item in all_items:
                if item.page.topic.name == self.request.get('topic'): 
                    these_items.append(item)
                else: continue
        else: these_items = all_items
        for this_raw_item in these_items[0:QUIZBUILDER_LIMIT]:
			raw_item = {}
			raw_item['pre_content'] = this_raw_item.pre_content
			raw_item['content'] = this_raw_item.content
			raw_item['post_content'] = this_raw_item.post_content
			raw_item['answer_candidates'] = this_raw_item.answer_candidates
			raw_item['index'] = str(this_raw_item.index)
			raw_item['url'] = str(this_raw_item.page.url)
			raw_item['topic'] = str(this_raw_item.page.topic.name)
			raw_quiz_items.append(raw_item) 
        return raw_quiz_items


            



class BuildItemsFromPage():
    
  def get(self, page):
        raw_quiz_items = []
        tag_threshold = 0
        soup = self.get_soup(page)
        if not soup: return False
        tags = self.get_tags(soup)
        for tag in tags[0:RAW_ITEMS_PER_PAGE]:  # Slice [1:...]
        # Check if tag is too short, or too common. (the "she" problem)
        # CHECK IF TAG IS A TYPED TOPIC ON FREEBASE 
            # Make sure that get_similar_topics and get_paragraphs_containing_tag are successful.
            similar_topics = self.get_similar_topics(tag)
            if similar_topics: # not just if it exists, but if there's a list.
               tag_threshold += 1
               raw_content_groups = self.get_raw_content_groups(soup.findAll('c:document'), tag)
               for raw_content in raw_content_groups:
                     #If len(get_similar_topics(tag)) < 1, add synonym tags or related tags in Answer Candidate
                    raw_quiz_item = {"similar_topics" : similar_topics, "raw_content": raw_content, "correct_answer": tag, "page": page }
                    raw_quiz_items.append(raw_quiz_item)
            continue 

        return raw_quiz_items


  def get_soup(self, page):
	#in case we need to meet 100k limit, truncate page.
	soup_url = SEMANTICPROXY_URL +  str(page.url)    # + TRUNCATE URL + 
	# timeout for fetch_page (and all fetch pages)
	fetch_page = urlfetch.fetch(soup_url)              # perform semantic analysis
	soup = BeautifulSoup(fetch_page.content) #whole page
	try: # look for error
		exception = soup.findAll('exception')[0].contents[0]
		print exception
		return False
	except: return soup 
	
	  
  def get_tags(self, soup):
	page_tags = soup.findAll('c:exact')
	if len(page_tags) == 0: return "no tags" 
	tags = [] # for a page, get a relevency-ranked list of topics found in the text. 
	for tag in page_tags:
		tags.append(str(tag.contents[0]))
	tags = self.rank_tags(tags)
	return tags  
    
  def rank_tags(self, l):
    # tag ranking helper function
    # take a list of tags ['tag1', 'tag2', 'tag2', tag3'....]
    # sort set of tags by order of frequency
    tally = defaultdict(int)
    for x in l:
        tally[x] += 1
    sorted_tags = sorted(tally.items(), key=operator.itemgetter(1))
    tags = []
    for tag in sorted_tags:
        tags.append(tag[0]) 
    tags.reverse()
    return tags
          
  def get_similar_topics_edgelist(self, tag):   # only used for graph
    # Freebase request to get similar topics for a tag.
    tag = tag.replace(' ','%20') #urlencode tag
    tilde_request = str(TILDE_BASE_URL) + "?format=xml&topic_limit=" + str(TILDE_TOPIC_LIMIT) + "&type_limit=" + str(TILDE_TYPE_LIMIT) + "&exclude=" + str(TILDE_EXCLUDE) + "&request=" + str(tag)
    try:
        tilde_response = urlfetch.fetch(tilde_request)
    except:
        logging.debug('Unable to fetch tilde response') 
    tilde_soup = BeautifulStoneSoup(tilde_response.content)
    entries = [entry.contents for entry in tilde_soup.findAll('entry')]
    similar_topics = [str(topic.contents[0]) for topic in tilde_soup.findAll('title')]
    similar_ids = [str(id.contents[0]) for id in tilde_soup.findAll('id')]
    similar_types = [str(type.contents[0]) for type in tilde_soup.findAll('type')]
    for id in similar_ids:
    	print id + " " + similar_types[similar_ids.index(id)]
    if len(similar_topics) >= AC_MIN:
        return similar_topics[1:AC_LIMIT]
    else:
        return False 
        
                  
  def get_similar_topics(self, tag):
    # Freebase request to get similar topics for a tag.
    tag = tag.replace(' ','%20') #urlencode tag
    tilde_request = str(TILDE_BASE_URL) + "?format=xml&topic_limit=" + str(TILDE_TOPIC_LIMIT) + "&type_limit=" + str(TILDE_TYPE_LIMIT) + "&exclude=" + str(TILDE_EXCLUDE) + "&request=" + str(tag)
    try:
        tilde_response = urlfetch.fetch(tilde_request)
    except:
        logging.debug('Unable to fetch tilde response') 
    tilde_soup = BeautifulStoneSoup(tilde_response.content)
    similar_topics = [str(topic.contents[0]) for topic in tilde_soup.findAll('title')]
    if len(similar_topics) >= AC_MIN:
        return similar_topics[1:AC_LIMIT]
    else:
        return False 
        
  def get_raw_content_groups(self, page_text,tag):
    # find paragraph in text containing a tag.    
    # todo: Templates for mediawiki and google knol
    raw_content_groups = []
    w = re.compile(tag)
    #tag_word = " " + tag + " " #regexp -> 're.IGNORECASE | re.MULTILINE'
    for p in page_text[0].contents:
        psoup = BeautifulSoup(p)
        for paragraph in psoup.findAll('p'):
            if paragraph.find(text=re.compile(r'\W%s\W' % tag )):  # Is tag in this paragraph? 
                the_paragraph = self.highlightAnswer(paragraph, tag) 
                # GET NEXT AND PREV <P> ELEMENTS CONTAINING SIGNIFICANT CONTENT. 
                if (paragraph.findPreviousSibling('p') == None):
                    previous_paragraph = ""
                else:
                    previous_paragraph = paragraph.findPreviousSibling('p').contents[0]
                if (paragraph.findNextSibling('p') == None):
                    next_paragraph = ""
                else:
                    next_paragraph = paragraph.findNextSibling('p').contents[0]
                paragraphs = (previous_paragraph, the_paragraph, next_paragraph)
                clean_paragraphs = []
                for p in paragraphs:
                	p = p.encode('utf-8')
                	p = p.replace('\n', '')
                	clean_paragraphs.append(p) 
                raw_content_groups.append(clean_paragraphs)#return paragraph_containing_tag # this only returns the first instance.
            else:
                continue  # tag not found in paragraph
        return raw_content_groups[0:RAW_ITEMS_PER_TAG]  # This slice could also be a threshold, or randomized, to avoid bias to the top of the document. 
                
     
                
  def highlightAnswer(self, text, tag):
    # apply HTML markup to answer within quiz item content
     text = str(text)
     str_tag = str(tag)
     return text.replace(str_tag, '<span class="answer_span">%s</span>' % str_tag)               
     #return text.replace(str_tag, '<span style="border:1px solid #E2C922; padding:0 5px; margin:0 5px;font-weight:bold;">%s</span>' % str_tag)               
                 
                 



  def truncate_page(self, url):
    # Truncate page to meet OpenCalais 100k limit.
    fetch_page = urlfetch.fetch(soup_url)   
    soup = BeautifulSoup(fetch_page.content) # necessary?
    
    # truncate HTML document. 
    




        


class InductionInterface(webapp.RequestHandler):

    def get(self):
        template_values = {}
        path = tpl_path(QUIZBUILDER_PATH + 'induction.html')
        self.response.out.write(template.render(path, template_values))
        


    














