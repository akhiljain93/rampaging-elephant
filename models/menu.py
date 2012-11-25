response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%(author)s <%(author_email)s>' % settings
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
(T('Dashboard'),False,URL('default','dashboard'),
  [(T('Overview'),False,URL('default','dashboard')),
  (T('Timeline'),False,URL('dashboard','timeline')),
  (T('Bar Chart'),False,URL('dashboard','barchart')),
  (T('Mash Up'),False,URL('dashboard','mashup')),
  (T('Histogram'),False,URL('dashboard','histogram')),
  (T('Stacked Area'),False,URL('dashboard','stacked')),
  ]
),
(T('Motion Chart'),False,URL('default','motion'),[]),
(T('Database'),False,URL('data','index'),[]),
(T('Nework Graph'),False,URL('default','graph'),[]),
(T('Report'),False,URL('static','report.pdf'),[]),
]
