#!/usr/bin/env python

import jinja2
import os

from modules import nav
import site_map

OUTPUT_DIR = 'generated'

class Generator():
    def __init__(self):
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
        self.templates = [ self.env.get_template(i) for i in os.listdir('templates') if i.endswith('.tmp') ]
        
        import site_map
        self.structure = site_map.structure

    def regen_site(self):
        for node in self.structure:
            name = node['name']
            if not node['template'] in [ i.name for i in self.templates ]:
                raise Exception('Unkonwn template %s for node %s' % (node['template'], name))

if __name__ == '__main__':
    gen = Generator()
    gen.regen_site()
