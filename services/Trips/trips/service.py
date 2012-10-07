import logging
import time
from datetime import datetime
import base64
import traceback

import uuid

from bctservices.crud import BasicCRUDService
import bctks_glbldb.connection

class TripsDb(BasicCRUDService):
    list_mapreduce = """
        function (value, keyData, arg) {
            if (value.values[0].metadata['content-type'] != 'application/json')
                return [];

            var usermeta = value.values[0].metadata['X-Riak-Meta'];
            if (!usermeta['X-Riak-Meta-object_type'] ||
                    usermeta['X-Riak-Meta-object_type'] != 'trip')
                return[];

            if (value.values[0].data.length < 1)
                return [];

            var data = Riak.mapValuesJson(value)[0];
            if (data.owner == arg['owner'])
                return [data];

            var friends = data.friends;
            for (friend in friends) {
                if (friends[friend].email == arg['owner'] &&
                        friends[friend].invite_status != 'not coming')
                    return [data];
            }
            
            return [];
        }
    """

    def __init__(self, remote_client, riak, bucket_name, url, converter = None):
        self.remoting = remote_client
        self.url = url
        self.converter = converter
        BasicCRUDService.__init__(self, riak, bucket_name)

    def create(self, owner, obj):
        '''
        Add a new object
        '''
        con = bctks_glbldb.connection.Connection(self.riak)
        realm = con.Realm(self.bucket_name)
        doc = realm.Document()
        doc.update(obj)
        doc['id'] = doc.key
        doc['owner'] = owner
        doc.object_type = 'trip'

        realm.store(doc)

        return dict(doc)

    def __send_invite_email(self, trip_id, trip_data, invite):
# What is the link going to be?
# How do we do a template?
# Need to get the user information for the invitor.
        template_vars = trip_data.copy()
        template_vars.update(invite)
        template_vars['url'] = self.url
        template_vars['id'] = trip_id

        message = """
        %(first)s, You have been invited on a trip!

        Go to %(url)s#trips/%(id)s to view the details of the trip and accept the invitation.

        More about the trip:
            Trip: %(name)s
            Dates: %(start)s - %(end)s
        """ % template_vars

        email_service = self.remoting.service('Email')
        command = email_service.send(to=invite['email'],
                subject="You have been invited on a trip",
                message=message)
        self.remoting.call(command)

    def invite(self, trip_id, invitor, invite):
        result = invite.copy()
        result['id'] = str(result['email'])

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

    def __update_invite_status(self, trip_id, invitee, status):
        bucket = self.riak.bucket(self.bucket_name)
        trip = bucket.get(str(trip_id))
        trip_data = trip.get_data()

        # Not sure if I like this solution... it obfiscates the fact that the trip_data
        # object is being updated
        invite = filter(lambda i: i['email'] == invitee, trip_data['friends'])[0]
        invite['invite_status'] = status

        trip.set_data(trip_data)
        trip.store()

        return invite

    def accept(self, trip_id, invitee):
        '''Updates the staus of an invite to accepted'''
        return self.__update_invite_status(trip_id, invitee, 'accepted')

    def reject(self, trip_id, invitee):
        '''Updates the staus of an invite to not coming'''
        return self.__update_invite_status(trip_id, invitee, 'not coming')

    def get_personal_gear(self, trip, person):
        '''Return person's gear for trip'''
        bucket = self.riak.bucket(self.bucket_name)
        tripobj = bucket.get(str(trip))

        links = tripobj.get_links()
        gear_links = filter(lambda x: x.get_tag() == 'gear_personal', links)
        gear = [link.get() for link in gear_links]

        personal_gear = filter(lambda x: x.get_data()['owner'] == person, gear)
        gear_data = map(lambda x: x.get_data(), personal_gear)

        return gear_data

    def add_personal_gear(self, trip, person, gear):
        '''Add a personal gear item to trip for person'''
        gearobj = False
        bucket = self.riak.bucket(self.bucket_name)
        tripobj = bucket.get(str(trip))

        def remove_from_personal_gear(link):
            obj = link.get();
            data = obj.get_data()
            if link.get_tag() == 'gear_group' and data['gear_id'] == gear['gear_id']:
                obj.delete()
                tripobj.remove_link(link)
        map(remove_from_personal_gear, tripobj.get_links())

        if not gearobj or not gearobj.exists():
            gear_id = str(uuid.uuid4())
            gear['id'] = gear_id
            gearobj = bucket.new(gear_id, gear)

        gearobj.set_usermeta({'object_type': 'gear_personal'})
        gearobj.store()

        tripobj.add_link(gearobj, tag='gear_personal')
        tripobj.store()

        return gear

    def remove_personal_gear(self, trip_id, person, gear_id):
        '''
        Remove a piece of gear from a persons personal gear list for the trip
        '''
        bucket = self.riak.bucket(self.bucket_name)
        gearobj = bucket.get(str(gear_id))
        tripobj = bucket.get(str(trip_id))
        tripobj.remove_link(gearobj, tag='gear_personal')
        tripobj.store()
        gearobj.delete()

    def get_group_gear(self, trip):
        '''Retrieve a list of the trips shared / group gear'''
        logging.debug('Get Group Gear for %s', trip)
        bucket = self.riak.bucket(self.bucket_name)
        tripobj = bucket.get(str(trip))

        links = tripobj.get_links()
        gearlinks = filter(lambda x: x.get_tag() == 'gear_group', links)
        gear = map(lambda x: x.get().get_data(), gearlinks)

        return gear 

    def share_gear(self, trip, gear):
        '''Share a piece of gear with the trip'''
        logging.debug('Share %s gear for %s trip', trip, gear)
        gearobj = False
        bucket = self.riak.bucket(self.bucket_name)
        tripobj = bucket.get(str(trip))

        def remove_from_personal_gear(link):
            obj = link.get();
            data = obj.get_data()
            if link.get_tag() == 'gear_personal' and data['gear_id'] == gear['gear_id']:
                obj.delete()
                tripobj.remove_link(link)
        map(remove_from_personal_gear, tripobj.get_links())

        if not gearobj or not gearobj.exists():
            gear_id = str(uuid.uuid4())
            gear['id'] = gear_id
            gearobj = bucket.new(gear_id, gear)

        gearobj.set_usermeta({'object_type': 'gear_group'})
        gearobj.store()

        tripobj.add_link(gearobj, tag='gear_group')
        tripobj.store()

        return gear

    
    def unshare_gear(self, trip, gear_id):
        '''Remove a piece of gear from the group gear list'''
        bucket = self.riak.bucket(self.bucket_name)
        tripobj = bucket.get(str(trip))
        
        gearobj = bucket.get(str(gear_id))
        tripobj.remove_link(gearobj, tag='gear_group')

        gearobj.delete()
        tripobj.store()

    def store_route(self, trip_id, document):
        '''Store a GPS file as a route for a trip'''
        bucket = self.riak.bucket(self.bucket_name)
        mapbucket = self.riak.bucket('maps')
        tripobj = bucket.get(str(trip_id))

        converter = self.converter(base64.b64decode(document))
        kml_doc = converter.convert('kml')

        links = tripobj.get_links()
        routes = filter(lambda x: x.get_tag() == 'route', links)
        if len(routes) == 0:
            route_id = str(uuid.uuid4())
            routeobj = mapbucket.new_binary(route_id, str(kml_doc), content_type = 'application/vnd.google-earth.kml+xml')
            routeobj.store()
            tripobj.add_link(routeobj, tag='route')
            tripobj.store()
        else:
            route = routes[0].get()
            route.set_data(kml_doc)
            route.store()

        return True

    def get_route(self, trip_id):
        '''Retrieve a route for a trip'''
        bucket = self.riak.bucket(self.bucket_name)
        tripobj = bucket.get(str(trip_id))

        links = tripobj.get_links()
        routes = filter(lambda x: x.get_tag() == 'route', links)

        try:
            route = routes[0].get()
            return route.get_data() or ''
        except IndexError:
            return ''

    def __send_comment_notification(self, trip_id, comment_data, trip_data):
        template_vars = comment_data.copy()
        template_vars.update(trip_data.copy())
        template_vars['url'] = self.url
        template_vars['id'] = trip_id

        message = """
        %(first_name)s %(last_name)s posted a new comment on the %(name)s trip.
        ----
        %(comment)s
        ----

        To view the discussion for the trip goto %(url)s#trips/%(id)s/discussion
        """ % template_vars

        invites = trip_data['friends']
        send_to = filter(lambda invite: invite['invite_status'] == 'accepted', invites)
        to = [invite['email'] for invite in send_to]

        email_service = self.remoting.service('Email')
        command = email_service.send(to=to,
                subject="New comment on %s trip" % trip_data['name'],
                message=message)
        self.remoting.call(command)

    def comment(self, trip_id, owner, comment):
        '''Add a comment to a trip'''
        trips = self.riak.bucket(self.bucket_name)

        adventurers = self.riak.bucket('adventurers')
        adventurer_obj = adventurers.get(str(owner))
        adventurer = adventurer_obj.get_data()

        comment_id = str(uuid.uuid4())
        comment_data = {
                'comment': comment,
                'date': str(datetime.utcnow().strftime('%B %d, %Y %H:%M:%S GMT+0000')),
                'owner': owner,
                'id': comment_id,
                'first_name': adventurer['first_name'],
                'last_name': adventurer['last_name']
                }

        comment_obj = trips.new(comment_id, comment_data)
        comment_obj.set_usermeta({'object_type': 'comment'})
        comment_obj.store()

        trip = trips.get(str(trip_id))
        trip.add_link(comment_obj, tag='comment')

        trip.store()

        self.__send_comment_notification(trip_id, comment_data, trip.get_data())

        return comment_data

    def get_comments(self, trip_id):
        '''Get all comments on a trip'''
        trips = self.riak.bucket(self.bucket_name)
        trip = trips.get(str(trip_id))

        linked_objects = trip.get_links()
        comment_links = filter(lambda x: x.get_tag() == 'comment', linked_objects)
        def map_comment(comment_link):
            comment = comment_link.get()
            comment_data = comment.get_data()
            return comment_data
        comments = map(map_comment, comment_links)

        return comments
        
