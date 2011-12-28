from pkg_resources import load_entry_point
import yaml
import os
import os.path
import subprocess

from django.conf import settings
from django.template import Template, Context

def link_javscript_file(js_file):
    basename = os.path.basename(js_file)
    link_name = '/srv/www/static/js/' + basename
    print js_file, link_name
    try:
        os.remove(link_name)
    except OSError:
        pass

    os.symlink(js_file, link_name)

    return '/static/js/' + basename

def link_stylesheet_file(stylesheet_file):
    basename = os.path.basename(stylesheet_file)
    link_name = '/srv/www/static/css/' + basename
    print stylesheet_file, link_name
    try:
        os.remove(link_name)
    except OSError:
        pass

    os.symlink(stylesheet_file, link_name)

    return basename

def get_webroot_data(webroot):
    javascript_files = []
    templates = []
    stylesheets = []


    for extension in webroot:
        distribution, name = extension.split('/')
        entry = load_entry_point(distribution, 'tripplanner.web.files', name)

        ext = entry()

        if hasattr(ext, 'javascript_files'):
            javascript_files.extend(ext.javascript_files)

        if hasattr(ext, 'templates'):
            templates.append(ext.templates)

        if hasattr(ext, 'stylesheets'):
            stylesheets.extend(ext.stylesheets)

    return javascript_files, templates, stylesheets


def build_webroot():
    src_root = os.path.dirname(__file__) + "/.."
    settings.configure()

    config = yaml.load(open('/etc/tripplanner/tpapp.yaml', 'r').read())    
    webroot = config['webroot']

    javascript_files, templates, stylesheet_files = get_webroot_data(webroot)

    apphome_template_path = src_root + "/htdocs/apphome.html.template"
    template_file = open(apphome_template_path, 'r').read()
    template = Template(template_file)

    javascripts = map(link_javscript_file, javascript_files)
    stylesheets = map(link_stylesheet_file, stylesheet_files)

    context = Context({
        'javascript_files': javascripts,
        'templates': templates,
        'stylesheets': stylesheets
        })

    apphome_content = template.render(context)

    with open('/srv/www/apphome.html', 'w') as apphome:
        apphome.write(apphome_content)

        

        
        
                 

if __name__ == '__main__':
    build_webroot()

