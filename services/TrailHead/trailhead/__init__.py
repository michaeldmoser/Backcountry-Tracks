from pkg_resources import resource_filename

from .entrypoint import EntryPoint

from .handlers import BaseHandler

class Webroot(object):
    '''
    @property
    def javascript_files(self):
        return [resource_filename('trailhead', 'webroot/tripplannerapp.js')]
    '''

    @property
    def stylesheets(self):
        return [resource_filename('trailhead', 'webroot/bct.css')]

