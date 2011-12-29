from pkg_resources import resource_filename
from bctplugins import entrypoint
from riak import RiakClient

from .service import AdventurerRepository
from .mailer import Mailer

class EntryPoint(entrypoint.MessagingEntryPointFactory):

    def assemble_service(self):
        bucket_name = self.config['database']['bucket']
        riak = RiakClient(self.config['database']['host'])
        base_url = self.environ.config['trailhead_url']

        smtp_config = self.config.get('smtp', {'host': 'localhost', 'port': 25})
        smtp_host = smtp_config.get('host', 'localhost')
        smtp_port = smtp_config.get('port', 25)
        
        mailer = Mailer(host=smtp_host, port=smtp_port)

        service = AdventurerRepository(bucket_name = bucket_name,
                db = riak, trailhead_url = base_url, mailer=mailer)

        return service


class Templates(object):

    @property
    def javascript_files(self):
        return [resource_filename('adventurer', 'webroot/adventurer.js')]

    @property
    def templates(self):
        return open(resource_filename('adventurer', 'webroot/template.html'), 'r').read()

    @property
    def stylesheets(self):
        stylesheets = [
                resource_filename('adventurer', 'webroot/front.css'),
                ]
        return stylesheets





