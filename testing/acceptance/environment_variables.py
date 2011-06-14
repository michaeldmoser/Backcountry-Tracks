import socket
from tptesting import environment

environ = environment.create()

SITE_HOME_PAGE = 'http://%s/' % socket.getfqdn()

ALBERT = environ.albert
DOUGLAS = environ.douglas
RAMONA = environ.ramona

SELENIUM_SERVER = environ.selenium_server

APPLICATION_HOME_PAGE = SITE_HOME_PAGE + "app/home"

