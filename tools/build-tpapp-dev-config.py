import os
import os.path
import socket
from shutil import copytree

import pwd

from django.conf import settings
from django.template import Template, Context

def main():
    settings.configure()
    working_directory = os.getcwd()

    tpapp_yaml_template = "config/tpapp.yaml.in"
    tpapp_yaml = 'config/tpapp.yaml'

    tpapp_template_file = open(tpapp_yaml_template, "r+")
    tpapp_template = Template(tpapp_template_file.read())

    tpapp_yaml_file = open(tpapp_yaml, 'w')

    fqdn = socket.getfqdn()

    pw_name = pwd.getpwuid(os.getuid()).pw_name

    context = Context({
        'hostname': socket.getfqdn(),
        'user': pw_name,
    })

    rendered_tpapp_yaml = tpapp_template.render(context)

    tpapp_yaml_file.write(rendered_tpapp_yaml)
    tpapp_yaml_file.close()

if __name__ == '__main__':
    main()


