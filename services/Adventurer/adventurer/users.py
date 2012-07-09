import uuid
import copy

class Users(object):

    def __init__(self, bucket = None):
        self.bucket = bucket

    def get_by_id(self, user_id):
        '''Will retrieve a user by their id'''
        userobj = self.bucket.get(str(user_id))
        if not userobj.exists():
            raise KeyError("No such user")

        user = userobj.get_data()
        return user

    def get_by_email(self, email):
        '''Will retrieve a user object by the email address'''
        email_ref_obj = self.bucket.get(str(email))
        if not email_ref_obj.exists():
            raise KeyError('No such user')

        email_ref = email_ref_obj.get_data()
        return self.get_by_id(email_ref['key'])


    def __save_the_user(self, user_data, key):
        userobj = self.bucket.get(str(key))
        if userobj.exists():
            olddata = userobj.get_data()
            olddata.update(user_data)
            data_to_store = olddata
        else:
            userobj = self.bucket.new(key, user_data)
            user_data['key'] = key
            data_to_store = user_data

        userobj.set_data(data_to_store)
        userobj.set_usermeta({
            'object_type': 'user_profile'
            })

        userobj.store()
        return data_to_store

    def __save_email_reference(self, key, email):
        email_ref = self.bucket.get(str(email))
        if not email_ref.exists():
            email_ref = self.bucket.new(email, {'key': key})
            email_ref.store()

    def save(self, user_data = {}, user_id = None):
        '''Saves a user object to the database'''
        email = str(user_data.get('email', None))
        if len(email) < 5:
            raise Exception("An email address must be provided.")

        key = user_id if user_id is not None else str(uuid.uuid4())

        user_data = self.__save_the_user(user_data, key)
        self.__save_email_reference(key, email)

        return user_data


        




         

