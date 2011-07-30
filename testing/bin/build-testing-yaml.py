import os
import os.path
import socket
from shutil import copytree

from django.conf import settings
from django.template import Template, Context

def main():
    settings.configure()
    working_directory = os.getcwd()

    tptesting_yaml_template = "testing/etc/tptesting.yaml.in"
    tptesting_yaml = 'testing/etc/tptesting.yaml'

    tptesting_template_file = open(tptesting_yaml_template, "r+")
    tptesting_template = Template(tptesting_template_file.read())

    tptesting_yaml_file = open(tptesting_yaml, 'w')

    fqdn = socket.getfqdn()

    pw_name = pwd.getpwuid(os.getuid()).pw_name

    context = Context({
        'hostname': socket.getfqdn(),
        'user': pw_name,
    })

    rendered_tptesting_yaml = tptesting_template.render(context)

    tptesting_yaml_file.write(rendered_tptesting_yaml)
    tptesting_yaml_file.close()

if __name__ == '__main__':
    main()


