from bctplugins import entrypoint

from .service import EmailService

class EntryPoint(entrypoint.MessagingEntryPointFactory):

    def assemble_service(self):
        smtp_config = self.config.get('smtp', {'host': 'localhost', 'port': 25})
        return EmailService(smtp_config)

