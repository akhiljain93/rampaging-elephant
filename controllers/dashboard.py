#  Controller for all the pages under dashboard

import datetime
import time

# Controllers for index.html, timeline.html, mashup.html, histogram.html, stacked.html, ...
def index(): return dict()

def timeline(): return dict()

def mashup(): return dict()

def histogram(): return dict()

def stacked(): return dict()

# Function fetches the data for all topics in last 7 days with their location of communication to create 3-level hierarichal bar chart
def barchart():
  latest = db(db.ldaywise.id>0).select(db.ldaywise.time.max().with_alias('time'),limitby=(0,1)).first().time 
  lim = latest - 7*24*3600*1000
  data = db((db.ldaywise.time>lim)&(db.ldaywise.locedge==db.locedges.id)).select()
  arr = {'name':'topics-days-locations', 'children':set([])}
  locs = set([])
  for record in data:
    arr['children'].add(record.ldaywise.topic)
    locs.add(record.locedges.loc1)
    locs.add(record.locedges.loc2)
  locs = sorted(list(locs))
  dic3 = {} # inverse dictionary for lev3
  dic2 = {} # inverse dictionary for lev2
  dic1 = {} # inverse dictionary for lev1
  def level3():
    ret = []
    for loc in locs:
      dic3[loc] = len(ret)
      ret.append({'name':loc, 'size': 0})
    return ret
  def level2():
    ret = []
    for i in range(7):
      time = datetime.datetime.fromtimestamp(latest/1000 - i*24*3600).strftime("%b %d")
      dic2[latest - i*24*3600*1000] = len(ret)
      ret.append({'name': time, 'children': level3()})
    return ret
  arr['children'] = list(arr['children'])
  for t in arr['children']:
    dic1[t] = arr['children'].index(t)
  arr['children'] = map(lambda x: {'name': x, 'children': level2()}, arr['children'])
  for record in data:
    a = arr['children'][dic1[record.ldaywise.topic]]['children'][dic2[record.ldaywise.time]]['children']
    a[dic3[record.locedges.loc1]]['size'] += record.ldaywise.volume
    a[dic3[record.locedges.loc2]]['size'] += record.ldaywise.volume
  return dict(data = arr)
