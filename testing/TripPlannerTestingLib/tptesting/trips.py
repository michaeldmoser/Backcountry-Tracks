import uuid
import time
from datetime import datetime
from dateutil import tz

class TripsEnvironment(object):
    def __init__(self, env):
        self.env = env
        self.tripsdb = self.env.riak.get_database('trips')

    def add_trips_to_user(self, user, trips):
        stored_trips = []
        for trip in trips:
            stored_trip = trip.copy()
            stored_trip.update({
                'friends': [
                    {
                        'id': user.email,
                        'email': user.email,
                        'first': user.first_name,
                        'last': user.last_name,
                        'invite_status': 'owner'
                        }
                    ]
                });
            trip_id = self.add(owner = user.email, **stored_trip)
            stored_trip.update({
                'id': trip_id,
                'owner': user.email,
                'friends': [
                    {
                        'id': user.email,
                        'email': user.email,
                        'first': user.first_name,
                        'last': user.last_name,
                        'invite_status': 'owner'
                        }
                    ]
                });
            stored_trips.append(stored_trip)

        return stored_trips

    def add(self, **kwargs):
        """
        Add a new trips to the user's trip list
        """
        trip = {
                'route_description': '',
                'trip_distance': '',
                'elevation_gain': '',
                'difficulty': '',
                }
        assert kwargs['owner'] is not None, "You must provide a owner"
        assert kwargs['name'] is not None, "You must provide a name for the trip"
        assert kwargs['description'] is not None, "You must provide a description for the trip"
        assert kwargs['start'] is not None, "You must provide a start for the trip"
        assert kwargs['end'] is not None, "You must provide a end for the trip"

        trip.update(kwargs)

        trip_id = str(uuid.uuid4())
        trip['id'] = trip_id
        new_trip = self.tripsdb.new(trip_id, data=trip)
        new_trip.set_usermeta({'object_type': 'trip'})
        new_trip.store()

        return trip_id

    def remove_all(self):
        '''
        Remove all trips that exist in the datbase
        '''
        keys = self.tripsdb.get_keys()
        for key in keys:
            trip = self.tripsdb.get(str(key))
            trip.delete()

        for x in range(50):
            keys = self.tripsdb.get_keys()
            if len(keys) == 0:
                return

            time.sleep(.1)

        assert False, "Database did not clear out in the alloted time"

    def get_by_name(self, name):
        '''
        Get a trip by it's name
        '''
        trip = None 

        keys = self.tripsdb.get_keys()
        for key in keys:
            trip_obj = self.tripsdb.get(str(key))
            trip_data = trip_obj.get_data()

            if trip_data['name'] == name:
                trip = trip_data
                trip['id'] = key
                break

        return trip

    def add_invitee(self, trip_id, person, status):
        '''
        Add the person to the trip with id trip_id

        person should be a user object
        '''
        trip = self.tripsdb.get(str(trip_id))

        trip_data = trip.get_data()
        if not trip_data.has_key('friends'):
            trip_data['friends'] = list()

        trip_data['friends'].append({
            'id': person.email,
            'first': person.first_name,
            'last': person.last_name,
            'email': person.email,
            'invite_status': status
            })

        trip.set_data(trip_data)
        trip.store()

    def get(self, trip_id):
        '''Get a trip by it's id'''
        trip_obj = self.tripsdb.get(str(trip_id))
        trip_data = trip_obj.get_data()

        return trip_data

    def add_trip_gear(self, user, trip_id, gear_list):
        '''
        Add gear in gear_list to trip_id for user
        '''
        trip = self.tripsdb.get(str(trip_id))

        trip_data = trip.get_data()
        
        if not trip_data.has_key('gear'):
            trip_data['gear'] = dict()

        trip_data['gear'].update({user.email: gear_list})

        trip.set_data(trip_data)
        trip.store()

    def add_group_gear(self, trip_id, gear_list):
        '''
        Add shared/group gear to trip_id
        '''
        trip = self.tripsdb.get(str(trip_id))

        trip_data = trip.get_data()
        
        if not trip_data.has_key('groupgear'):
            trip_data['groupgear'] = list()

        trip_data['groupgear'].extend(gear_list)

        trip.set_data(trip_data)
        trip.store()

    def add_comment(self, trip_id, owner, comment, date=None):
        '''
        Add a comment to a trip
        '''
        comment_date = date or datetime.now(tz.tzutc())
        trip = self.tripsdb.get(str(trip_id))
        comment_id = str(uuid.uuid4())
        comment_data = {
            'comment': comment,
            'date': str(comment_date.strftime('%B %d, %Y %H:%M:%S GMT%z')),
            'owner': owner,
            'id': comment_id
            }

        comment = self.tripsdb.new(comment_id, comment_data)
        comment.set_usermeta({'object_type': 'comment'})
        comment.store()

        trip.add_link(comment, tag='comment')
        trip.store()

        return comment_data

        

        

