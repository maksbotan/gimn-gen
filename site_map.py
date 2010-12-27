#!/usr/bin/env python
# -*- coding: utf8; -*-

structure = [
    { 'name': 'index',
      'title': u'Главная',
      'template': 'index.tmp',
      'modules': [ 'featured', 'notd'],
      'sources': 'index.cont',
      'subs': []
    },
    { 'name': 'innovacii',
      'title': u'Инновации',
      'template': 'main.tmp',
      'modules': [],
      'sources': 'innovacii.cont',
      'subs': [
                { 'name': 'introdaction',
                  'title': u'«Введение в интеллектуальную жизнь»',
                  'template': 'main.tmp',
                  'modules': [],
                  'sources': 'introdaction.cont',
                  'subs': []
                },
              ]
    }
]
