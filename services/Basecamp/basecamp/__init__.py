from pkg_resources import resource_filename

class Webroot(object):

    @property
    def javascript_files(self):
        return [
                resource_filename('basecamp', 'webroot/basecamp.js'),
                ]

    @property
    def templates(self):
        return open(resource_filename('basecamp', 'webroot/templates.html')).read()

