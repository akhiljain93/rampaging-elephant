# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite')
    db.executesql('PRAGMA journal_mode=WAL')
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

db.define_table('nodes',
            Field('uid', 'integer', required = True, unique = True),
            Field('location'),
            Field('clusterid', 'integer'),
            migrate = 'nodes.table')

db.define_table('edges',
            Field('node1', 'integer', required = True, requires = IS_IN_DB(db, 'nodes.uid')),
            Field('node2', 'integer', required = True, requires = IS_IN_DB(db, 'nodes.uid')),
            Field('cledgeid', 'integer', requires = IS_IN_DB(db, 'cledges.id')),
            Field('locedgeid', 'integer', requires = IS_IN_DB(db, 'locedges.id')),
            Field('totalv', 'integer', default = 0),
            migrate = 'edges.table')

db.define_table('cledges',
            Field('cluster1', 'integer', required = True, requires = IS_IN_DB(db, 'nodes.clusterid')),
            Field('cluster2', 'integer', required = True, requires = IS_IN_DB(db, 'nodes.clusterid')),
            Field('totalv', 'integer', default = 0),
            migrate = 'cledges.table')

db.define_table('locedges',
            Field('loc1', required = True, requires = IS_IN_DB(db, 'nodes.location')),
            Field('loc2', required = True, requires = IS_IN_DB(db, 'nodes.location')),
            Field('totalv', 'integer', default = 0),
            migrate = 'locedges.table')

class IS_HOUR(object):
    def __init__(self, error_message="Not an hour!"):
        self.error_message = error_message

    def __call__(self, value):
        error = None
        if value % 3600000 != 1800000:
            error = self.error_message
        return (value, error)

class IS_DAY(object):
    def __init__(self, error_message="Not a day!"):
        self.error_message = error_message

    def __call__(self, value):
        error = None
        if value % 86400000 != 66600000:
            error = self.error_message
        return (value, error)

class IS_WEEK(object):
    def __init__(self, error_message="Not a week!"):
        self.error_message = error_message

    def __call__(self, value):
        error = None
        if value % 604800000 != 325800000:
            error = self.error_message
        return (value, error)

# maintain for 10 days
db.define_table('chourwise',
            Field('topic', required = True),
            Field('time', 'integer', required = True, requires = IS_HOUR()),
            Field('volume', 'integer', default = 1),
            Field('cledge', required = True, requires = IS_IN_DB(db, 'cledges.id')),
            migrate = 'chours.table')
db.define_table('lhourwise',
            Field('topic', required = True),
            Field('time', 'integer', required = True, requires = IS_HOUR()),
            Field('volume', 'integer', default = 1),
            Field('locedge', required = True, requires = IS_IN_DB(db, 'locedges.id')),
            migrate = 'lhours.table')


# maintain for 9 months
db.define_table('cdaywise',
            Field('topic', required = True),
            Field('time', 'integer', required = True, requires = IS_DAY()),
            Field('volume', 'integer', default = 1),
            Field('cledge', required = True, requires = IS_IN_DB(db, 'cledges.id')),
            migrate = 'cdays.table')
db.define_table('ldaywise',
            Field('topic', required = True),
            Field('time', 'integer', required = True, requires = IS_DAY()),
            Field('volume', 'integer', default = 1),
            Field('locedge', required = True, requires = IS_IN_DB(db, 'locedges.id')),
            migrate = 'ldays.table')

#maintain for eternity
db.define_table('cweekwise',
            Field('topic', required = True),
            Field('time', 'integer', required = True, requires = IS_WEEK()),
            Field('volume', 'integer', default = 1),
            Field('cledge', required = True, requires = IS_IN_DB(db, 'cledges.id')),
            migrate = 'cweeks.table')
db.define_table('lweekwise',
            Field('topic', required = True),
            Field('time', 'integer', required = True, requires = IS_WEEK()),
            Field('volume', 'integer', default = 1),
            Field('locedge', required = True, requires = IS_IN_DB(db, 'locedges.id')),
            migrate = 'lweeks.table')

if False:
    db.executesql('CREATE INDEX IF NOT EXISTS nodesidx ON nodes (location,clusterid,uid);')
    db.executesql('CREATE UNIQUE INDEX IF NOT EXISTS edgeuniqidx ON edges (node1,node2);')
    db.executesql('CREATE UNIQUE INDEX IF NOT EXISTS cledgidx ON cledges (cluster1,cluster2);')
    db.executesql('CREATE UNIQUE INDEX IF NOT EXISTS locedgidx ON locedges (loc1,loc2);')
    db.executesql('CREATE UNIQUE INDEX IF NOT EXISTS chouridx ON chourwise (time,topic,cledge);')
    db.executesql('CREATE UNIQUE INDEX IF NOT EXISTS cdayidx ON cdaywise (time,topic,cledge);')
    db.executesql('CREATE UNIQUE INDEX IF NOT EXISTS cweekidx ON cweekwise (time,topic,cledge);')
    db.executesql('CREATE UNIQUE INDEX IF NOT EXISTS lhouridx ON lhourwise (time,topic,locedge);')
    db.executesql('CREATE UNIQUE INDEX IF NOT EXISTS ldayidx ON ldaywise (time,topic,locedge);')
    db.executesql('CREATE UNIQUE INDEX IF NOT EXISTS lweekidx ON lweekwise (time,topic,locedge);')
    db.executesql('analyze')
