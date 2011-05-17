import os
import os.path
import socket
from shutil import copytree

from django.conf import settings
from django.template import Template, Context

def main():
    settings.configure()
    working_directory = os.getcwd()

    template_dir = os.path.join(working_directory, "config/riak.in")
    destination_dir = os.path.join(working_directory, "config/riak")

    app_config_template = os.path.join(template_dir, "app.config")
    app_config = os.path.join(destination_dir, "app.config")

    vm_args_template = os.path.join(template_dir, "vm.args")
    vm_args = os.path.join(destination_dir, "vm.args")

    if not os.path.exists(destination_dir):
        copytree(template_dir, destination_dir)

    app_config_template_file = open(app_config_template, "r+")
    app_config_template = Template(app_config_template_file.read())

    app_config_file = open(app_config, 'w')
    
    fqdn = socket.getfqdn()

    context = Context({
        'hostname': socket.getfqdn(),
    })

    rendered_app_config = app_config_template.render(context)
    app_config_file.write(rendered_app_config)
    app_config_file.close()

    vm_args_template_file = open(vm_args_template, "r+")
    vm_args_template = Template(vm_args_template_file.read())

    vm_args_file = open(vm_args, 'w')
    
    fqdn = socket.getfqdn()

    context = Context({
        'hostname': socket.getfqdn(),
    })

    rendered_vm_args = vm_args_template.render(context)
    vm_args_file.write(rendered_vm_args)
    vm_args_file.close()

if __name__ == '__main__':
    main()

