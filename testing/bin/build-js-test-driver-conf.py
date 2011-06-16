import os
import os.path
import socket
from shutil import copytree

from django.conf import settings
from django.template import Template, Context

def main():
    settings.configure()
    working_directory = os.getcwd()

    js_config_template = "testing/etc/jsTestDriver.conf.in"
    js_config = 'testing/etc/jsTestDriver.conf'

    js_config_template_file = open(js_config_template, "r+")
    js_config_template = Template(js_config_template_file.read())

    js_config_file = open(js_config, 'w')

    fqdn = socket.getfqdn()

    context = Context({
        'working_directory': working_directory,
        'hostname': socket.getfqdn(),
    })

    rendered_js_config = js_config_template.render(context)

    js_config_file.write(rendered_js_config)
    js_config_file.close()

if __name__ == '__main__':
    main()


