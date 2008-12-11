import logging
# Log a message each time this module get loaded.
logging.info('Loading %s', __name__)
import cgi
import wsgiref.handlers
import os
import datetime, time
from utils.webapp import template
from utils import webapp
from utils.webapp import util
from .utils.utils import tpl_path

HOMEPAGE_PATH = 'homepage/'           
              


class ViewHomepage(webapp.RequestHandler):

    def get(self):
        template_values = {'no_load': True, 'page_title': 'Plopquiz'}
        path = tpl_path(HOMEPAGE_PATH + 'homepage.html')
        self.response.out.write(template.render(path, template_values))


class ExitPage(webapp.RequestHandler):

    def get(self):
        template_values = {'no_load': True}
        path = tpl_path(HOMEPAGE_PATH + 'exit.html')
        if self.request.get('o'): path = tpl_path(HOMEPAGE_PATH + 'old_exit.html')  #for demo, and old time's sake.
        self.response.out.write(template.render(path, template_values))

"""
class AboutUs(webapp.RequestHandler):

    def get(self):
        template_values = {'no_load': True}
        path = tpl_path(HOMEPAGE_PATH + 'about.html')
        self.response.out.write(template.render(path, template_values))
"""        
