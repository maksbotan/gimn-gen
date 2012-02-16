#!/usr/bin/env python

import jinja2
import os, sys, json

OUTPUT_DIR = 'generated'
#Color map for.log function
colors = {'normal': '\033[0m', 'good': '\033[32;1m', 'warn': '\033[33;1m', 'err': '\033[31;1m'}


class Generator():
    def __init__(self):
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates', encoding='utf-8'))
        self.structure = json.load(open('site_map.json', 'r'), encoding='utf-8')

    def process_node(self, node, level, path, title):
        print self.log(level, 'Processing node {0} on {1}'.format(node['name'], level), 'good')

        if node['subs']:
            self.recreate_dirs(*self.cat_list(OUTPUT_DIR, path, node['name']), level=level)
        else:
            self.recreate_dirs(*self.cat_list(OUTPUT_DIR, path), level=level)

        if node['link']:
            #Node is simple link, no need to process
            print self.log(level, 'Processed link to {0}'.format(node['sources']), 'good')
            print
            return

        #Try to load template
        try:
            template = self.env.get_template(node['template'])
        except jinja2.TemplateNotFound:
            print self.log(level,
                'Node {0} not generated due to missing template {1}, also \
refusing to generate its subnodes!'.format(node['name'], node['template']),
                'err')
            print ''
            return
    
        if not os.path.exists(os.path.join('content', node['sources'])):
            print self.log(level, 'Content file {0} for node {1} not found, using \
default one (fish.cont)'.format(node['sources'], node['name']),
                     'warn')
            source = 'fish.cont'
        else:
            source = node['sources']

        with open(os.path.join('content', source)) as f:
            content = f.read().decode('utf-8')

        modules = {}
        for module in node['modules']:
            try:
                modules[module] = json.load(
                    open(os.path.join('modules', '{0}.json'.format(module))))
            except IOError:
                print self.log(level, 'Cannot open file {0}, refusing to \
generate node {1} and all its subnodes!'.format(module, node['name']), 'err')
                print ''
                return
            except ValueError as e:
                print self.log(level, 'JSON cannot parse file {0}, refusing \
to generate node {1} and all its subnodes! Details:\n{2}'.format(module, node['name'], e), 'err')
                print ''
                return

        with open(os.path.join(*self.cat_list(OUTPUT_DIR, path, '{0}.htm'.format(node['name']))), 'w') as f:
            print self.log(level, 'Writing file {0}'.format(os.path.join(*self.cat_list(path, '{0}.htm'.format(node['name'])))), 'good')
            page = template.render(
                                    me = node,
                                    prefix = '../' * level,
                                    content = content,
                                    path = os.path.join(*path),
                                    title = ' :: '.join(self.cat_list(title, node['title'])),
                                    nodes = self.structure,
                                    **modules).encode('utf-8')
            f.write(page)

        print ''

        for sub in node['subs']:
            self.process_node(
                node = sub,
                level = level+1,
                path = self.cat_list(path, node['name']),
                title = self.cat_list(title, node['title'])
            )

    def log(self, level, text, color='normal'):
        """
        Auxillary function for making '[+]' line headers and logging with colors
        """

        return '{0}{1} {2}{3}'.format(colors[color], '[+]' * (level+1), text, colors['normal'])

    def cat_list(self, *args):
        """
        Auxillary funciton to ease doing 'f(*a, b)' calls
        """

        res = []
        for i in args:
            if type(i) == list or type(i) == tuple:
                res += i
            else:
                res.append(i)
        
        return res
        
    def recreate_dirs(self, *args, **kwargs):
        for i in range(1,len(args)+1):
            if not os.path.exists(os.path.join(*args[:i])):
                print self.log(
                    kwargs.get('level', 0),
                    'Creating dir {0}'.format(os.path.join(*args[:i])),
                    'good')
                os.mkdir(os.path.join(*args[:i]))

    def regen_site(self):
        #DFS-like node processing
        for node in self.structure:
            self.process_node(node, 0, [''], [])

if __name__ == '__main__':
    gen = Generator()
    gen.regen_site()
