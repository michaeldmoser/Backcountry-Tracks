from tptesting import faketornado, environment, fakepika
from trailhead.mq import PikaClient

def create_fake_application():
    pika_connection_class = fakepika.SelectConnectionFake()
    application = faketornado.WebApplicationFake()
    application()
    application.mq = PikaClient(pika_connection_class, dict())
    application.mq.connect()
    pika_connection_class.ioloop.start()

    return application, pika_connection_class

