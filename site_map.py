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
    {
      'name': 'vizitka',
      'title': u'Визитка',
      'template': 'main.tmp',
      'modules': [],
      'sources': 'fish.cont',
      'subs': [
                { 'name': 'administration',
                  'title': u'Администрация',
                  'template': 'main.tmp',
                  'modules': [],
                  'sources': 'admin.cont',
                  'subs': []
                },
                { 'name': 'contacts',
                  'title': u'Контактная информация',
                  'template': 'main.tmp',
                  'modules': [],
                  'sources': 'contacts.cont',
                  'subs': []
                },
                { 'name': 'priemnaya',
                  'title': u'Электронная приёмная',
                  'template': 'main.tmp',
                  'modules': [],
                  'sources': 'fish.cont',
                  'subs': []
                }
              ]
    },
    { 'name': 'innovacii',
      'title': u'Инновации',
      'template': 'main.tmp',
      'modules': [],
      'sources': 'fish.cont',
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
