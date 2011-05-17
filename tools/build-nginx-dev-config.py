import os
import os.path
import socket
from shutil import copytree

from django.conf import settings
from django.template import Template, Context

def main():
    settings.configure()
    working_directory = os.getcwd()

    template_dir = os.path.join(working_directory, "config/nginx.in")
    destination_dir = os.path.join(working_directory, "config/nginx")
    nginx_conf_template = os.path.join(template_dir, "nginx.conf")
    nginx_conf = os.path.join(destination_dir, "nginx.conf")

    if not os.path.exists(destination_dir):
        copytree(template_dir, destination_dir)

    nginx_template_file = open(nginx_conf_template, "r+")
    nginx_template = Template(nginx_template_file.read())

    nginx_conf_file = open(nginx_conf, 'w')
    
    fqdn = socket.getfqdn()

    context = Context({
        'hostname': socket.getfqdn(),
        'username': os.getlogin(),
    })

    rendered_nginx_conf = nginx_template.render(context)

    nginx_conf_file.write(rendered_nginx_conf)
    nginx_conf_file.close()

if __name__ == '__main__':
    main()

