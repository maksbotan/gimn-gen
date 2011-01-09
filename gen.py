#!/usr/bin/env python

import jinja2
import os, imp, json

OUTPUT_DIR = 'generated'

class Generator():
    def __init__(self):
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates', encoding='utf-8'))
        self.templates = [ self.env.get_template(i) for i in os.listdir('templates') if i.endswith('.tmp') ]
        
        self.structure = json.load(open('site_map.json', 'r'), encoding='utf-8')

    def process_node(self, node, level, path):
        prefix = "../" * level
        print '[+] Processing node %s on %s' % (node['name'], prefix)

        if node['subs']:
            self.recreate_dirs(os.path.join(path, node['name']))
        else:
            self.recreate_dirs(path)
      
        template = self.get_template(node['template'])
        with open(os.path.join(OUTPUT_DIR, path, '%s.htm' % node['name']), 'w') as f:
            print '[+][+] Writing file %s' % os.path.join(path, node['name'])

            modules = {}
            for i in node['modules']:
                try:
                    module = imp.load_source(i, 'modules/%s.py' % i)
                except:
                    raise Exception('Unknown module: %s' % i)
    
                modules[i] = getattr(module,i)

            try:
                content = open(os.path.join('content', node['sources']),'r').read().decode('utf-8')
            except IOError:
                content = open(os.path.join('content', 'fish.cont'),'r').read().decode('utf-8')

            f.write(template.render(
                prefix = '../' * level,
                title  = node['title'],
                content = content,
                nodes = self.structure,
                name = node['name'],
                **modules
                ).encode('utf8'))

        for sub in node['subs']:
            self.process_node(sub, level+1, node['name']) 

    def get_template(self, name):
        temps = [ i for i in self.templates if i.name == name]
        if temps:
            return temps[0]
        else:
            raise Exception('Unkonwn template %s' % name)
        
    def recreate_dirs(self, filename):
        path = [ OUTPUT_DIR ] + filename.split(os.path.sep)
        
        for i in range(1,len(path)+1):
            if not os.path.exists(os.path.join(*path[:i])):
                print '[+][+] Creating dir %s' % path[:i]
                os.mkdir(os.path.join(*path[:i]))

    def regen_site(self):
        #DFS-like node processing
        for node in self.structure:
            self.process_node(node, 0, '')

if __name__ == '__main__':
    gen = Generator()
    gen.regen_site()
