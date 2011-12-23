import logging
import time

import uuid

from bctservices.crud import BasicCRUDService

class TripsDb(BasicCRUDService):

    def __init__(self, remote_client, riak, bucket_name):
        self.remoting = remote_client
        BasicCRUDService.__init__(self, riak, bucket_name)

    def __send_invite_email(self, trip_id, trip_data, invite):
# What is the link going to be?
# How do we do a template?
# Need to get the user information for the invitor.
        template_vars = trip_data.copy()
        template_vars.update(invite)
        template_vars['url'] = 'http://bctrax.dev/app/home'
        template_vars['id'] = trip_id

        message = """
        %(first)s, You have been invited on a trip!

        Go to %(url)s#trips/%(id)s to view the details of the trip and accept the invitation.

        More about the trip:
            Trip: %(name)s
            Dates: %(start)s - %(end)s
            Going to: %(destination)s
        """ % template_vars

        email_service = self.remoting.service('Email')
        command = email_service.send(to=invite['email'],
                subject="You have been invited on a trip",
                message=message)
        self.remoting.call(command)

    def invite(self, trip_id, invitor, invite):
        result = invite.copy()
        result['id'] = str(uuid.uuid4())

        bucket = self.riak.bucket(self.bucket_name)
        logging.debug("Get trip by id: %s" % trip_id)
        trip = bucket.get(str(trip_id))
        trip_data = trip.get_data()

        if not trip_data.has_key('friends'):
            trip_data['friends'] = []

        trip_data['friends'].append(result)
        trip.set_data(trip_data)
        trip.store()

        self.__send_invite_email(trip_id, trip_data, invite)

        return result

