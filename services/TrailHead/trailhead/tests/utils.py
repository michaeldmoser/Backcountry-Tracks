from tptesting import faketornado, environment, fakepika
from trailhead.mq import PikaClient
from bctmessaging.remoting import RemotingClient

import Cookie

def create_fake_application():
    pika_connection_class = fakepika.SelectConnectionFake()
    application = faketornado.WebApplicationFake()
    application()
    application.mq = PikaClient(pika_connection_class, dict(), RemotingClient)
    application.mq.connect()
    pika_connection_class.ioloop.start()

    return application, pika_connection_class

def make_user_authenticated(handler, user):
    handler.set_secure_cookie('user', user)
    cookie_value = handler._new_cookies[0]
    handler._cookies = Cookie.BaseCookie()
    handler._cookies['user'] = cookie_value['user'].value

def setup_handler(Handler, method, url, user=None, body=None, headers=None):
    '''
    Setup a RequestHandler so as to be able to simulate HTTP Requests on the object.

    @Handler is the RequestHandler sub-class.
    @method is the intend HTTP request method (GET, POST, etc...)
    @url is the URL the request is happening on
    @user is the email address of the user to simulate as authenticated. If no user is supplied then
        the request will be treated as unauthenticated.
    '''
    application, pika = create_fake_application()

    request = faketornado.HTTPRequestFake(method, url, body=body, headers=headers)
    handler = Handler(application, request)
    handler._transforms = []
    if user is not None:
        make_user_authenticated(handler, user)

    return handler, application, pika


